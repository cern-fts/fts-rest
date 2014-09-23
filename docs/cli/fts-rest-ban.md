% FTS-REST-CLI(1) fts-rest-ban
% fts-devel@cern.ch
% July 15, 2014
# NAME

fts-rest-ban

# SYNOPIS

Usage: fts-rest-ban [options]

# DESCRIPTION

Ban and unban storage elements and users

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

--storage
:	Storage element

--user
:	User dn

--unban
:	Unban instead of ban

--status
:	Status of the jobs that are already in the queue: cancel or wait

--timeout
:	The timeout for the jobs that are already in the queue if status is wait

--allow-submit
:	Allow submissions if status is wait

# EXAMPLE
```
$ fts-rest-ban -s https://fts3-devel.cern.ch:8446 --storage gsiftp://sample
No jobs affected
$ fts-rest-ban -s https://fts3-devel.cern.ch:8446 --storage gsiftp://sample --unban
$

```
