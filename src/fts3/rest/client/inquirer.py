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
    import json
except:
    import simplejson as json
import urllib

from exceptions import *


class Inquirer(object):

    def __init__(self, context):
        self.context = context

    def get_job_status(self, job_id, list_files=False):
        try:
            job_info = json.loads(self.context.get("/jobs/%s" % job_id))
            if list_files:
                job_info['files'] = json.loads(self.context.get("/jobs/%s/files" % job_id))
            return job_info
        except NotFound:
            raise NotFound(job_id)

    def get_job_list(self, user_dn=None, vo_name=None, source_se=None, dest_se=None):
        url = "/jobs?"
        args = {}
        if user_dn:
            args['user_dn'] = user_dn
        if vo_name:
            args['vo_name'] = vo_name
        if source_se:
            args['source_se'] = source_se
        if dest_se:
            args['dest_se'] = dest_se

        query = '&'.join(map(lambda (k, v): "%s=%s" % (k, urllib.quote(v, '')),
                             args.iteritems()))
        url += query

        return json.loads(self.context.get(url))

    def whoami(self):
        return json.loads(self.context.get("/whoami"))

    def get_snapshot(self, vo=None, source=None, destination=None):
        if vo:
            vo = urllib.quote(vo, '')
        else:
            vo = ''
        if source:
            source = urllib.quote(source, '')
        else:
            source = ''
        if destination:
            destination = urllib.quote(destination, '')
        else:
            destination = ''
        return json.loads(
            self.context.get("/snapshot?vo_name=%s&source_se=%s&dest_se=%s" % (vo, source, destination))
        )
