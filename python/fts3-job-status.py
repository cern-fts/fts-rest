#!/usr/bin/env python
from fts3.rest.client import Client, setDefaultLogging
import getopt
import logging
import sys
import traceback


setDefaultLogging()


# Parameters
def usage():
	print "Usage: %s [-v|--verbose] [-h|--help] -s|--endpoint <endpoint> job-id" % sys.argv[0]
	sys.exit(0)




endpoint = None
opt, args = getopt.getopt(sys.argv[1:], 'hs:v', ['--help', '--endpoint', '--verbose'])
for o, v in opt:
	if o in ('-h', '--help'):
		usage()
	elif o in ('-s', '--endpoint'):
		endpoint = v
	elif o in ('-v', '--verbose'):
		logging.getLogger().setLevel(logging.DEBUG)

if endpoint is None:
	logging.critical("Need an endpoint")
	sys.exit(1)
	
if len(args) == 0:
	logging.critical("Need a job id")
	sys.exit(1)
	
jobId = args[0]

try:
	client    = Client(endpoint, logger = logging.getLogger())
	job       = client.getJobStatus(jobId)
	
	print "Request ID: %s" % job['job_id']
	print "Status: %s" % job['job_state']
	print "Client DN: %s" % job['user_dn']
	print "Reason: %s" % job['reason']
	print "Submission time: %s" % job['submit_time']
	print "Priority: %d" % job['priority']
	print "VOName: %s" % job['vo_name']
	print "Files: %d" % len(job['files'])
	for f in job['files']:
		print "\tTransfer id: %d" % f['file_id']
		print "\tStatus: %s" % f['file_state']
		print "\tReason: %s" % f['reason']

except Exception, e:
	print >>sys.stderr, str(e)
	if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
		traceback.print_exc()
	sys.exit(1)
