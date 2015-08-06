#   Copyright notice:
#   Copyright CERN, 2015.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import random
import socket
import types
import uuid
from datetime import datetime
from sqlalchemy import func
from urlparse import urlparse

from fts3.model import File, BannedSE
from fts3rest.lib.base import Session
from fts3rest.lib.http_exceptions import *


DEFAULT_PARAMS = {
    'bring_online': -1,
    'verify_checksum': False,
    'copy_pin_lifetime': -1,
    'gridftp': '',
    'job_metadata': None,
    'overwrite': False,
    'reuse': False,
    'multihop': False,
    'source_spacetoken': '',
    'spacetoken': '',
    'retry': 0,
    'retry_delay': 0,
    'priority': 3,
    'max_time_in_queue': None
}


def get_storage_element(uri):
    """
    Returns the storage element of the given uri, which is the scheme + hostname without the port

    Args:
        uri: An urlparse instance
    """
    return "%s://%s" % (uri.scheme, uri.hostname)


def _validate_url(url):
    """
    Validates the format and content of the url
    """
    if not url.scheme:
        raise ValueError('Missing scheme (%s)' % url.geturl())
    if url.scheme == 'file':
        raise ValueError('Can not transfer local files (%s)' % url.geturl())
    if not url.path or (url.path == '/' and not url.query):
        raise ValueError('Missing path (%s)' % url.geturl())
    if not url.hostname:
        raise ValueError('Missing host (%s)' % url.geturl())


def _safe_flag(flag):
    """
    Traduces from different representations of flag values to True/False
    True/False => True/False
    1/0 => True/False
    'Y'/'N' => True/False
    """
    if isinstance(flag, types.StringType) or isinstance(flag, types.UnicodeType):
        return len(flag) > 0 and flag[0].upper() == 'Y'
    else:
        return bool(flag)


def _safe_filesize(size):
    if isinstance(size, float):
        return size
    elif size is None:
        return 0.0
    else:
        return float(size)


def _generate_hashed_id():
    """
    Generates a uniformly distributed value between 0 and 2**16
    This is intended to split evenly the load across node
    The name is an unfortunately legacy from when this used to be based on a hash on the job
    """
    return random.randint(0, (2 ** 16) - 1)


def _has_multiple_options(files):
    """
    Returns a tuple (Boolean, Integer)
    Boolean is True if there are multiple replica entries, and Integer holds the number
    of unique files.
    """
    ids = map(lambda f: f['file_index'], files)
    id_count = len(ids)
    unique_id_count = len(set(ids))
    return unique_id_count != id_count, unique_id_count


def _select_best_replica(files, vo_name, entry_state='SUBMITTED'):
    """
    Given a list of files (that must be multiple replicas for the same file) mark as submitted
    the best one
    """
    source_se_list = map(lambda f: f['source_se'], files)
    queue_sizes = Session.query(File.source_se, func.count(File.source_se))\
        .filter(File.vo_name == vo_name)\
        .filter(File.file_state == 'SUBMITTED')\
        .filter(File.dest_se == files[0]['dest_se'])\
        .filter(File.source_se.in_(source_se_list))\
        .group_by(File.source_se)

    best_ses = map(lambda elem: elem[0], sorted(queue_sizes, key=lambda elem: elem[1]))
    best_index = 0
    for index, transfer in enumerate(files):
        # If not in the result set, the queue is empty, so finish here
        if transfer['source_se'] not in best_ses:
            best_index = index
            break
        # So far this looks good, but keep looking, in case some other has nothing at all
        if transfer['source_se'] == best_ses[0]:
            best_index = index
    files[best_index]['file_state'] = entry_state


def _apply_banning(files):
    """
    Query the banning information for all pairs, reject the job
    as soon as one SE can not submit.
    Update wait_timeout and wait_timestamp is there is a hit
    """
    # Usually, banned SES will be in the order of ~100 max
    # Files may be several thousands
    # We get all banned in memory so we avoid querying too many times the DB
    # We then build a dictionary to make look up easy
    banned_ses = dict()
    for b in Session.query(BannedSE):
        banned_ses[str(b.se)] = (b.vo, b.status, b.wait_timeout)

    now = datetime.utcnow()
    for f in files:
        source_banned = banned_ses.get(str(f['source_se']), None)
        dest_banned = banned_ses.get(str(f['dest_se']), None)
        timeout = None

        if source_banned and (source_banned[0] == f['vo_name'] or source_banned[0] is None):
            if source_banned[1] != 'WAIT_AS':
                raise HTTPForbidden("%s is banned" % f['source_se'])
            timeout = source_banned[2]

        if dest_banned and (dest_banned[0] == f['vo_name'] or dest_banned[0] is None):
            if dest_banned[1] != 'WAIT_AS':
                raise HTTPForbidden("%s is banned" % f['dest_se'])
            if not timeout:
                timeout = dest_banned[2]
            else:
                timeout = max(timeout, dest_banned[2])

        if timeout is not None:
            f['wait_timestamp'] = now
            f['wait_timeout'] = timeout


class JobBuilder(object):
    """
    From a dictionary, build the internal representation of Job, Files and
    Data Management
    """

    def _get_params(self, submitted_params):
        """
        Returns proper parameters applying defaults and user values
        """
        params = dict()
        params.update(DEFAULT_PARAMS)
        params.update(submitted_params)
        # Some parameters may be explicitly None to pick the default, so re-apply defaults
        for k, v in params.iteritems():
            if v is None and k in DEFAULT_PARAMS:
                params[k] = DEFAULT_PARAMS[k]
        return params

    def _build_internal_job_params(self):
        """
        Generates the value for job.internal_job_params depending on the
        received protocol parameters
        """
        param_list = list()
        if self.params.get('nostreams', None):
            param_list.append("nostreams:%d" % int(self.params['nostreams']))
        if self.params.get('timeout', None):
            param_list.append("timeout:%d" % int(self.params['timeout']))
        if self.params.get('buffer_size', None):
            param_list.append("buffersize:%d" % int(self.params['buffer_size']))
        if self.params.get('strict_copy', False):
            param_list.append("strict")
        if self.params.get('ipv4', False):
            param_list.append('ipv4')
        elif self.params.get('ipv6', False):
            param_list.append('ipv6')

        if len(param_list) == 0:
            return None
        else:
            return ','.join(param_list)

    def _set_job_source_and_destination(self, entries):
        """
        Iterates through the files that belong to the job, and determines the
        'overall' job source and destination Storage Elements
        """
        # Multihop
        if self.job['reuse_job'] == 'H':
            self.job['source_se'] = entries[0]['source_se']
            self.job['dest_se'] = entries[-1]['dest_se']
        # Regular transfers
        else:
            self.job['source_se'] = entries[0]['source_se']
            self.job['dest_se'] = entries[0]['dest_se']
            for elem in entries:
                if elem['source_se'] != self.job['source_se']:
                    self.job['source_se'] = None
                if elem['dest_se'] != self.job['dest_se']:
                    self.job['dest_se'] = None

    def _populate_files(self, file_dict, f_index, shared_hashed_id):
        """
        From the dictionary file_dict, generate a list of transfers for a job
        """
        # Extract matching pairs
        pairs = []
        for source in file_dict['sources']:
            source_url = urlparse(source.strip())
            _validate_url(source_url)
            for destination in file_dict['destinations']:
                dest_url = urlparse(destination.strip())
                _validate_url(dest_url)
                pairs.append((source_url, dest_url))

        # Create one File entry per matching pair
        if self.is_bringonline:
            initial_file_state = 'STAGING'
        else:
            initial_file_state = 'SUBMITTED'

        # Multiple replica job?
        if len(file_dict['sources']) > 1:
            if self.is_bringonline:
                raise HTTPBadRequest('Staging with multiple replicas is not allowed')
            # On multiple replica job, we mark all files initially with NOT_USED
            initial_file_state = 'NOT_USED'
            # Multiple replicas, all must share the hashed-id
            if shared_hashed_id is None:
                shared_hashed_id = _generate_hashed_id()

        for source, destination in pairs:
            if source.scheme not in ('srm', 'mock') and self.is_bringonline:
                raise HTTPBadRequest('Staging operations can only be used with the SRM protocol')

            f = dict(
                job_id=self.job_id,
                file_index=f_index,
                file_state=initial_file_state,
                source_surl=source.geturl(),
                dest_surl=destination.geturl(),
                source_se=get_storage_element(source),
                dest_se=get_storage_element(destination),
                vo_name=None,
                user_filesize=_safe_filesize(file_dict.get('filesize', 0)),
                selection_strategy=file_dict.get('selection_strategy', 'auto'),
                checksum=file_dict.get('checksum', None),
                file_metadata=file_dict.get('metadata', None),
                activity=file_dict.get('activity', 'default'),
                hashed_id=shared_hashed_id if shared_hashed_id else _generate_hashed_id()
            )
            self.files.append(f)

    def _apply_selection_strategy(self):
        """
        On multiple-replica jobs, select the adecuate file to go active
        """
        if self.files[0].get('selection_strategy', 'auto') == 'auto':
            _select_best_replica(self.files, self.user.vos[0])
        else:
            self.files[0]['file_state'] = 'STAGING' if self.is_bringonline else 'SUBMITTED'

    def _populate_transfers(self, files_list):
        """
        Initializes the list of transfers
        """
        reuse_flag = 'N'
        if self.params['multihop']:
            reuse_flag = 'H'
        elif _safe_flag(self.params['reuse']):
            reuse_flag = 'Y'

        self.is_bringonline = self.params['copy_pin_lifetime'] > 0 or self.params['bring_online'] > 0

        job_initial_state = 'STAGING' if self.is_bringonline else 'SUBMITTED'

        self.job = dict(
            job_id=self.job_id,
            job_state=job_initial_state,
            reuse_job=reuse_flag,
            retry=int(self.params['retry']),
            retry_delay=int(self.params['retry_delay']),
            job_params=self.params['gridftp'],
            submit_host=socket.getfqdn(),
            agent_dn='rest',
            user_dn=None,
            voms_cred=None,
            vo_name=None,
            cred_id=None,
            submit_time=datetime.utcnow(),
            priority=max(min(int(self.params['priority']), 5), 1),
            space_token=self.params['spacetoken'],
            overwrite_flag=_safe_flag(self.params['overwrite']),
            source_space_token=self.params['source_spacetoken'],
            copy_pin_lifetime=int(self.params['copy_pin_lifetime']),
            checksum_method=self.params['verify_checksum'],
            bring_online=self.params['bring_online'],
            job_metadata=self.params['job_metadata'],
            internal_job_params=self._build_internal_job_params(),
            max_time_in_queue=self.params['max_time_in_queue']
        )

        if 'credential' in self.params:
            self.job['user_cred'] = self.params['credential']
        elif 'credentials' in self.params:
            self.job['user_cred'] = self.params['credentials']

        # If reuse is enabled, or it is a bring online job, generate one single "hash" for all files
        if reuse_flag in ('H', 'Y') or self.is_bringonline:
            shared_hashed_id = _generate_hashed_id()
        else:
            shared_hashed_id = None

        # Files
        f_index = 0
        for file_dict in files_list:
            self._populate_files(file_dict, f_index, shared_hashed_id)
            f_index += 1

        if len(self.files) == 0:
            raise HTTPBadRequest('No valid pairs available')

        # If a checksum is provided, but no checksum is available, 'relaxed' comparison
        # (Not nice, but need to keep functionality!)
        has_checksum = False
        for file_dict in self.files:
            if file_dict['checksum'] is not None:
                has_checksum = len(file_dict['checksum']) > 0
                break
        if not self.job['checksum_method'] and has_checksum:
            self.job['checksum_method'] = 'r'

        # Validate that if this is a multiple replica job, that there is one single unique file
        self.is_multiple, unique_files = _has_multiple_options(self.files)
        if self.is_multiple:
            # Multiple replicas can not use the reuse flag, nor multihop
            if reuse_flag in ('H', 'Y'):
                raise HTTPBadRequest('Can not specify reuse and multiple replicas at the same time')
            # Only one unique file per multiple-replica job
            if unique_files > 1:
                raise HTTPBadRequest('Multiple replicas jobs can only have one unique file')
            self.job['reuse_job'] = 'R'
            # Apply selection strategy
            self._apply_selection_strategy()

        self._set_job_source_and_destination(self.files)

    def _populate_deletion(self, deletion_dict):
        """
        Initializes the list of deletions
        """
        self.job = dict(
            job_id=self.job_id,
            job_state='DELETE',
            reuse_job=None,
            retry=int(self.params['retry']),
            retry_delay=int(self.params['retry_delay']),
            job_params=self.params['gridftp'],
            submit_host=socket.getfqdn(),
            agent_dn='rest',
            user_dn=None,
            voms_cred=None,
            vo_name=None,
            cred_id=None,
            submit_time=datetime.utcnow(),
            priority=3,
            space_token=self.params['spacetoken'],
            overwrite_flag='N',
            source_space_token=self.params['source_spacetoken'],
            copy_pin_lifetime=-1,
            checksum_method=None,
            bring_online=None,
            job_metadata=self.params['job_metadata'],
            internal_job_params=None,
            max_time_in_queue=self.params['max_time_in_queue']
        )

        if 'credential' in self.params:
            self.job['user_cred'] = self.params['credential']
        elif 'credentials' in self.params:
            self.job['user_cred'] = self.params['credentials']

        shared_hashed_id = _generate_hashed_id()

        # Avoid surl duplication
        unique_surls = []

        for dm in deletion_dict:
            if isinstance(dm, dict):
                entry = dm
            elif isinstance(dm, str) or isinstance(dm, unicode):
                entry = dict(surl=dm)
            else:
                raise ValueError("Invalid type for the deletion item (%s)" % type(dm))

            surl = urlparse(entry['surl'])
            _validate_url(surl)

            if surl not in unique_surls:
                self.datamanagement.append(dict(
                    job_id=self.job_id,
                    vo_name=None,
                    file_state='DELETE',
                    source_surl=entry['surl'],
                    source_se=get_storage_element(surl),
                    dest_surl=None,
                    dest_se=None,
                    hashed_id=shared_hashed_id,
                    file_metadata=entry.get('metadata', None)
                ))
                unique_surls.append(surl)

        self._set_job_source_and_destination(self.datamanagement)

    def _set_user(self):
        """
        Set the user that triggered the action
        """
        self.job['user_dn'] = self.user.user_dn
        self.job['cred_id'] = self.user.delegation_id
        self.job['voms_cred'] = ' '.join(self.user.voms_cred)
        self.job['vo_name'] = self.user.vos[0]
        for file in self.files:
            file['vo_name'] = self.user.vos[0]
        for dm in self.datamanagement:
            dm['vo_name'] = self.user.vos[0]

    def __init__(self, user, **kwargs):
        """
        Constructor
        """
        try:
            self.user = user
            # Get the job parameters
            self.params = self._get_params(kwargs.pop('params', dict()))

            files_list = kwargs.pop('files', None)
            datamg_list = kwargs.pop('delete', None)

            if files_list is not None and datamg_list is not None:
                raise HTTPBadRequest('Simultaneous transfer and namespace operations not supported')
            if files_list is None and datamg_list is None:
                raise HTTPBadRequest('No transfers or namespace operations specified')

            self.job_id = str(uuid.uuid1())
            self.files = list()
            self.datamanagement = list()

            if files_list is not None:
                self._populate_transfers(files_list)
            elif datamg_list is not None:
                self._populate_deletion(datamg_list)

            self._set_user()

            # Reject for SE banning
            # If any SE does not accept submissions, reject the whole job
            # Update wait_timeout and wait_timestamp if WAIT_AS is set
            if self.files:
                _apply_banning(self.files)
            if self.datamanagement:
                _apply_banning(self.datamanagement)

        except ValueError, e:
            raise HTTPBadRequest('Invalid value within the request: %s' % str(e))
        except TypeError, e:
            raise HTTPBadRequest('Malformed request: %s' % str(e))
        except KeyError, e:
            raise HTTPBadRequest('Missing parameter: %s' % str(e))

