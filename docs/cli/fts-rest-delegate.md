% FTS-REST-CLI(1) fts-rest-delegate
% fts-devel@cern.ch
% June 17, 2015
# NAME

fts-rest-delegate

# SYNOPIS

Usage: fts-rest-delegate [options]

# DESCRIPTION

This command can be used to (re)delegate your credentials to the FTS3 server

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

-f/--force
:	Force the delegation

# EXAMPLE
```
$ fts-rest-delegate -s https://fts3-devel.cern.ch:8446
Delegation id: 9a4257f435fa2010"

```
