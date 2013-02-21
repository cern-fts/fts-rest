#!/usr/bin/env python
from fts3.rest.client import Delegator

import getopt
import logging
import os
import sys


logging.getLogger().setLevel(logging.DEBUG)


if 'X509_USER_PROXY' not in os.environ:
	raise Exception("X509_USER_PROXY must be set")


proxy = os.environ['X509_USER_PROXY']
endpoint = sys.argv[1]

delegator = Delegator(endpoint, proxy, proxy)
delegationId = delegator.delegate()

print "Got delegation ID", delegationId
