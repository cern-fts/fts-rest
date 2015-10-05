# FTS3 REST Command Line Tools
## [fts-rest-ban](fts-rest-ban.md)
Ban and unban storage elements and users

## [fts-rest-transfer-submit](fts-rest-transfer-submit.md)
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


## [fts-rest-transfer-status](fts-rest-transfer-status.md)
This command can be used to check the current status of a given job

## [fts-rest-transfer-list](fts-rest-transfer-list.md)
This command can be used to list the running jobs, allowing to filter by user dn or vo name

## [fts-rest-server-status](fts-rest-server-status.md)
Use this command to check on the service status.

## [fts-rest-transfer-cancel](fts-rest-transfer-cancel.md)
This command can be used to cancel a running job.  It returns the final state of the canceled job.
Please, mind that if the job is already in a final state (FINISHEDDIRTY, FINISHED, FAILED),
this command will return this state.
You can additionally cancel only a subset appending a comma-separated list of file ids


## [fts-rest-whoami](fts-rest-whoami.md)
This command exists for convenience. It can be used to check, as the name suggests,
who are we for the server.


## [fts-rest-delete-submit](fts-rest-delete-submit.md)
This command can be used to submit a deletion job to FTS3. It supports simple and bulk submissions.


## [fts-rest-delegate](fts-rest-delegate.md)
This command can be used to (re)delegate your credentials to the FTS3 server

## [fts-rest-snapshot](fts-rest-snapshot.md)
This command can be used to retrieve the internal status FTS3 has on all pairs with ACTIVE transfers.
It allows to filter by VO, source SE and destination SE

