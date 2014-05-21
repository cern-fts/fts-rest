#   Copyright notice:
#   Copyright CERN, 2014.
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

import json
import logging
from datetime import datetime
from pylons import request
from sqlalchemy import distinct, func

from fts3.model import BannedDN, BannedSE, Job, File, JobActiveStates, FileActiveStates
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.http_exceptions import *
from fts3rest.lib.middleware.fts3auth import authorize
from fts3rest.lib.middleware.fts3auth.constants import *

log = logging.getLogger(__name__)


def _ban_se(storage, vo_name, allow_submit, status, timeout):
    """
    Mark in the db the given storage as banned
    """
    user = request.environ['fts3.User.Credentials']
    banned = BannedSE()
    banned.se = storage
    banned.addition_time = datetime.utcnow()
    banned.admin_dn = user.user_dn
    banned.vo = vo_name
    if allow_submit and status == 'WAIT':
        banned.status = 'WAIT_AS'
    else:
        banned.status = status
    banned.wait_timeout = timeout
    Session.merge(banned)
    Session.commit()


def _ban_dn(dn):
    """
    Mark in the db the given DN as banned
    """
    user = request.environ['fts3.User.Credentials']
    banned = BannedDN()
    banned.dn = dn
    banned.addition_time = datetime.utcnow()
    banned.admin_dn = user.user_dn
    Session.merge(banned)
    Session.commit()


def _cancel_transfers(storage=None, vo_name=None):
    """
    Cancels the transfers that have the given storage either in source or destination,
    and belong to the given VO.
    Returns the list of affected jobs ids.
    """
    affected_job_ids = set()
    files = Session.query(File)\
        .filter((File.source_se == storage) | (File.dest_se == storage))\
        .filter(File.file_state.in_(FileActiveStates + ['NOT_USED']))
    if vo_name:
        files = files.filter(File.vo_name == vo_name)

    now = datetime.utcnow()

    try:
        for file in files:
            affected_job_ids.add(file.job_id)
            # Cancel the affected file
            file.file_state = 'CANCELED'
            file.reason = 'Storage banned'
            file.finish_time = now
            Session.merge(file)
            # If there are alternatives, enable them
            Session.query(File).filter(File.job_id == file.job_id)\
                .filter(File.file_index == file.file_index)\
                .filter(File.file_state == 'NOT_USED').update({'file_state': 'SUBMITTED'})

        # Or next queries will not see the changes!
        Session.commit()
    except Exception:
        Session.rollback()
        raise

    # Set each job terminal state if needed
    try:
        for job_id in affected_job_ids:
            reuse_flag = Session.query(Job.reuse_job).get(job_id)[0]
            n_files = Session.query(func.count(distinct(File.file_id))).filter(File.job_id == job_id).all()[0][0]
            n_canceled = Session.query(func.count(distinct(File.file_id)))\
                .filter(File.job_id == job_id).filter(File.file_state == 'CANCELED').all()[0][0]
            n_finished = Session.query(func.count(distinct(File.file_id)))\
                .filter(File.job_id == job_id).filter(File.file_state == 'FINISHED').all()[0][0]
            n_failed = Session.query(func.count(distinct(File.file_id)))\
                .filter(File.job_id == job_id).filter(File.file_state == 'FAILED').all()[0][0]

            n_terminal = n_canceled + n_finished + n_failed

            # Job finished!
            if n_terminal == n_files:
                reason = None
                Session.query(Job).filter(Job.job_id == job_id).update({
                    'job_state': 'CANCELED',
                    'job_finished': now,
                    'finish_time': now,
                    'reason': reason
                })
                Session.query(File).filter(File.job_id == job_id).update({
                    'job_finished': now
                })

        Session.commit()
    except Exception:
        Session.rollback()
        raise
    return affected_job_ids


def _cancel_jobs(dn):
    """
    Cancel all jobs that belong to dn.
    Returns the list of affected jobs ids.
    """
    jobs = Session.query(Job.job_id).filter(Job.job_state.in_(JobActiveStates)).filter(Job.user_dn == dn)
    job_ids = map(lambda j: j[0], jobs)

    try:
        now = datetime.utcnow()
        for job_id in job_ids:
            Session.query(File).filter(File.job_id == job_id).filter(File.file_state.in_(FileActiveStates))\
                .update({
                    'file_state': 'CANCELED', 'reason': 'User banned',
                    'job_finished': now, 'finish_time': now
                })
            Session.query(Job).filter(Job.job_id == job_id)\
                .update({
                    'job_state': 'CANCELED', 'reason': 'User banned',
                    'job_finished': now, 'finish_time': now
                })

        Session.commit()
        return job_ids
    except Exception:
        Session.rollback()
        raise


def _set_to_wait(storage=None, vo_name=None, timeout=0):
    """
    Updates the transfers that have the given storage either in source or destination,
    and belong to the given VO.
    Returns the list of affected jobs ids.
    """
    job_ids = Session.query(distinct(File.job_id))\
        .filter((File.source_se == storage) | (File.dest_se == storage)).filter(File.file_state.in_(FileActiveStates))
    if vo_name:
        job_ids = job_ids.filter(File.vo_name == vo_name)
    job_ids = map(lambda j: j[0], job_ids.all())

    try:
        for job_id in job_ids:
            Session.query(File).filter(File.job_id == job_id).filter(File.file_state.in_(FileActiveStates))\
                .update({'wait_timestamp': datetime.utcnow(), 'wait_timeout': timeout})

        Session.commit()
        return job_ids
    except Exception:
        Session.rollback()
        raise


class BanningController(BaseController):
    """
    Banning API
    """

    @authorize(CONFIG)
    @doc.query_arg('storage', 'Storage to ban', required=True)
    @doc.query_arg('vo_name', 'Limit the banning to a given VO', required=False)
    @doc.query_arg('allow_submit', 'If true, transfers will not run, but submissions will be accepted', required=False)
    @doc.query_arg(
        'status',
        'What to do with the queued jobs: cancel (default, cancel immediately) or wait(wait for some time)',
        required=False
    )
    @doc.query_arg(
        'timeout',
        'If status==wait, timeout for the queued jobs. 0 = will not timeout (default)',
        required=False
    )
    @doc.response(400, 'storage is missing, or any of the others have an invalid value')
    @doc.response(413, 'The user is not allowed to change the configuration')
    @doc.return_type(array_of=str)
    @jsonify
    def ban_se(self):
        """
        Ban a storage element. Returns affected jobs ids.
        """
        if request.content_type == 'application/json':
            try:
                input_dict = json.loads(request.body)
            except Exception:
                raise HTTPBadRequest('Malformed input')
        else:
            input_dict = request.params

        storage = input_dict.get('storage', None)
        if not storage:
            raise HTTPBadRequest('Missing storage parameter')

        vo_name = input_dict.get('vo_name', None)
        allow_submit = bool(input_dict.get('allow_submit', False))
        status = input_dict.get('status', 'cancel').upper()

        if status not in ['CANCEL', 'WAIT']:
            raise HTTPBadRequest('status can only be cancel or wait')

        if allow_submit and status == 'CANCEL':
            raise HTTPBadRequest('allow_submit and status = CANCEL can not be combined')

        try:
            timeout = int(input_dict.get('timeout', 0))
            if timeout < 0:
                raise ValueError()
        except ValueError:
            raise HTTPBadRequest('timeout expects an integer equal or greater than zero')

        _ban_se(storage, vo_name, allow_submit, status, timeout)

        if status == 'CANCEL':
            affected = _cancel_transfers(storage=storage, vo_name=vo_name)
        else:
            affected = _set_to_wait(storage=storage, vo_name=vo_name, timeout=timeout)

        log.warn("Storage %s banned (%s), %d jobs affected" % (storage, status, len(affected)))
        return affected

    @authorize(CONFIG)
    @doc.query_arg('user_dn', 'User DN to ban', required=True)
    @doc.response(400, 'dn is missing')
    @doc.response(409, 'The user tried to ban (her|his)self')
    @doc.response(413, 'The user is not allowed to change the configuration')
    @jsonify
    def ban_dn(self):
        """
        Ban a user
        """
        if request.content_type == 'application/json':
            try:
                input_dict = json.loads(request.body)
            except Exception:
                raise HTTPBadRequest('Malformed input')
        else:
            input_dict = request.params

        user = request.environ['fts3.User.Credentials']
        dn = input_dict.get('user_dn', None)

        if not dn:
            raise HTTPBadRequest('Missing dn parameter')
        if dn == user.user_dn:
            raise HTTPConflict('The user tried to ban (her|his)self')

        _ban_dn(dn)
        affected = _cancel_jobs(dn=dn)

        log.warn("User %s banned, %d jobs affected" % (dn, len(affected)))

        return affected

    @doc.query_arg('storage', 'The storage to unban', required=True)
    @doc.response(204, 'Success')
    @doc.response(400, 'storage is empty or missing')
    @doc.response(403, 'The user is not allowed to perform configuration actions')
    @authorize(CONFIG)
    def unban_se(self, start_response):
        """
        Unban a storage element
        """
        storage = request.params.get('storage', None)
        if not storage:
            raise HTTPBadRequest('Missing storage parameter')

        banned = Session.query(BannedSE).get(storage)
        if banned:
            Session.delete(banned)
            Session.commit()
            log.warn("Storage %s unbanned" % storage)
        else:
            log.warn("Unban of storage %s without effect" % storage)

        start_response('204 No Content', [])
        return ['']

    @doc.query_arg('user_dn', 'User DN to unban', required=True)
    @doc.response(204, 'Success')
    @doc.response(400, 'user_dn is empty or missing')
    @doc.response(403, 'The user is not allowed to perform configuration actions')
    @authorize(CONFIG)
    def unban_dn(self, start_response):
        """
        Unban a user
        """
        dn = request.params.get('user_dn', None)
        if not dn:
            raise HTTPBadRequest('Missing user_dn parameter')

        banned = Session.query(BannedDN).get(dn)
        if banned:
            Session.delete(banned)
            Session.commit()
            log.warn("User %s unbanned" % dn)
        else:
            log.warn("Unban of user %s without effect" % dn)

        start_response('204 No Content', [])
        return ['']


__all__ = ['BanningController']
