DIRAC Bindings
==============

This subdirectory contains documentation about the provided DIRAC bindings.
The directory [examples](examples/) contains a set of example Python programs showing
practical uses of the bindings.

The API
-------
For using the DIRAC bindings, you need to import `fts3.rest.client.dirac_bindings`, althought
for convenience it can be renamed as something else

```python
import fts3.rest.client.dirac_bindings as fts3
```

In the following code snippets, an import as above is assumed.

### Exceptions

#### FTS3ClientException
Base class for all other exceptions

#### BadEndpoint
Can not contact the given endpoint

### Unauthorized
The user is not allowed to perform the operation

#### Client error
The client tried to perform an invaild action (i.e. bad submission)

#### Server error
Server side error (i.e. internal server error)

#### NotFound
The resource has not been found

### Context
In order to be able to do any operation, some state about the user credentials and remote endpoint need to be
kept.
That's the purpose of a Context

```python
context = fts3.Context(endpoint, ucert, ukey)
```

If you are using a proxy certificate, you can either specify only user_certificate, or point both parameters
to the proxy.

user_certificate and user_key can be safely omitted, and the program will use the values
defined in the environment variables `X509_USER_PROXY` or `X509_USER_CERT + X509_USER_KEY`.

### whoami
Queries the server to see how does it see us

#### Args:
* **context** fts3.rest.client.context.Context instance

#### Returns:
Deserialized JSON message returned by the server with a representation of
the user credentials (as set in context)
    
#### Example:
```python
fts3.whoami(context)
```

```json
{
  "dn": [
    "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=678984/CN=Alejandro Alvarez Ayllon", 
    "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=678984/CN=Alejandro Alvarez Ayllon/CN=proxy"
  ], 
  "roles": [
    "lcgadmin"
  ], 
  "level": {
    "transfer": "vo", 
    "config": "all"
  }, 
  "user_dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=678984/CN=Alejandro Alvarez Ayllon", 
  "delegation_id": "7e0863c6cf4e52dd", 
  "vos": [
    "dteam", 
    "dteam/cern"
  ], 
  "voms_cred": [
    "/dteam/Role=lcgadmin/Capability=NULL", 
    "/dteam/Role=NULL/Capability=NULL", 
    "/dteam/cern/Role=NULL/Capability=NULL"
  ]
}
```

### list_jobs
List active jobs. Can filter by user_dn and vo

#### Args:
* **context** fts3.rest.client.context.Context instance
* **user_dn** Filter by user dn. Can be left empty
* **vo**      Filter by vo. Can be left empty

#### Returns:
Deserialized JSON message returned by the server (list of jobs)

#### Example:
```python
fts3.list_jobs(context. user_dn=None, vo=None)
```

```json
[
  {
    "cred_id": "1234", 
    "user_dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/...", 
    "retry": 0, 
    "job_id": "1234-5678-98765",
    "cancel_job": false, 
    "job_finished": null, 
    "submit_host": "fts104.cern.ch", 
    "priority": 3, 
    "source_space_token": "", 
    "max_time_in_queue": null, 
    "job_metadata": "", 
    "source_se": "srm://source.cern.ch",
    "user_cred": "", 
    "reuse_job": false, 
    "source_token_description": null, 
    "job_params": "", 
    "bring_online": -1, 
    "reason": null, 
    "space_token": "", 
    "submit_time": "2014-04-28T13:18:26", 
    "dest_se": "srm://destination.cern.ch",
    "internal_job_params": "", 
    "finish_time": null, 
    "verify_checksum": false, 
    "vo_name": "cms", 
    "copy_pin_lifetime": -1, 
    "agent_dn": null, 
    "job_state": "SUBMITTED", 
    "overwrite_flag": true
  }, 
  {
    "cred_id": "1234", 
    "user_dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/...", 
    "retry": 0, 
    "job_id": "1234-5678-987ab",
    "cancel_job": false, 
    "job_finished": null, 
    "submit_host": "fts102.cern.ch", 
    "priority": 3, 
    "source_space_token": "", 
    "max_time_in_queue": null, 
    "job_metadata": "", 
    "source_se": "gsiftp://source.cern.ch", 
    "user_cred": "", 
    "reuse_job": false, 
    "source_token_description": null, 
    "job_params": "", 
    "bring_online": -1, 
    "reason": null, 
    "space_token": "", 
    "submit_time": "2014-04-28T09:00:17", 
    "dest_se": "srm://destination.cern.ch",
    "internal_job_params": "", 
    "finish_time": null, 
    "verify_checksum": false, 
    "vo_name": "cms", 
    "copy_pin_lifetime": -1, 
    "agent_dn": null, 
    "job_state": "SUBMITTED", 
    "overwrite_flag": true
  }
]
```

### get_job_status
Get a job status

#### Args:
* **context**    fts3.rest.client.context.Context instance
* **job_id**     The job ID
* **list_files** If True, the status of each individual file will be queried

#### Returns:
Deserialized JSON message returned by the server (job, plus optionally list of files)

#### Example:
```python
fts3.get_job_status(context, '1234-5678-abcdef', list_files=False)
```

```json
{
  "cred_id": "0ef8fb17bc42a356", 
  "user_dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=saketag/CN=678984/CN=Alejandro Alvarez Ayllon", 
  "retry": 0, 
  "job_id": "969bc54e-ca78-11e3-a6e2-02163e00a17a", 
  "cancel_job": false, 
  "job_finished": "2014-04-22T23:48:25", 
  "submit_host": "fts106.cern.ch", 
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
  "source_token_description": null, 
  "job_params": "", 
  "bring_online": 120, 
  "reason": "", 
  "space_token": "", 
  "submit_time": "2014-04-22T23:48:22", 
  "dest_se": "srm://hepgrid11.ph.liv.ac.uk", 
  "internal_job_params": null, 
  "finish_time": "2014-04-22T23:48:25", 
  "verify_checksum": false, 
  "vo_name": "dteam", 
  "copy_pin_lifetime": -1, 
  "agent_dn": null, 
  "job_state": "FINISHED", 
  "overwrite_flag": false
}
```

### delegate
Delegates the credentials

#### Args:
* **context**  fts3.rest.client.context.Context instance
* **lifetime** The delegation life time
* **force**    If true, credentials will be re-delegated regardless
         of the remaining life of the previous delegation

#### Returns:
The delegation ID

#### Example
```python
dlg_id = fts3.delegate(context, lifetime=timedelta(hours=48), force=False)
```

### submit
Check the documentation on [submit](submit.md) to see how to build a job and submit it.
