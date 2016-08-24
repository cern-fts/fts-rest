% FTS-REST-CLI(1) fts-rest-snapshot
% fts-devel@cern.ch
% August 24, 2016
# NAME

fts-rest-snapshot

# SYNOPIS

Usage: fts-rest-snapshot [options]

# DESCRIPTION

This command can be used to retrieve the internal status FTS3 has on all pairs with ACTIVE transfers.
It allows to filter by VO, source SE and destination SE


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

--vo
:	Filter by vo

--source
:	Filter by source se

--destination
:	Filter by destination se

# EXAMPLE
```
$ fts-rest-snapshot -s https://fts3-devel.cern.ch:8446
Source:              gsiftp://whatever
Destination:         gsiftp://whatnot
VO:                  dteam
Max. Active:         5
Active:              1
Submitted:           0
Finished:            0
Failed:              0
Success ratio:       -
Avg. Throughput:     -
Avg. Duration:       -
Avg. Queued:         0 seconds
Most frequent error: -

```
