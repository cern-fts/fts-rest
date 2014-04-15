Using the API with curl
=======================

Checking how the server sees us
-------------------------------
`curl --capath /etc/grid-security/certificates -E ~/proxy.pem --cacert ~/proxy.pem https://fts3-pilot.cern.ch:8446/whoami`

```json
{
  "delegation_id": "34644b4229f12f0d", 
  "dn": [
    "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=678984/CN=Alejandro Alvarez Ayllon", 
    "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=678984/CN=Alejandro Alvarez Ayllon/CN=proxy"
  ], 
  "level": {
    "*": "all"
  }, 
  "roles": [], 
  "user_dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=678984/CN=Alejandro Alvarez Ayllon", 
  "voms_cred": [
    "/testers.eu-emi.eu/Role=NULL/Capability=NULL", 
    "/testers.eu-emi.eu/test/Role=NULL/Capability=NULL"
  ], 
  "vos": [
    "testers.eu-emi.eu", 
    "testers.eu-emi.eu/test"
  ]
}
```

Get a list of jobs running
--------------------------
Filtering by atlas

`curl --capath /etc/grid-security/certificates -E ~/proxy.pem --cacert ~/proxy.pem https://fts3-pilot.cern.ch:8446/jobs?vo_name=atlas`

```json
[
  {
    "agent_dn": null, 
    "bring_online": -1, 
    "cancel_job": false, 
    "copy_pin_lifetime": -1, 
    "cred_id": "123456789", 
    "dest_se": "srm://site.pl", 
    "finish_time": null, 
    "internal_job_params": "", 
    "job_finished": null, 
    "job_id": "abcdef-abcde-4638-98a7-123456789", 
    "job_metadata": "", 
    "job_params": "", 
    "job_state": "ACTIVE", 
    "max_time_in_queue": null, 
    "overwrite_flag": true, 
    "priority": 3, 
    "reason": null, 
    "retry": 0, 
    "reuse_job": false, 
    "source_se": "srm://site.es", 
    "source_space_token": "", 
    "source_token_description": null, 
    "space_token": "ATLASDATADISK", 
    "submit_host": "fts105.cern.ch", 
    "submit_time": "2014-04-15T14:02:50", 
    "user_cred": "", 
    "user_dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=ddmadmin/CN=531497/CN=Robot: ATLAS Data Management", 
    "verify_checksum": "r", 
    "vo_name": "atlas"
  }, 
  {
    "agent_dn": null, 
    "bring_online": -1, 
    "cancel_job": false, 
    "copy_pin_lifetime": -1, 
    "cred_id": "123456789", 
    "dest_se": "srm://site.de", 
    "finish_time": null, 
    "internal_job_params": "", 
    "job_finished": null, 
    "job_id": "abcdef-abcd-4b07-8433-987654321", 
    "job_metadata": "", 
    "job_params": "", 
    "job_state": "ACTIVE", 
    "max_time_in_queue": null, 
    "overwrite_flag": true, 
    "priority": 3, 
    "reason": null, 
    "retry": 0, 
    "reuse_job": false, 
    "source_se": "srm://site.org", 
    "source_space_token": "", 
    "source_token_description": null, 
    "space_token": "ATLASDATADISK", 
    "submit_host": "fts104.cern.ch", 
    "submit_time": "2014-04-15T13:59:56", 
    "user_cred": "", 
    "user_dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=ddmadmin/CN=531497/CN=Robot: ATLAS Data Management", 
    "verify_checksum": "r", 
    "vo_name": "atlas"
  }
]
```

Get a given job
---------------
`curl --capath /etc/grid-security/certificates -E ~/proxy.pem --cacert ~/proxy.pem https://fts3-pilot.cern.ch:8446/jobs/a40b82b7-1132-459f-a641-f8b49137a713`
```json
{
  "agent_dn": null, 
  "bring_online": -1, 
  "cancel_job": null, 
  "checksum_method": null, 
  "copy_pin_lifetime": -1, 
  "cred_id": "9e52376e3ab44cf0", 
  "dest_se": "https://lxfsra10a01.cern.ch", 
  "files": [
    {
      "agent_dn": null, 
      "bringonline_token": null, 
      "checksum": null, 
      "current_failures": null, 
      "dest_se": "https://lxfsra10a01.cern.ch", 
      "dest_surl": "https://lxfsra10a01.cern.ch/dpm/cern.ch/home/dteam/copy.9.77", 
      "error_phase": null, 
      "error_scope": null, 
      "file_id": 1062, 
      "file_index": 0, 
      "file_metadata": null, 
      "file_state": "FAILED", 
      "filesize": 19, 
      "finish_time": "2013-03-22T13:37:33", 
      "internal_file_params": "nostreams:1,timeout:5000,buffersize:0", 
      "job_finished": "2013-03-22T13:37:33", 
      "job_id": "a40b82b7-1132-459f-a641-f8b49137a713", 
      "num_failures": null, 
      "pid": 2445, 
      "reason": "[gfalt_copy_file]HEAD failed with code '404'", 
      "reason_class": null, 
      "retry": 0, 
      "selection_strategy": null, 
      "source_se": "https://lxfsra04a04.cern.ch", 
      "source_surl": "https://lxfsra04a04.cern.ch/dpm/cern.ch/home/dteam/vector-sample.txt", 
      "staging_finished": null, 
      "staging_start": null, 
      "start_time": "2013-03-22T13:37:32", 
      "symbolicname": null, 
      "throughput": 0, 
      "transferhost": "fts3src2", 
      "tx_duration": 1, 
      "user_filesize": 0
    }
  ], 
  "finish_time": "2013-03-22T13:37:33", 
  "internal_job_params": null, 
  "job_finished": "2013-03-22T13:37:33", 
  "job_id": "a40b82b7-1132-459f-a641-f8b49137a713", 
  "job_metadata": null, 
  "job_params": null, 
  "job_state": "FAILED", 
  "max_time_in_queue": null, 
  "overwrite_flag": null, 
  "priority": 3, 
  "reason": "One or more files failed. Please have a look at the details for more information", 
  "reuse_job": null, 
  "source_se": "https://lxfsra04a04.cern.ch", 
  "source_space_token": null, 
  "source_token_description": null, 
  "space_token": null, 
  "submit_host": "fts3src2", 
  "submit_time": "2013-03-22T13:35:39", 
  "user_cred": null, 
  "user_dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=msalicho/CN=709008/CN=Michail Salichos", 
  "vo_name": "dteam"
}
```

Cancel a job
------------
`curl --capath /etc/grid-security/certificates -E ~/proxy.pem --cacert ~/proxy.pem https://fts3-pilot.cern.ch:8446/jobs/a40b82b7-1132-459f-a641-f8b49137a713 -X DELETE`

Check the expiration time of our delegated credentials
------------------------------------------------------
`curl --capath /etc/grid-security/certificates -E ~/proxy.pem --cacert ~/proxy.pem https://fts3-pilot.cern.ch:8446/delegation/34644b4229f12f0d`
```json
{
  "termination_time": "2013-03-22T21:54:46"
}
```

Remove delegated credentials
----------------------------
`curl --capath /etc/grid-security/certificates -E ~/proxy.pem --cacert ~/proxy.pem https://fts3-pilot.cern.ch:8446/delegation/34644b4229f12f0d -X DELETE`

Get the submit schema
---------------------
Returns the JSON Schema for the submission message. This can be used by the clients to validate their JSON before actually submitting the transfer.

```python
import jsonschema
import json
import requests

root_ca    = '/etc/grid-security/certificates/CERN-Root.pem'
my_proxy   = '/home/user/proxy.pem'
schema     = json.loads(requests.get('https://fts3-pilot.cern.ch:8446/schema/submit', verify=root_ca, cert=my_proxy).text)
submission = json.loads(open('submit.json').read())
jsonschema.validate(submission, schema)

submission['params']['verify_checksum'] = 1234
jsonschema.validate(submission, schema)
Traceback...
jsonschema.ValidationError: 1234 is not of type [u'boolean', u'null']
```

Here you can see an example of a submission file

```javascript
{
  "files": [
    {
      "sources": ["root://source/file"],     // Array of strings: Source files*
      "destinations": ["root://dest/file"],  // Array of strings: Destination files*
      "metadata": "User defined metadata",   // Any valid json object: User defined metadata
      "filesize": 1024,                      // Integer: Expected file size
      "checksum": 'adler32:1234',            // String: User defined checksum in the form 'algorithm:value'.
                                             //         This will NOT be honored unless verify_checksum is true.
    }
  ], 
  "params": {
    "verify_checksum": true,    // Boolean: If set to true, checksum will be validated.
    "reuse": false,             // Boolean: If set to true, srm sessions will be reused.
    "spacetoken": null,         // String: Destination space token
    "bring_online": null        // Integer: Bring online operation timeout.
    "copy_pin_lifetime": -1,    // Integer: Minimum lifetime when bring online is used. -1 means no bring online.
    "job_metadata": null,       // Any valid json object: User defined metadata
    "source_spacetoken": null,  // String: Source space token.
    "overwrite": false,         // Boolean: Overwrite the destination file.
    "gridftp": null             // Not used yet. It can be left empty.
  }
}
```

Please, note that comments are not supported in JSON. They are just shown here as a help.
If you want to check other more complex submission modes, you can check the reference page for the [bulk submission format](bulk.md).
