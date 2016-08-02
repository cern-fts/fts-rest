% FTS-REST-CLI(1) fts-rest-transfer-status
% fts-devel@cern.ch
% August 02, 2016
# NAME

fts-rest-transfer-status

# SYNOPIS

Usage: fts-rest-transfer-status [options] JOB_ID

# DESCRIPTION

This command can be used to check the current status of a given job

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

--capath
:	Use the specified directory to verify the peer

--insecure
:	Do not validate the server certificate

--access-token
:	Oauth2 access token (supported only by some endpoints, takes precedence)

# EXAMPLE
```
$ fts-rest-transfer-status -s https://fts3-devel.cern.ch:8446 c079a636-c363-11e3-b7e5-02163e009f5a
Request ID: c079a636-c363-11e3-b7e5-02163e009f5a
Status: FINISHED
Client DN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=saketag/CN=678984/CN=Alejandro Alvarez Ayllon
Reason:
Submission time: 2014-04-13T23:31:34
Priority: 3
VO Name: dteam

```
