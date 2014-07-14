FTS3 RESTful CLI
================

Installation
------------
### EPEL
Currently we do not ship our REST API in EPEL, so the only way of obtaining it is through our continuous build repository:

```ini
[fts3-prod-el6]
name=FTS3 Continuous Build Repository (Production)
baseurl=http://grid-deployment.web.cern.ch/grid-deployment/dms/fts3/repos/el6/$basearch
gpgcheck=0
enabled=1
protect=0
```

The package needed is ```fts-rest-cli```

### Getting the code
These clients are pure Python, so they can be checked out directly from the repository, or downloaded from the proper release tag.

In both cases you will need to install ```python-pycurl``` and ```m2crypto```

```
yum install python-pycurl m2crypto
```

Or, for EPEL5

```
yum install python26 python26-pycurl python26-m2crypto
```

Now, you can get the code checking out from the stage branch (this is, release candidate)

```
git clone https://github.com/cern-it-sdc-id/fts3-rest.git --branch stage
```

Finally, you just need to set the PATH and PYTHONPATH acordingly

```bash
export PYTHONPATH=$PYTHONPATH:~+/fts3-rest/src/
export PATH=$PATH:~+/fts3-rest/src/cli/
```

You can now check if everything is properly set up running this command

```
fts-rest-delegate -s https://fts3-devel.cern.ch:8446 -v
```

Please, note than in EPEL5 the X509v3 extension support has been disabled.

Usage
-----

These options are common to all tools.

```
  -h, --help                       show this help message and exit
  -v, --verbose                    verbose output
  -s ENDPOINT, --endpoint=ENDPOINT FTS3 REST endpoint
  -j                               print the output in JSON format
  --key=UKEY                       the user certificate private key
  --cert=UCERT                     the user certificate
```

### fts-rest-ban
Ban and unban storage elements and users.

Options:

```
  --storage=STORAGE     storage element
  --user=USER_DN        user dn
  --unban               unban instead of ban
  --status=STATUS       status of the jobs that are already in the queue:
                        cancel or wait
  --timeout=TIMEOUT     the timeout for the jobs that are already in the queue
                        if status is wait
  --allow-submit        allow submissions if status is wait
```

Mind that not all combinations make sense:

* one, and only one, of --storage and --user must be specified
* --status can only be cancel for --user
* --allow-submit can only be enabled if --status is wait, for storages

```
$ fts-rest-ban -s https://fts3-devel.cern.ch:8446 --storage gsiftp://sample
No jobs affected
$ fts-rest-ban -s https://fts3-devel.cern.ch:8446 --storage gsiftp://sample --unban
$
```

### fts-rest-delegate
This command can be used to (re)delegate your credentials to the FTS3 server.

Options:

```
  -f, --force           force the delegation
```

If the stored credentials in the server are recent enough, it won't try to do the delegation unless it is forced with `--forced`

```
$ fts-rest-delegate -s https://fts3-devel.cern.ch:8446
Delegation id: 9a4257f435fa2010
```

### fts-rest-snapshot
This command can be used to retrieve the internal status FTS3 has on all pairs with ACTIVE transfers. It allows
to filter by VO, source SE and destination SE.

Options:
```
  --vo=VO               filter by VO
  --source=SOURCE       filter by source SE
  --destination=DESTINATION
                        filter by destination SE
```

```
fts-rest-snapshot -s https://fts3-devel.cern.ch:8446
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

### fts-rest-transfer-cancel
This command can be used to cancel a running job.  It returns the final state of the canceled job.
Please, mind that if the job is already in a final state (FINISHEDDIRTY, FINISHED, FAILED), this command will return this state.

```
$ fts-rest-transfer-cancel -s https://fts3-devel.cern.ch:8446 c079a636-c363-11e3-b7e5-02163e009f5a
FINISHED
```

### fts-rest-transfer-list
This command can be used to list the running jobs, allowing to filter by user dn or vo name.

Options:
```
  -u USER_DN, --userdn=USER_DN
                        query only for the given user.
  -o VO_NAME, --voname=VO_NAME
                        query only for the given VO.
```

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


### fts-rest-transfer-status
This command can be used to check the current status of a given job.

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

If the option `-j` (json) is specified, the output will be more verbose as well.

```
$ fts-rest-transfer-status -s https://fts3-devel.cern.ch:8446 c079a636-c363-11e3-b7e5-02163e009f5a -j
```
```json
{
  "cred_id": "0ef8fb17bc42a356",
  "user_dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=saketag/CN=678984/CN=Alejandro Alvarez Ayllon",
  "retry": 0,
  "job_id": "c079a636-c363-11e3-b7e5-02163e009f5a",
  "cancel_job": false,
  "job_finished": "2014-04-13T23:31:37",
  "submit_host": "fts3devel01.cern.ch",
  "priority": 3,
  "source_space_token": "",
  "max_time_in_queue": null,
  "job_metadata": {
    "test": "test_bring_online_only",
    "label": "fts3-tests"
  },
  "source_se": "srm://hepgrid11.ph.liv.ac.uk",
  "user_cred": "",
  "reuse_job": false,
  "files": [
    {
      "symbolicname": null,
      "tx_duration": null,
      "pid": null,
      "hashed_id": 16774,
      "num_failures": null,
      "dest_surl": "srm://hepgrid11.ph.liv.ac.uk:8446/srm/managerv2?SFN=/dpm/ph.liv.ac.uk/home/dteam//fts3tests.5c48938b-e4fe-44e6-9a3e-a4463abe8386",
      "log_debug": null,
      "retry": 0,
      "job_id": "c079a636-c363-11e3-b7e5-02163e009f5a",
      "job_finished": null,
      "staging_start": "2014-04-13T23:31:36",
      "filesize": null,
      "source_se": "srm://hepgrid11.ph.liv.ac.uk",
      "file_state": "FINISHED",
      "start_time": null,
      "current_failures": null,
      "internal_file_params": null,
      "reason": "",
      "file_id": 594344,
      "error_phase": null,
      "source_surl": "srm://hepgrid11.ph.liv.ac.uk:8446/srm/managerv2?SFN=/dpm/ph.liv.ac.uk/home/dteam//fts3tests.5c48938b-e4fe-44e6-9a3e-a4463abe8386",
      "bringonline_token": "4899eeca-ccf5-4a4f-a0f7-fbef0adddf03",
      "selection_strategy": null,
      "retries": [],
      "dest_se": "srm://hepgrid11.ph.liv.ac.uk",
      "file_index": 0,
      "finish_time": null,
      "checksum": null,
      "staging_finished": "2014-04-13T23:31:37",
      "user_filesize": 0.0,
      "file_metadata": "None",
      "error_scope": null,
      "transferhost": "fts3devel01.cern.ch",
      "throughput": null,
      "activity": "default",
      "log_file": null,
      "agent_dn": null,
      "reason_class": null,
      "vo_name": "dteam"
    }
  ],
  "source_token_description": null,
  "job_params": "",
  "bring_online": 120,
  "reason": "",
  "space_token": "",
  "submit_time": "2014-04-13T23:31:34",
  "dest_se": "srm://hepgrid11.ph.liv.ac.uk",
  "internal_job_params": null,
  "finish_time": "2014-04-13T23:31:37",
  "verify_checksum": false,
  "vo_name": "dteam",
  "copy_pin_lifetime": -1,
  "agent_dn": null,
  "job_state": "FINISHED",
  "overwrite_flag": false
}
```

### fts-rest-transfer-submit
This command can be used to submit new jobs to FTS3. It has several options:

```
  -b, --blocking        blocking mode. Wait until the operation completes.
  -i POLL_INTERVAL, --interval=POLL_INTERVAL
                        interval between two poll operations in blocking mode.
  -e PROXY_LIFETIME, --expire=PROXY_LIFETIME
                        expiration time of the delegation in minutes.
  -o, --overwrite       overwrite files.
  -r, --reuse           enable session reuse for the transfer job.
  --job-metadata=JOB_METADATA
                        transfer job metadata.
  --file-metadata=FILE_METADATA
                        file metadata.
  --file-size=FILE_SIZE
                        file size (in Bytes)
  -g GRIDFTP_PARAMS, --gparam=GRIDFTP_PARAMS
                        GridFTP parameters.
  -t DESTINATION_TOKEN, --dest-token=DESTINATION_TOKEN
                        the destination space token or its description.
  -S SOURCE_TOKEN, --source-token=SOURCE_TOKEN
                        the source space token or its description.
  -K COMPARE_CHECKSUM, --compare-checksum=COMPARE_CHECKSUM
                        compare checksums between source and destination.
  --copy-pin-lifetime=PIN_LIFETIME
                        pin lifetime of the copy in seconds.
  --bring-online=BRING_ONLINE
                        bring online timeout in seconds.
  --fail-nearline       fail the transfer is the file is nearline.
  --dry-run             do not send anything, just print the JSON message.
  -f BULK_FILE, --file=BULK_FILE
                        Name of configuration file
  --retry=RETRY         Number of retries. If 0, the server default will be
                        used.If negative, there will be no retries.
  -m, --multi-hop        submit a multihop transfer.
```

If can be used in two manners:

#### One line submissions
This mode only allows to submit one pair (source and destination) each time
```
$ fts-rest-transfer-submit -s https://fts3-devel.cern.ch:8446 gsiftp://source.host/file gsiftp://destination.host/file
Job successfully submitted.
Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a
```

#### Bulk submissions
This mode allows to submit several transfers at once, grouped in a single job.
Please, mind that some options will be ignored in this case: file metadata, file size and checksum.
They would have to be configured per pair in the bulk file.

```
$ fts-rest-transfer-submit -s https://fts3-devel.cern.ch:8446 -f bulk.json
Job successfully submitted.
Job id: 9fee8c1e-c46d-11e3-8299-02163e00a17a
```

The expected format is similar as the one expected by the gSOAP-based fts-transfer-submit:

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
      "filesize": 2048
    }
  ]
}
```

The example above represents one single job with two transfers: one from `gsiftp://source.host/file` to `gsiftp://destination.host/file` and another from `gsiftp://source.host/file2` to `gsiftp://destination.host/file2`.

But you can do [more complex things](bulk.md) with this format!

*Hint*: Try --dry-run to see what would be sent to the server

### fts-rest-whoami
This command exists for convenience. It can be used to check, as the name suggests, who are we for the server.

```
$ fts-rest-whoami -s https://fts3-pilot.cern.ch:8446
User DN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=saketag/CN=678984/CN=Alejandro Alvarez Ayllon
VO: dteam
VO: dteam/cern
Delegation id: 9a4257f435fa2010
```
