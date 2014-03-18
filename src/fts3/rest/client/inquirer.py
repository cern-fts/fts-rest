import json
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

    def get_job_list(self, user_dn=None, vo_name=None):
        url = "/jobs?"
        args = {}
        if user_dn:
            args['user_dn'] = user_dn
        if vo_name:
            args['vo_name'] = vo_name

        query = '&'.join(map(lambda (k, v): "%s=%s" % (k, urllib.quote(v, '')),
                             args.iteritems()))
        url += query

        return json.loads(self.context.get(url))
