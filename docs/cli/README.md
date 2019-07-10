# FTS3 REST Command Line Tools

## fts-rest-ban
Ban and unban storage elements and users
### Usage
Usage: fts-rest-ban [options]

### Options
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


### Example
```
$ fts-rest-ban -s https://fts3-devel.cern.ch:8446 --storage gsiftp://sample
No jobs affected
$ fts-rest-ban -s https://fts3-devel.cern.ch:8446 --storage gsiftp://sample --unban
$

```
## fts-rest-delegate
This command can be used to (re)delegate your credentials to the FTS3 server
### Usage
Usage: fts-rest-delegate [options]

### Options
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

-f/--force
:	Force the delegation

-H/--hours
:	Duration of the delegation in hours (default: 12)


### Example
```
$ fts-rest-delegate -s https://fts3-devel.cern.ch:8446
Delegation id: 9a4257f435fa2010"

```
## fts-rest-delete-submit
This command can be used to submit a deletion job to FTS3. It supports simple and bulk submissions.

### Usage
Usage: fts-rest-delete-submit [options] SURL1 [SURL2] [SURL3] [...]

### Options
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


### Example
```
$ fts-rest-delete-submit -s https://fts3-devel.cern.ch:8446 gsiftp://source.host/file1 gsiftp://source.host/file2
Job successfully submitted.
Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a

$ fts-rest-delete-submit -s https://fts3-devel.cern.ch:8446 -f bulk.list
Job successfully submitted.
Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a

```
## fts-rest-server-status
Use this command to check on the service status.
### Usage
Usage: fts-rest-server-status [options]

### Options
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


## fts-rest-transfer-cancel
This command can be used to cancel a running job.  It returns the final state of the canceled job.
Please, mind that if the job is already in a final state (FINISHEDDIRTY, FINISHED, FAILED),
this command will return this state.
You can additionally cancel only a subset appending a comma-separated list of file ids

### Usage
Usage: fts-rest-transfer-cancel [options]

### Options
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


### Example
```
$ fts-rest-transfer-cancel -s https://fts3-devel.cern.ch:8446 c079a636-c363-11e3-b7e5-02163e009f5a
FINISHED
$ fts-rest-transfer-cancel -s https://fts3-devel.cern.ch:8446 c079a636-c363-11e3-b7e5-02163e009f5a:5658,5659,5670
CANCELED, CANCELED, CANCELED

```
## fts-rest-transfer-list
This command can be used to list the running jobs, allowing to filter by user dn or vo name
### Usage
Usage: fts-rest-transfer-list [options]

### Options
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

-u/--userdn
:	Query only for the given user

-o/--voname
:	Query only for the given vo

--source
:	Query only for the given source storage element

--destination
:	Query only for the given destination storage element


### Example
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
## fts-rest-transfer-status
This command can be used to check the current status of a given job
### Usage
Usage: fts-rest-transfer-status [options] JOB_ID

### Options
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


### Example
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
## fts-rest-transfer-submit
This command can be used to submit new jobs to FTS3. It supports simple and bulk submissions. The bulk
format is as follows:

```json
{
  "files": [
    {
      "sources": [
        "gsiftp://source.host/file"
      ],
      "destinations": [
        "gsiftp://destination.host/file"
      ],
      "metadata": "file-metadata",
      "checksum": "ADLER32:1234",
      "filesize": 1024
    },
    {
      "sources": [
        "gsiftp://source.host/file2"
      ],
      "destinations": [
        "gsiftp://destination.host/file2"
      ],
      "metadata": "file2-metadata",
      "checksum": "ADLER32:4321",
      "filesize": 2048,
      "activity": "default"
    }
  ]
}
```

### Usage
Usage: fts-rest-transfer-submit [options] SOURCE DESTINATION [CHECKSUM]

### Options
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

--delegate-when-lifetime-lt
:	Delegate the proxy when the remote lifetime is less than this value (in minutes)

-o/--overwrite
:	Overwrite files. 

-r/--reuse
:	Enable session reuse for the transfer job. 

--job-metadata
:	Transfer job metadata. 

--file-metadata
:	File metadata. 

--file-size
:	File size (in bytes)

-g/--gparam
:	Gridftp parameters. 

-t/--dest-token
:	The destination space token or its description. 

-S/--source-token
:	The source space token or its description. 

-K/--compare-checksum
:	Deprecated: compare checksums between source and destination. 

-C/--checksum-mode
:	Compare checksums in source, target, both or none. 

--copy-pin-lifetime
:	Pin lifetime of the copy in seconds. 

--bring-online
:	Bring online timeout in seconds. 

--timeout
:	Transfer timeout in seconds. 

--fail-nearline
:	Fail the transfer is the file is nearline. 

--dry-run
:	Do not send anything, just print the json message. 

-f/--file
:	Name of configuration file

--retry
:	Number of retries. If 0, the server default will be used. If negative, there will be no retries. 

-m/--multi-hop
:	Submit a multihop transfer. 

--cloud-credentials
:	Use cloud credentials for the job (i. E. Dropbox). 

--nostreams
:	Number of streams

--ipv4
:	Force ipv4

--ipv6
:	Force ipv6


### Example
```
$ fts-rest-transfer-submit -s https://fts3-devel.cern.ch:8446 gsiftp://source.host/file gsiftp://destination.host/file
Job successfully submitted.
Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a

$ fts-rest-transfer-submit -s https://fts3-devel.cern.ch:8446 -f bulk.json
Job successfully submitted.
Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a

```
## fts-rest-whoami
This command exists for convenience. It can be used to check, as the name suggests,
who are we for the server.

### Usage
Usage: fts-rest-whoami [options]

### Options
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


### Example
```
$ fts-rest-whoami -s https://fts3-pilot.cern.ch:8446
User DN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=saketag/CN=678984/CN=Alejandro Alvarez Ayllon
VO: dteam
VO: dteam/cern
Delegation id: 9a4257f435fa2010

```
