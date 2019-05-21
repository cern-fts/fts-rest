% FTS-REST-CLI(1) fts-rest-delete-submit
% fts-devel@cern.ch
% May 21, 2019
# NAME

fts-rest-delete-submit

# SYNOPIS

Usage: fts-rest-delete-submit [options] SURL1 [SURL2] [SURL3] [...]

# DESCRIPTION

This command can be used to submit a deletion job to FTS3. It supports simple and bulk submissions.


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

-b/--blocking
:	Blocking mode. Wait until the operation completes. 

-i/--interval
:	Interval between two poll operations in blocking mode. 

-e/--expire
:	Expiration time of the delegation in minutes. 

--job-metadata
:	Transfer job metadata. 

--file-metadata
:	File metadata. 

-S/--spacetoken
:	The space token or its description. 

--dry-run
:	Do not send anything, just print the json message. 

-f/--file
:	Name of configuration file

--retry
:	Number of retries. If 0, the server default will be used. If negative, there will be no retries. 

--cloud-credentials
:	Use cloud credentials for the job (i. E. Dropbox). 

# EXAMPLE
```
$ fts-rest-delete-submit -s https://fts3-devel.cern.ch:8446 gsiftp://source.host/file1 gsiftp://source.host/file2
Job successfully submitted.
Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a

$ fts-rest-delete-submit -s https://fts3-devel.cern.ch:8446 -f bulk.list
Job successfully submitted.
Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a

```
