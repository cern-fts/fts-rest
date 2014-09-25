% FTS-REST-CLI(1) fts-rest-transfer-list
% fts-devel@cern.ch
% September 25, 2014
# NAME

fts-rest-transfer-list

# SYNOPIS

Usage: fts-rest-transfer-list [options]

# DESCRIPTION

This command can be used to list the running jobs, allowing to filter by user dn or vo name

# OPTIONS

-h/--help
:	Show this help message and exit

-v/--verbose
:	Verbose output. 

-s/--endpoint
:	Fts3 rest endpoint. 

-j/--json
:	Print the output in json format. 

--key
:	The user certificate private key. 

--cert
:	The user certificate. 

--insecure
:	Do not validate the server certificate

--access-token
:	Oauth2 access token (supported only by some endpoints, takes precedence)

-u/--userdn
:	Query only for the given user

-o/--voname
:	Query only for the given vo

--source
:	Query only for the given source storage element

--destination
:	Query only for the given destination storage element

# EXAMPLE
```
$ fts-rest-transfer-list -s https://fts3-devel.cern.ch:8446 -o atlas
Request ID: ff294db7-655a-4c0a-9efb-44a994677bb3
Status: ACTIVE
Client DN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=ddmadmin/CN=531497/CN=Robot: ATLAS Data Management
Reason: None
Submission time: 2014-04-15T07:05:38
Priority: 3
VO Name: atlas

Request ID: a2e4586c-760a-469e-8303-d0f3d5aadc73
Status: READY
Client DN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=ddmadmin/CN=531497/CN=Robot: ATLAS Data Management
Reason: None
Submission time: 2014-04-15T07:07:33
Priority: 3
VO Name: atlas

```
