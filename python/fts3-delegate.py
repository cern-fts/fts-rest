#!/usr/bin/env python
from fts3.rest.client import ClientV1
import getopt
import os
import sys


if 'X509_USER_PROXY' not in os.environ:
	raise Exception("X509_USER_PROXY must be set")


proxy = os.environ['X509_USER_PROXY']
endpoint = sys.argv[1]

print "Using endpoint", endpoint
print "Using proxy", proxy


client = ClientV1(endpoint, proxy, proxy)
delegationId = client.delegate()

print "Got delegation ID", delegationId
