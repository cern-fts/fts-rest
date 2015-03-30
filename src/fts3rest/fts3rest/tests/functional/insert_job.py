from datetime import datetime, timedelta
import uuid

from fts3.model import Job, File
from fts3rest.lib.base import Session


def insert_job(vo, source=None, destination=None, state='SUBMITTED', **kwargs):
    job = Job()
    job.user_dn = kwargs.get('user_dn', '/DC=ch/DC=cern/CN=Test User')
    job.vo_name = vo
    job.source_se = source
    job.dest_se = destination
    job.job_state = state
    job.submit_time = datetime.utcnow()

    duration = kwargs.get('duration', 0)
    queued = kwargs.get('queued', 0)
    if duration and queued:
        job.finish_time = job.submit_time + timedelta(seconds=duration+queued)
    elif duration:
        job.finish_time = job.submit_time + timedelta(seconds=duration)
    job.job_id = str(uuid.uuid4())

    Session.merge(job)

    multiple = kwargs.get('multiple', [(source, destination)])

    for source_se, dest_se in multiple:
        transfer = File()
        transfer.job_id = job.job_id
        transfer.vo_name = vo
        transfer.source_se = source_se
        transfer.source_surl = source_se + '/path'
        transfer.dest_se = dest_se
        transfer.dest_surl = dest_se + '/path'
        transfer.file_state = state
        if queued:
            transfer.start_time = job.submit_time + timedelta(seconds=queued)
        if duration:
            transfer.tx_duration = duration
        transfer.reason = kwargs.get('reason', None)
        transfer.throughput = kwargs.get('thr', None)
        Session.merge(transfer)
    Session.commit()
    return job.job_id
