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

from datetime import timedelta
from fts3.rest.client import Submitter
from delegate import delegate
from fts3.rest.client import ClientError

def cancel(context, job_id, file_ids=None):
    """
    Cancels a job

    Args:
        context: fts3.rest.client.context.Context instance
        job_id:  The job to cancel

    Returns:
        The terminal state in which the job has been left.
        Note that it may not be CANCELED if the job finished already!
    """
    submitter = Submitter(context)
    return submitter.cancel(job_id, file_ids)


def cancel_all(context, vo_name=None):
    """
    Cancel all jobs within a given VO or FTS3 (needs enough privileges)

    Args:
        context: fts3.rest.client.context.Context instance
        vo_name: The VO name, or None to cancell all jobs

    Returns:
        None
    """
    submitter = Submitter(context)
    return submitter.cancel_all(vo_name)


def new_transfer(source, destination, checksum=None, filesize=None, metadata=None, activity=None):
    """
    Creates a new transfer pair

    Args:
        source:      Source SURL
        destination: Destination SURL
        checksum:    Checksum
        filesize:    File size
        metadata:    Metadata to bind to the transfer

    Returns:
        An initialized transfer
    """
    transfer = dict(
        sources=[source],
        destinations=[destination],
    )
    if checksum:
        transfer['checksum'] = checksum
    if filesize:
        transfer['filesize'] = filesize
    if metadata:
        transfer['metadata'] = metadata
    if activity:
        transfer['activity'] = activity
    return transfer


def add_alternative_source(transfer, alt_source):
    """
    Adds an alternative source to a transfer

    Args:
        transfer:   A dictionary created with new_transfer
        alt_source: Alternative source

    Returns:
        For convenience, transfer
    """
    transfer['sources'].push_back(alt_source)
    return transfer


def new_job(transfers=None, deletion=None, verify_checksum=True, reuse=False, overwrite=False, multihop=False,
            source_spacetoken=None, spacetoken=None,
            bring_online=None, copy_pin_lifetime=None,
            retry=-1, retry_delay=0, metadata=None, priority=None, strict_copy=False):
    """
    Creates a new dictionary representing a job

    Args:
        transfers:         Initial list of transfers
        deletion:          Delete files
        verify_checksum:   Enable checksum verification
        reuse:             Enable reuse (all transfers are handled by the same process)
        overwrite:         Overwrite the destinations if exist
        multihop:          Treat the transfer as a multihop transfer
        source_spacetoken: Source space token
        spacetoken:        Destination space token
        bring_online:      Bring online timeout
        copy_pin_lifetime: Pin lifetime
        retry:             Number of retries: <0 is no retries, 0 is server default, >0 is whatever value is passed
        metadata:          Metadata to bind to the job
        priority:          Job priority

    Returns:
        An initialized dictionary representing a job
    """
    if transfers is None and deletion is None:
        raise ClientError('Bad request: No transfers or deletion jobs are provided')
    if transfers is None:
        transfers = []
    params = dict(
        verify_checksum=verify_checksum,
        reuse=reuse,
        spacetoken=spacetoken,
        bring_online=bring_online,
        copy_pin_lifetime=copy_pin_lifetime,
        job_metadata=metadata,
        source_spacetoken=source_spacetoken,
        overwrite=overwrite,
        multihop=multihop,
        retry=retry,
        retry_delay=retry_delay,
        priority=priority,
        strict_copy=strict_copy
    )
    job = dict(
        files=transfers,
        delete=deletion,
        params=params
    )
    return job

def new_staging_job(files, bring_online=None, copy_pin_lifetime=None, source_spacetoken=None, spacetoken=None, metadata=None, priority=None):
    """
        Creates a new dictionary representing a staging job
        
    Args:
        files:  Array of surls to stage.
        bring_online:      Bring online timeout
        copy_pin_lifetime: Pin lifetime
        source_spacetoken: Source space token
        spacetoken: Deletion spacetoken
        metadata:   Metadata to bind to the job
        priority:          Job priority
        
    Returns:
        An initialized dictionary representing a staging job
    """
    if bring_online <= 0 and copy_pin_lifetime <= 0:
        raise ClientError('Bad request: bring_online and copy_pin_lifetime are not positive numbers')
        
    transfers = []
    for i in range (0, len(files)-1):
        transfers.append(new_transfer(source=files[i], destination=files[i]))
        	 
    params = dict(
        source_spacetoken=source_spacetoken,
        spacetoken=spacetoken,
        bring_online=bring_online,
        copy_pin_lifetime=copy_pin_lifetime,
        job_metadata=metadata,

    )
    job = dict(
       files=transfers,
       params=params
    )
    return job

def new_delete_job(files, spacetoken=None, metadata=None):
    """
    Creates a new dictionary representing a deletion job

    Args:
        files:      Array of surls to delete. Each item can be either a string or a dictionary with keys surl and metadata
        spacetoken: Deletion spacetoken
        metadata:   Metadata to bind to the job

    Return
        An initialized dictionary representing a deletion job
    """
    params = dict(
        source_spacetoken=spacetoken,
        job_metadata=metadata
    )
    job = dict(
        delete=files,
        params=params
    )
    return job


def submit(context, job, delegation_lifetime=timedelta(hours=7), force_delegation=False):
    """
    Submits a job

    Args:
        context: fts3.rest.client.context.Context instance
        job:     Dictionary representing the job
        delegation_lifetime: Delegation lifetime
        force_delegation:    Force delegation even if there is a valid proxy

    Returns:
        The job id
    """
    delegate(context, delegation_lifetime, force_delegation)
    submitter = Submitter(context)
    params = job.get('params', {})
    return submitter.submit(transfers=job.get('files', None), delete=job.get('delete', None), staging=job.get('staging', None), **params)
