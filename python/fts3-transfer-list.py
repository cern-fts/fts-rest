#!/usr/bin/env python
from fts3.rest.client import JobInquirer
import getopt
import logging
import sys
import traceback



# Usage
def usage():
	print "Usage: %s [-v|--verbose] [-h|--help] [-j] [-u|--userdn <userdn>] [-o|--voname <vo>] -s|--endpoint <endpoint>" % sys.argv[0]
	print "\t-v, --verbose  Verbose output"
	print "\t-h, --help     Shows this help"
	print "\t-j             Prints the output in JSON format"
	print "\t-u, --userdn   Query only for the given user"
	print "\t-o, --voname   Query only for the given VO"
	print "\t-s, --endpoint FTS3 REST endpoint to use"
	sys.exit(0)


# Generate a human readable string
def job2HumanReadable(job):	
	s = """Request ID: %(job_id)s
Status: %(job_state)s
Client DN: %(user_dn)s
Reason: %(reason)s
Submission time: %(submit_time)s
Priority: %(priority)d
VO Name: %(vo_name)s
""" % job

	return s


def jobList2HumanReadable(jobList):
	jobStr = []
	for job in jobList:
		jobStr.append(job2HumanReadable(job))
	return '\n'.join(jobStr)
	

# Generate JSON string
def jobList2Json(job):
	import json
	return json.dumps(job, indent = 2)

# Main code
endpoint  = None
printJson = False
userDn    = None
voName    = None
opt, args = getopt.getopt(sys.argv[1:], 'hs:vju:o:', ['help', 'endpoint=', 'verbose', 'userdn=', 'voname='])
for o, v in opt:
	if o in ('-h', '--help'):
		usage()
	elif o in ('-s', '--endpoint'):
		endpoint = v
	elif o in ('-v', '--verbose'):
		logging.getLogger().setLevel(logging.DEBUG)
	elif o in ('-j'):
		printJson = True
	elif o in ('-u', '--userdn'):
		userDn = v
	elif o in ('-o', '--voname'):
		voName = v

if endpoint is None:
	logging.critical("Need an endpoint")
	sys.exit(1)


try:
	client    = JobInquirer(endpoint, logger = logging.getLogger())
	jobList   = client.getJobList(userDn, voName)
	
	if not printJson:
		print jobList2HumanReadable(jobList)
	else:
		print jobList2Json(jobList)

except Exception, e:
	print >>sys.stderr, str(e)
	if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
		traceback.print_exc()
	sys.exit(1)
