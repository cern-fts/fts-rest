% FTS-REST-CLI(1) fts-rest-whoami
% fts-devel@cern.ch
% September 25, 2014
# NAME

fts-rest-whoami

# SYNOPIS

Usage: fts-rest-whoami [options]

# DESCRIPTION

This command exists for convenience. It can be used to check, as the name suggests,
who are we for the server.


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

# EXAMPLE
```
$ fts-rest-whoami -s https://fts3-pilot.cern.ch:8446
User DN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=saketag/CN=678984/CN=Alejandro Alvarez Ayllon
VO: dteam
VO: dteam/cern
Delegation id: 9a4257f435fa2010

```
