from datetime import datetime, timedelta
import uuid

from fts3.model import Job, File
from fts3rest.lib.base import Session


def insert_job(vo, source=None, destination=None, state='SUBMITTED', multiple=None,
               duration=None, queued=None, thr=None, reason=None,
               user_dn='/DC=ch/DC=cern/CN=Test User'):
    assert(multiple is not None or (destination is not None and source is not None))

    job = Job()
    job.user_dn = user_dn
    job.vo_name = vo
    job.source_se = source
    job.job_state = state
    job.submit_time = datetime.utcnow()
    if duration and queued:
        job.finish_time = job.submit_time + timedelta(seconds=duration+queued)
    elif duration:
        job.finish_time = job.submit_time + timedelta(seconds=duration)
    job.job_id = str(uuid.uuid4())

    Session.merge(job)

    if multiple is None:
        multiple = [(source, destination)]

    for (s, d) in multiple:
        transfer = File()
        transfer.job_id = job.job_id
        transfer.vo_name = vo
        transfer.source_se = s
        transfer.source_surl = s + '/path'
        transfer.dest_se = d
        transfer.dest_surl = d + '/path'
        transfer.file_state = state
        if queued:
            transfer.start_time = job.submit_time + timedelta(seconds=queued)
        if duration:
            transfer.tx_duration = duration
        if reason:
            transfer.reason = reason
        if thr:
            transfer.throughput = thr
        Session.merge(transfer)
    Session.commit()
    return job.job_id
