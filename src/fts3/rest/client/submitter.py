import json


class Submitter(object):

    def __init__(self, context):
        self.context = context

    @staticmethod
    def build_submission(transfers, **kwargs):
        job = dict()

        job['files'] = transfers
        job['params'] = dict()
        job['params'].update(kwargs)
        if 'checksum' in kwargs:
            for f in job['files']:
                if 'checksum' not in f:
                    f['checksum'] = kwargs['checksum']
            del job['params']['checksum']
        if 'filesize' in kwargs:
            for f in job['files']:
                f['filesize'] = kwargs['filesize']
            del job['params']['filesize']
        if 'file_metadata' in kwargs:
            for f in job['files']:
                f['metadata'] = kwargs['file_metadata']
            del job['params']['file_metadata']

        return json.dumps(job, indent=2)

    def submit(self, transfers, **kwargs):
        job = Submitter.build_submission(transfers, **kwargs)
        r = json.loads(self.context.post_json('/jobs', job))
        return r['job_id']

    def cancel(self, job_id):
        return json.loads(self.context.delete('/jobs/%s' % job_id))
