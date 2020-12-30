Easy Bindings
==============

This subdirectory contains documentation about the provided Easy bindings.
The directory [examples](examples/) contains a set of example Python programs showing
practical uses of the bindings.

The API
-------
For using the Easy bindings, you need to import `fts3.rest.client.easy`, althought
for convenience it can be renamed as something else

```python
import fts3.rest.client.easy as fts3
```

In the following code snippets, an import as above is assumed.

### Exceptions

#### FTS3ClientException
Base class for all other exceptions.

#### BadEndpoint
Can not contact the given endpoint.

### Unauthorized
The user is not allowed to perform the operation.

#### Client error
The client tried to perform an invaild action (i.e. bad submission).

#### NotFound
The resource has not been found.

#### NeedDelegation
The server needs new delegated credentials.

#### FailedDependency
Some step required to succeed a request failed, so the whole request was canceled. i.e. requesting adding voms
extensions.

#### Server error
Server side error (i.e. internal server error)

#### TryAgain
The server could not fulfill the request now, but it may be able to do so later on.

### Context
In order to be able to do any operation, some state about the user credentials and remote endpoint need to be
kept.
That's the purpose of a Context.

```python
context = fts3.Context(endpoint, ucert, ukey, verify=True)
```

The endpoint to use corresponds to the FTS instance REST server and it must have the following format:

`https://<host>:<port>` 

Example: https://fts3.cern.ch:8446

If you are using a proxy certificate, you can either specify only user_certificate, or point both parameters
to the proxy.

The user_certificate and user_key parameters can be safely omitted, and the program will use 
the values defined in the `X509_USER_PROXY` or `X509_USER_CERT + X509_USER_KEY` environment variables.

If verify is False, the server certificate will not be verified.

Additionally, the `Context` object provides a method `get_endpoint_info()` to retrieve information
about the endpoint, after it has passed validation. This method returns a dictionary
with relevant information about the endpoint:
- url: the endpoint URL string
- delegation: `{major, minor, patch}` delegation version dictionary
- core: `{major, minor, patch}` FTS server version dictionary
- api: `{major, minor, patch}` REST API version dictionary
- schema: `{major, minor, patch}` schema version dictionary

Note: the same info can be obtained via a GET request 
to the `https://<host>:<port>/` address of the FTS REST endpoint

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
fts3.list_jobs(context, user_dn=None, vo=None)
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

### get_jobs_statuses
Get the status of a list of jobs

#### Args:
* **context**    fts3.rest.client.context.Context instance
* **job_ids**    A list of job IDs
* **list_files** If True, the status of each individual file will be queried

#### Returns:
Deserialized JSON message returned by the server containing a list of jobs plus optionally a list of the following fields for each transfer part of the job:
file_state, dest_surl, finish_time, start_time, reason, source_surl, file_metadata

#### Example:
```python
fts3.get_jobs_statuses(context, ['e360232c-7ba6-11e9-aea1-02163e00a077', 'e3941092-7ba6-11e9-8851-02163e00a077', 'e3b1d898-7ba6-11e9-8851-02163e00a077'], list_files=True)
```

```json
[
  {
    'cred_id': 'bfd3b0c180c099ea',
    'user_dn': '/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=amanzi/CN=683749/CN=Andrea Manzi',
    'job_type': 'N',
    'retry': -1,
    'job_id': 'e360232c-7ba6-11e9-aea1-02163e00a077',
    'cancel_job': False,
    'job_state': 'SUBMITTED',
    'submit_host': 'fts3devel02.cern.ch',
    'priority': 3,
    'source_space_token': '',
    'max_time_in_queue': None,
    'job_metadata': {
      'test': 'test_multiple_jobs',
      'label': 'fts3-tests'
    },
    'source_se': None,
    'files': [
      {
        'dest_surl': 'mock://test.cern.ch/ttqv/pryb/nnvw?size_post=1048576&time=2',
        'finish_time': None,
        'start_time': None,
        'file_metadata': None,
        'reason': None,
        'source_surl': 'mock://somewhere.uk/qtgc/mxar/aohc?size=1048576',
        'file_state': 'SUBMITTED'
      },
      {
        'dest_surl': 'mock://test.cern.ch/swnx/jznu/laso?size_post=1048576&time=2',
        'finish_time': None,
        'start_time': None,
        'file_metadata': None,
        'reason': None,
        'source_surl': 'mock://aplace.es/vgcl/cpwh/umfo?size=1048576',
        'file_state': 'SUBMITTED'
      },
      {
        'dest_surl': 'mock://test2.cern.ch/kzqa/pvhf/jmto?size_post=1048576&time=2',
        'finish_time': None,
        'start_time': None,
        'file_metadata': None,
        'reason': None,
        'source_surl': 'mock://test2.cern.ch/yasr/anan/zhbz?size=1048576',
        'file_state': 'SUBMITTED'
      }
    ],
    'http_status': '200 Ok',
    'bring_online': -1,
    'reason': None,
    'space_token': '',
    'submit_time': '2019-05-21T09:00:32',
    'retry_delay': 0,
    'dest_se': None,
    'internal_job_params': 'nostreams:1',
    'vo_name': 'dteam',
    'copy_pin_lifetime': -1,
    'verify_checksum': 'n',
    'job_finished': None,
    'overwrite_flag': False
  },
  {
    'cred_id': 'bfd3b0c180c099ea',
    'user_dn': '/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=amanzi/CN=683749/CN=Andrea Manzi',
    'job_type': 'N',
    'retry': -1,
    'job_id': 'e3941092-7ba6-11e9-8851-02163e00a077',
    'cancel_job': False,
    'job_state': 'SUBMITTED',
    'submit_host': 'fts3devel02.cern.ch',
    'priority': 3,
    'source_space_token': '',
    'max_time_in_queue': None,
    'job_metadata': {
      'test': 'test_multiple_jobs',
      'label': 'fts3-tests'
    },
    'source_se': None,
    'files': [
      {
        'dest_surl': 'mock://test2.cern.ch/plym/iotw/awln?size_post=1048576&time=2',
        'finish_time': None,
        'start_time': None,
        'file_metadata': None,
        'reason': None,
        'source_surl': 'mock://aplace.es/dlgj/tvlr/kyqh?size=1048576',
        'file_state': 'SUBMITTED'
      },
      {
        'dest_surl': 'mock://test.cern.ch/zjtl/tuyd/wsrm?size_post=1048576&time=2',
        'finish_time': None,
        'start_time': None,
        'file_metadata': None,
        'reason': None,
        'source_surl': 'mock://somewhere.uk/ktmp/wmly/pjrv?size=1048576',
        'file_state': 'SUBMITTED'
      },
      {
        'dest_surl': 'mock://somewhere.uk/yzau/bhzw/ggdp?size_post=1048576&time=2',
        'finish_time': None,
        'start_time': None,
        'file_metadata': None,
        'reason': None,
        'source_surl': 'mock://aplace.es/mwrb/eoiy/rvjm?size=1048576',
        'file_state': 'SUBMITTED'
      }
    ],
    'http_status': '200 Ok',
    'bring_online': -1,
    'reason': None,
    'space_token': '',
    'submit_time': '2019-05-21T09:00:32',
    'retry_delay': 0,
    'dest_se': None,
    'internal_job_params': 'nostreams:1',
    'vo_name': 'dteam',
    'copy_pin_lifetime': -1,
    'verify_checksum': 'n',
    'job_finished': None,
    'overwrite_flag': False
  },
  {
    'cred_id': 'bfd3b0c180c099ea',
    'user_dn': '/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=amanzi/CN=683749/CN=Andrea Manzi',
    'job_type': 'N',
    'retry': -1,
    'job_id': 'e3b1d898-7ba6-11e9-8851-02163e00a077',
    'cancel_job': False,
    'job_state': 'SUBMITTED',
    'submit_host': 'fts3devel02.cern.ch',
    'priority': 3,
    'source_space_token': '',
    'max_time_in_queue': None,
    'job_metadata': {
      'test': 'test_multiple_jobs',
      'label': 'fts3-tests'
    },
    'source_se': None,
    'files': [
      {
        'dest_surl': 'mock://somewhere.uk/zpun/fbmb/jvln?size_post=1048576&time=2',
        'finish_time': None,
        'start_time': None,
        'file_metadata': None,
        'reason': None,
        'source_surl': 'mock://aplace.es/tpfb/uoin/ipmb?size=1048576',
        'file_state': 'SUBMITTED'
      },
      {
        'dest_surl': 'mock://test2.cern.ch/qqxk/cjge/ysdf?size_post=1048576&time=2',
        'finish_time': None,
        'start_time': None,
        'file_metadata': None,
        'reason': None,
        'source_surl': 'mock://test2.cern.ch/vrmj/rlnk/yxmx?size=1048576',
        'file_state': 'SUBMITTED'
      },
      {
        'dest_surl': 'mock://test2.cern.ch/dqmq/yrvi/liqz?size_post=1048576&time=2',
        'finish_time': None,
        'start_time': None,
        'file_metadata': None,
        'reason': None,
        'source_surl': 'mock://somewhere.uk/jiyx/nxml/mzzc?size=1048576',
        'file_state': 'SUBMITTED'
      }
    ],
    'http_status': '200 Ok',
    'bring_online': -1,
    'reason': None,
    'space_token': '',
    'submit_time': '2019-05-21T09:00:32',
    'retry_delay': 0,
    'dest_se': None,
    'internal_job_params': 'nostreams:1',
    'vo_name': 'dteam',
    'copy_pin_lifetime': -1,
    'verify_checksum': 'n',
    'job_finished': None,
    'overwrite_flag': False
  }
]
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


### ban_se / unban_se
Ban and unban a storage element.

#### ban_se
* **context** fts3.rest.client.context.Context instance
* **storage** The storage to ban
* **status**  The status of the banning: cancel or wait (leave queued jobs for some time)
* **timeout** The wait timeout in seconds (0 means leave the queued jobs until they are done)
* **allow_submit** If True, submissions will be accepted. Only meaningful if status=active

Returns a list of job ids affected by the banning.

#### unban_se
* **context** fts3.rest.client.context.Context instance
* **storage** The storage to unban

Returns nothing.

#### Example
```python
affected_jobs = fts3.ban_se(context, 'gsiftp://example.com', status='wait', timeout=3600, allow_submit=False)
for job_id in affected_jobs:
  print job_id
fts3.unban_se(context, 'gsiftp://example.com')
```

### ban_dn / unban_dn
Ban and unban a user.

#### ban_dn
* **context** fts3.rest.client.context.Context instance
* **dn** The user to ban

Returns a list of job ids affected by the banning.

#### unban_dn
* **context** fts3.rest.client.context.Context instance
* **dn** The user to unban

#### Example
```python
affected_jobs = fts3.ban_dn(context, '/DC=cern/DC=ch/OU=....')
for job_id in affected_jobs:
  print job_id
fts3.unban_dn(context, '/DC=cern/DC=ch/OU=....')
```

Returns nothing.
