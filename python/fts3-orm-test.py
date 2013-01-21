#!/usr/bin/env python
import sys
from fts3 import orm

if len(sys.argv) < 2:
	print >>sys.stderr, "Need a connection string"
	sys.exit(1)

session = orm.connect(sys.argv[1])

schema = session.query(orm.SchemaVersion).first()
print "FTS3 Schema version", schema

cred = session.query(orm.CredentialVersion).first()
print "FTS3 Credential version", cred


print "Press 1 to list jobs"
print "      2 to list transfers"
print "      3 to list configuration audit"

input = sys.stdin.readline()[0]

if input == '1':
	query = session.query(orm.Job);
elif input == '2':
	query = session.query(orm.File);
elif input == '3':
	query = session.query(orm.ConfigAudit)
else:
	print >>sys.stderr, "Invalid input!"
	sys.exit(1)
	
sys.stdin.flush()

print query
raw_input("Press any key to execute")
for i in query:
	print i
