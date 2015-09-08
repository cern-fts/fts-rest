% FTS-REST-CLI(1) fts-rest-server-status
% fts-devel@cern.ch
% September 08, 2015
# NAME

fts-rest-server-status

# SYNOPIS

Usage: fts-rest-server-status [options]

# DESCRIPTION

Use this command to check on the service status.

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

-H/--host
:	Limit the output to a given host

--is-active
:	The tool will return < 0 on error, 0 if nothing is active, 1 if there are active transfers, 2 if there are active staging, 3 if there are both

