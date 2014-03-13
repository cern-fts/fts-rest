import json


class Submitter(object):

    def __init__(self, context):
        self.context = context

    @staticmethod
    def _build_submission(transfers, **kwargs):
        job = dict()

        job['files'] = transfers
        job['params'] = dict()
        job['params'].update(kwargs)
        if 'checksum' in kwargs:
            del job['params']['checksum']
        if 'filesize' in kwargs:
            del job['params']['filesize']
        if 'file_metadata' in kwargs:
            del job['params']['file_metadata']

        print job

        return json.dumps(job, indent=2)

    def submit(self, transfers, **kwargs):
        job = Submitter._build_submission(transfers, **kwargs)
        r = json.loads(self.context.post_json('/jobs', job))
        return r['job_id']

    def cancel(self, job_id):
        return json.loads(self.context.delete('/jobs/%s' % job_id))
