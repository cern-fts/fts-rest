#!/usr/bin/env python
from fts3.rest.client import Client
from fts3.rest.client import setDefaultLogging

import getopt
import logging
import os
import sys


setDefaultLogging()

logging.getLogger().setLevel(logging.DEBUG)


if 'X509_USER_PROXY' not in os.environ:
	raise Exception("X509_USER_PROXY must be set")


proxy = os.environ['X509_USER_PROXY']
endpoint = sys.argv[1]

client = Client(endpoint, proxy, proxy)
delegationId = client.delegate()

print "Got delegation ID", delegationId
