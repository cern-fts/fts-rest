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
* **verify_checksum**   Enable checksum verification or indicate source, target, both or none checksum mode.
* **reuse**             Enable reuse (all transfers are handled by the same process)
* **overwrite**         Overwrite the destinations if exist
* **multihop**          Treat the transfer as a multihop transfer
* **source_spacetoken** Source space token
* **spacetoken**        Destination space token
* **bring_online**      Bring online timeout
* **timeout**           Transfer timeout in seconds
* **copy_pin_lifetime** Pin lifetime
* **retry**             Number of retries: <0 is no retries, 0 is server default, >0 is whatever value is passed
* **metadata**          Metadata to bind to the job
* **id_generator**      Job id generator algorithm: 'standard' is used by default with uuid1 and 'deterministic' is used for specific job id generation with uuid5 and the base_id+vo+sid
* **sid** 				Specific id given by the user to be used with the deterministic job id generator algorithm
* **max_time_in_queue** Max time the job can be on the queue. Accepts an integer without suffix (interpreted as hours), or with a suffix s (seconds), m (minutes) or h (hours). e.g `60s`
* **priority**          Job priority. It should be a number between 1 and 5. The higher the number, the higher the priority.

### Returns:
A dictionary representing a new job submission

### Example
```python
transfers = [transfer1, transfer2, ...]
job = fts3.new_job(transfers, verify_checksum=True, reuse=True, id_generator=JobIdGenerator.deterministic, sid='6067830a-8596-4093-86f4-3ab940ebf876' ...)
```

Generating a deterministic id
-----------------------------
When a new job is created, we use the standard algorithm for generating the ids based on uuid1 by default. 
However, the possibility of generating a deterministic id is implemented based on the base id and a vo id, which can be checked by executing the whoami command. 

```python
fts-rest-whoami -s "https://fts3-devel.cern.ch:8446"
User DN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=ftssuite/CN=737188/CN=Robot: fts3 testsuite
VO: dteam
VO id: 6b10f4e4-8fdc-5555-baa2-7d4850d4f406
Delegation id: e9d6ea6f75a45ab7
Base id: 01874efb-4735-4595-bc9c-591aef8240c9
```

When you create the job, you can use the deterministic job id generator and a specific id (sid). With these two parameters you can obtain your deterministic job id. This id generator uses uuid5, the base id, vo id and the sid. 

###Parameters to use:

* **id_generator**      Job id generator algorithm: 
						1. 'standard' uses uuid1 by default
						2. 'deterministic' uses uuid5 and provides specific job id generation based on:
							a. base_id (fixed)
							b. vo_id (uuid5(base_id, vo_name))
							c. sid (uuid5(vo_id, sid))
* **sid** 				Specific id given by the user to be used with the deterministic job id generator algorithm. This parameter is mandatory if the deterministic job id generator is activated.

### Example
```python
transfers = [transfer1, transfer2, ...]
job = fts3.new_job(transfers, verify_checksum=True, reuse=True, id_generator=JobIdGenerator.deterministic, sid='6067830a-8596-4093-86f4-3ab940ebf876' ...)
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
