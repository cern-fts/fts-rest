% FTS-REST-CLI(1) fts-rest-transfer-cancel
% fts-devel@cern.ch
% September 08, 2015
# NAME

fts-rest-transfer-cancel

# SYNOPIS

Usage: fts-rest-transfer-cancel [options]

# DESCRIPTION

This command can be used to cancel a running job.  It returns the final state of the canceled job.
Please, mind that if the job is already in a final state (FINISHEDDIRTY, FINISHED, FAILED),
this command will return this state.
You can additionally cancel only a subset appending a comma-separated list of file ids


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
$ fts-rest-transfer-cancel -s https://fts3-devel.cern.ch:8446 c079a636-c363-11e3-b7e5-02163e009f5a
FINISHED
$ fts-rest-transfer-cancel -s https://fts3-devel.cern.ch:8446 c079a636-c363-11e3-b7e5-02163e009f5a:5658,5659,5670
CANCELED, CANCELED, CANCELED

```
