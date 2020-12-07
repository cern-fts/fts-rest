#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
#
#   See www.eu-emi.eu for details on the copyright holders
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

try:
    import simplejson as json
except:
    import json


class Submitter(object):

    def __init__(self, context):
        self.context = context

    @staticmethod
    def build_submission(transfers=None, delete=None, staging=None, params=None, **kwargs):
        job = dict()
        job['params'] = dict()
        if params:
            job['params'].update(params)
        job['params'].update(kwargs)

        if delete:
            job['delete'] = delete
        if staging:
            job['staging'] = staging
        if transfers:
            job['files'] = transfers
            if 'checksum' in job['params']:
                for f in job['files']:
                    if 'checksum' not in f:
                        f['checksum'] = job['params']['checksum']
                del job['params']['checksum']
            if 'filesize' in job['params']:
                for f in job['files']:
                    f['filesize'] = job['params']['filesize']
                del job['params']['filesize']
            if 'file_metadata' in job['params']:
                for f in job['files']:
                    f['metadata'] = job['params']['file_metadata']
                del job['params']['file_metadata']

        return json.dumps(job, indent=2)

    def submit(self, transfers=None, delete=None, params=None, **kwargs):
        job = Submitter.build_submission(transfers=transfers,
                                         delete=delete,
                                         params=params,
                                         **kwargs)
        r = json.loads(self.context.post_json('/jobs', job))
        return r['job_id']

    def cancel(self, job_id, file_ids = None):
        if file_ids is not None:
            file_ids_str = ','.join(map(str, file_ids))
            return json.loads(self.context.delete('/jobs/%s/files/%s' % (job_id, file_ids_str)))
        else:
            return json.loads(self.context.delete('/jobs/%s' % job_id))

    def cancel_all(self, vo = None):
        if vo is None:
            return json.loads(self.context.delete('/jobs/all'))
        else:
            return json.loads(self.context.delete('/jobs/vo/%s' % vo))
