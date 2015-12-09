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
  ]
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
