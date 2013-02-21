#!/usr/bin/env python
from fts3.rest.client import JobInquirer
import getopt
import logging
import sys
import traceback



# Usage
def usage():
	print "Usage: %s [-v|--verbose] [-h|--help] [-j] -s|--endpoint <endpoint> job-id" % sys.argv[0]
	print "\t-v, --verbose  Verbose output"
	print "\t-h, --help     Shows this help"
	print "\t-j             Prints the output in JSON format"
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
		
	filesStr = []
	for f in job['files']:
		fs = """\tTransfer id: %(file_id)d\n\tStatus: %(file_state)s\n\tReason: %(reason)s""" % (f)
		filesStr.append(fs)
	
	s += "Files: %d\n" % len(job['files']) + '\n'.join(filesStr)
	
	return s

# Generate JSON string
def job2Json(job):
	import json
	return json.dumps(job, indent = 2)

# Main code
endpoint  = None
printJson = False
opt, args = getopt.getopt(sys.argv[1:], 'hs:vj', ['help', 'endpoint=', 'verbose'])
for o, v in opt:
	if o in ('-h', '--help'):
		usage()
	elif o in ('-s', '--endpoint'):
		endpoint = v
	elif o in ('-v', '--verbose'):
		logging.getLogger().setLevel(logging.DEBUG)
	elif o in ('-j'):
		printJson = True

if endpoint is None:
	logging.critical("Need an endpoint")
	sys.exit(1)
	
if len(args) == 0:
	logging.critical("Need a job id")
	sys.exit(1)
	
jobId = args[0]

try:
	client    = JobInquirer(endpoint, logger = logging.getLogger())
	job       = client.getJobStatus(jobId)
	
	if not printJson:
		print job2HumanReadable(job)
	else:
		print job2Json(job)

except Exception, e:
	print >>sys.stderr, str(e)
	if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
		traceback.print_exc()
	sys.exit(1)
