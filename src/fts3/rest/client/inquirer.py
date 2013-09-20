from exceptions import *
import json
import urllib


class Inquirer(object):

    def __init__(self, context):
        self.context = context

    def getJobStatus(self, jobId):
        try:
            return json.loads(self.context.get("/jobs/%s" % jobId))
        except NotFound:
            raise NotFound(jobId)

    def getJobList(self, userDn=None, voName=None):
        url = "/jobs?"
        args = {}
        if userDn:
            args['user_dn'] = userDn
        if voName:
            args['vo_name'] = voName

        query = '&'.join(map(lambda (k, v): "%s=%s" % (k, urllib.quote(v, '')),
                             args.iteritems()))
        url += query

        return json.loads(self.context.get(url))
