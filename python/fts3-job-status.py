#!/usr/bin/env python
from fts3.rest.client import ClientV1
import getopt
import sys

def usage():
	print "Usage: %s [-h|--help] -s|--endpoint <endpoint> job-id" % sys.argv[0]
	sys.exit(0)

endpoint = None
opt, args = getopt.getopt(sys.argv[1:], 'hs:', ['--help', '--endpoint'])
for o, v in opt:
	if o in ('-h', '--help'):
		usage()
	elif o in ('-s', '--endpoint'):
		endpoint = v

if endpoint is None:
	print >>sys.stderr, "Need an endpoint"
	sys.exit(1)
	
if len(args) == 0:
	print >>sys.stderr, "Need a job id"
	sys.exit(1)
	
jobId = args[0]

try:
	client    = ClientV1(endpoint)
	info      = client.getEndpointInfo()
	job       = client.getJobStatus(jobId)

	print "# Using endpoint: %s" % info['url']
	print "# REST API version: %s" % info['api']
	print "# Schema version: %(major)d.%(minor)d.%(patch)d" % info['schema']
	print "# Delegation version: %(major)d.%(minor)d.%(patch)d" % info['delegation']
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
	print >>sys.stderr, e
	sys.exit(1)
