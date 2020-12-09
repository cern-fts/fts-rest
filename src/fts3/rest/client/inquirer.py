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
import urllib

from exceptions import *


class Inquirer(object):

    def __init__(self, context):
        self.context = context

    def get_job_status(self, job_id, list_files=False):

        if not isinstance(job_id, basestring):
            raise Exception('The job_id provided is not a string!')

        try:
            job_info = json.loads(self.context.get("/jobs/%s" % job_id))

            if list_files:
                job_info['files'] = json.loads(self.context.get("/jobs/%s/files" % job_id))
                job_info['dm'] = json.loads(self.context.get("/jobs/%s/dm" % job_id))

            return job_info

        except NotFound:
            raise NotFound(job_id)

    def get_jobs_statuses(self, job_ids, list_files=False):

        if isinstance(job_ids, list):
            xfer_ids = ','.join(job_ids)
        else:
            raise Exception('The input provided is not a list of ids!')

        try:
            if not list_files:
                job_info = json.loads(self.context.get("/jobs/%s" % xfer_ids))
            else:
                job_info = json.loads(self.context.get("/jobs/%s?files=file_state,dest_surl,finish_time,start_time,reason,source_surl,file_metadata" % xfer_ids))

            return job_info
        except NotFound:
            raise NotFound(job_ids)

    def get_job_list(self, user_dn=None, vo_name=None, source_se=None, dest_se=None, delegation_id=None, state_in=None):
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
        if delegation_id:
            args['dlg_id'] = delegation_id
        if state_in:
            args['state_in'] = ','.join(state_in)

        query = '&'.join(map(lambda (k, v): "%s=%s" % (k, urllib.quote(v, '')),
                             args.iteritems()))
        url += query

        return json.loads(self.context.get(url))

    def whoami(self):
        return json.loads(self.context.get("/whoami"))









 
  
   
    
     
      
       
