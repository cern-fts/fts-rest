Submission API
==============

Create the transfers
--------------------
For this, use `new_transfer(source, destination, checksu, filesize, metadata)`

### Args:
* **source**      Source SURL
* **destination** Destination SURL
* **checksum**    Checksum (optional)
* **filesize**    File size (optional)
* **metadata**    Metadata to bind to the transfer (optional)

### Returns:
An initialized transfer

### Example
```python
transfer = fts3.new_transfer(
  'gsiftp://source/path', 'gsiftp://destination/path',
  checksum='ADLER32:1234', filesize=1024,
  metadata='Submission example'
)
```

You can add additional alternatives for the source

```python
fts3.add_alternative_source(transfer, 'gsiftp://alternative/path')
```

Group transfers in a job
------------------------
You can do the previous step as many times as transfers you want to group in a single job.
Once you got the transfers, you can create the job with
`new_job(transfers, verify_checksum, reuse, overwrite, multihop, source_spacetoken, spacetoken, bring_online, copy_pin_lifetime, retry, metadata)`

Note that _all_ parameters are optional.

### Args:
* **transfers**         Initial list of transfers
* **verify_checksum**   Enable checksum verification
* **reuse**             Enable reuse (all transfers are handled by the same process)
* **overwrite**         Overwrite the destinations if exist
* **multihop**          Treat the transfer as a multihop transfer
* **source_spacetoken** Source space token
* **spacetoken**        Destination space token
* **bring_online**      Bring online timeout
* **copy_pin_lifetime** Pin lifetime
* **retry**             Number of retries: <0 is no retries, 0 is server default, >0 is whatever value is passed
* **metadata**          Metadata to bind to the job

### Returns:
A dictionary representing a new job submission

### Example
```python
transfers = [transfer1, transfer2, ...]
job = fts3.new_job(transfers, verify_checksum=True, reuse=True, ...)
```

Submit the job
--------------
Finally you can submit the job. You can [delegate](README.md#delegate) yourself before, but submit will
take care of it anyway.

Also, there is no need to build the dictionary step by step as shown here. You can build the dictionary by yourself,
as long as it follows the [expected schema](../api-curl.md#get-the-submit-schema)

### Args:
* **context**
* **job**
* **delegation_lifetime** Delegation lifetime
* **force_delegation**    Force delegation even if there is a valid proxy

### Returns
The job id

### Example
```python
job_id = fts3.submit(context, job)
```
