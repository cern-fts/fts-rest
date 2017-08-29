Bulk submissions
================

One job with multiple files
---------------------------
This is the basic submission pattern: several files that belong to a single job.

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
      "filesize": 1024,
      "activity": "Production"
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
      "filesize": 2048
    }
  ],
  "params": {
  }
}
```

One job with multiple files, enable session reuse
-------------------------------------------------
Same as before, but enabling session reuse. This is specially helpful for a lot of files of small size.
The format is the same as the previous one, just pass the flag `--reuse` to the command.

Alternatives
------------

### Multiple sources, one destination
You can provide several sources and one single destination, so if A to B fails, A2 to B will be tried.

```json
{
  "files": [
    {
      "sources": [
        "gsiftp://source.host/file", "gsiftp://alternative.host/file"
      ],
      "destinations": [
        "gsiftp://destination.host/file"
      ],
      "selection_strategy": "orderly",
      "metadata": "file-metadata",
      "checksum": "ADLER32:1234",
      "filesize": 1024
    }
  ]
}
```

Please, mind that the protocols have to be the same for all URL in this case.

### Multiple sources and multiple destinations
The same can be achieved but even combining protocols.

```json
{
  "files": [
    {
      "sources": [
        "davs://source.host/file", "gsiftp://source.host/file"
      ],
      "destinations": [
        "davs://destination.host/file", "gsiftp://destination.host/file"
      ],
      "selection_strategy": "orderly",
      "metadata": "file-metadata",
      "checksum": "ADLER32:1234",
      "filesize": 1024
    }
  ]
}
```

davs => davs will be tried first, and gsiftp => gsiftp will be used as fallback.

### Parameters
You can pass additional parameters to FTS3 that will influence the way the transfers
are performed. These parameters are sent as part of the JSON that describes the full
job.

```json
{
  "files": [],
  "params": {
    "max_time_in_queue": 36000,
    "timeout": 3600,
    "nostreams": 0,
    "buffer_size": 1024,
    "strict_copy": false,
    "ipv4": true,
    "ipv6": true,
    "multihop": false,
    "reuse": false,
    "copy_pin_lifetime": -1,
    "bring_online": -1,
    "spacetoken": "DISK",
    "source_spacetoken": "TAPE",
    "retry": 0,
    "retry_delay": 0,
    "priority": 3,
    "overwrite": false,
    "verify_checksum": true,
    "job_metadata": "My Custom Tag",
    "credential": "S3:whatnot.com",
    "id_generator": "standard",
    "sid": "abcd",
    "s3alternate": true
  }
}
```

Of course, all these parameters are optional. You can set only a subset of them,
or none at all.

* **max_time_in_queue** After this number of seconds on the queue, the transfer will be
canceled.
* **timeout** After this number of seconds running, the transfer will be aborted.
* **nostreams** Number of streams  to use during the transfer.
Not all protocols support this.
* **buffer_size** TCP buffer size.
* **strict_copy** If true, only a transfer will be done. No checksum, no size validation, no
parent directory creation... useful for endpoints that do not support any, of some, of this
operations, like S3.
* **ipv4** Enable/disable IPv4 support. Not all protocols support this.
* **ipv6** Enable/disable IPv6 support. Not all protocols support this.
* **multihop** Multihop transfer. Individual files within the job will be run sequentially.
If any step fails, the remaining ones wil be canceled.
* **reuse** Transfer all the files within the job reusing the same connection. Not all protocols
support this. Useful for small files.
* **copy_pin_lifetime** If greater than -1, a Bring Online operation will be done prior to the
stransfer. The value of this field will be sent to the remote storage for the lifetime
of the replica on disk.
* **bring_online** Bring online timeout. After this number of seconds, the staging operation will
be canceled, and the transfer will not take place. If greater than -1, a Bring Online operation will
be done.
* **spacetoken** Destination space token.
* **source_spacetoken** Source space token.
* **retry** Let FTS3 retry the file on error. Not all errors are retries. For instance,
a "File not found" will *not* be retried.
* **retry_dely** Wait this many seconds between retries.
* **priority** Job priority. Applied after VO Shares, and Activity Shares. *No* fair share.
If you keep submitting jobs with high priorities, jobs with lower priority will not go
through.
* **overwrite** If true, the destination file will be overwritten if it exists.
* **verify_checksum** One of 'source','target', 'both' (or true), and 'none' (or false)
* **job_metadata** User data. Can be JSON formatted.
* **credential** Deprecated. For newer versions of FTS3, the service will figure out
itself which cloud credentials must be used.
* **id_generator** Which job-id generator to use. Valid values are "standard" (UUID 1),
or "deterministic" (UUID 5).
* **sid** When using the deterministic job-id variant, the final job-id is generated as
 `UUID5(UUID5('01874efb-4735-4595-bc9c-591aef8240c9', vo_name), sid)`

`01874efb-4735-4595-bc9c-591aef8240c9` is the global root UUID for FTS3. It remains constant
across FTS3 installations.
* **s3alternate** (Introduced in 3.5.1). Sign S3 urls where the bucket is on the path.
