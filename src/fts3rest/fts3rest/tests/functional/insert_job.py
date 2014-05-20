from datetime import datetime, timedelta
import uuid

from fts3.model import Job, File
from fts3rest.lib.base import Session


def insert_job(vo, source, destination, state, duration=None, queued=None, thr=None, reason=None):
    job = Job()
    job.user_dn = '/XX'
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

    file = File()
    file.job_id = job.job_id
    file.vo_name = vo
    file.source_se = source
    file.source_surl = source + '/path'
    file.dest_se = destination
    file.dest_surl = destination + '/path'
    file.file_state = state
    if queued:
        file.start_time = job.submit_time + timedelta(seconds=queued)
    if duration:
        file.tx_duration = duration
    if reason:
        file.reason = reason
    if thr:
        file.throughput = thr

    Session.merge(file)
    Session.commit()
