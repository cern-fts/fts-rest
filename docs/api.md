API
===
This document has been generated automatically

### /whoami
#### GET /whoami
Returns the active credentials of the user

### API documentation
#### GET /api-docs
Auto-generated API documentation

##### Notes
Compatible with Swagger-UI

#### GET /api-docs/schema/submit
Json-schema for the submission operation

##### Notes
This can be used to validate the submission. For instance, in Python,<br/>jsonschema.validate

#### GET /api-docs/{resource}
Auto-generated API documentation for a specific resource

##### Path arguments

|Name    |Type  |
|--------|------|
|resource|string|

##### Responses

|Code|Description                  |
|----|-----------------------------|
|404 |The resource can not be found|

### Banning API
#### POST /ban/se
Ban a storage element. Returns affected jobs ids.

##### Returns
Array of string

##### Query arguments

|Name        |Type  |Required|Description                                                                                      |
|------------|------|--------|-------------------------------------------------------------------------------------------------|
|timeout     |string|False   |If status==wait, timeout for the queued jobs. 0 = will not timeout (default)                     |
|status      |string|False   |What to do with the queued jobs: cancel (default, cancel immediately) or wait(wait for some time)|
|allow_submit|string|False   |If true, transfers will not run, but submissions will be accepted                                |
|vo_name     |string|False   |Limit the banning to a given VO                                                                  |
|storage     |string|True    |Storage to ban                                                                                   |

##### Responses

|Code|Description                                                   |
|----|--------------------------------------------------------------|
|413 |The user is not allowed to change the configuration           |
|400 |storage is missing, or any of the others have an invalid value|

#### DELETE /ban/se
Unban a storage element

##### Query arguments

|Name   |Type  |Required|Description         |
|-------|------|--------|--------------------|
|storage|string|True    |The storage to unban|

##### Responses

|Code|Description                                             |
|----|--------------------------------------------------------|
|403 |The user is not allowed to perform configuration actions|
|400 |storage is empty or missing                             |
|204 |Success                                                 |

#### POST /ban/dn
Ban a user

##### Query arguments

|Name   |Type  |Required|Description   |
|-------|------|--------|--------------|
|user_dn|string|True    |User DN to ban|

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|413 |The user is not allowed to change the configuration|
|409 |The user tried to ban (her|his)self                |
|400 |dn is missing                                      |

#### DELETE /ban/dn
Unban a user

##### Query arguments

|Name   |Type  |Required|Description     |
|-------|------|--------|----------------|
|user_dn|string|True    |User DN to unban|

##### Responses

|Code|Description                                             |
|----|--------------------------------------------------------|
|403 |The user is not allowed to perform configuration actions|
|400 |user_dn is empty or missing                             |
|204 |Success                                                 |

### Data management operations
#### GET /dm/list
List the content of a remote directory

##### Query arguments

|Name|Type  |Required|Description|
|----|------|--------|-----------|
|surl|string|True    |Remote SURL|

##### Responses

|Code|Description                                          |
|----|-----------------------------------------------------|
|500 |Internal error                                       |
|503 |Try again later                                      |
|419 |The credentials need to be re-delegated              |
|404 |The SURL does not exist                              |
|403 |Permission denied                                    |
|400 |Protocol not supported OR the SURL is not a directory|

#### GET /dm/stat
Stat a remote file

##### Query arguments

|Name|Type  |Required|Description|
|----|------|--------|-----------|
|surl|string|True    |Remote SURL|

##### Responses

|Code|Description                                          |
|----|-----------------------------------------------------|
|500 |Internal error                                       |
|503 |Try again later                                      |
|419 |The credentials need to be re-delegated              |
|404 |The SURL does not exist                              |
|403 |Permission denied                                    |
|400 |Protocol not supported OR the SURL is not a directory|

### Operations on archived jobs and transfers
#### GET /archive/{job_id}/{field}
Get a specific field from the job identified by id

##### Path arguments

|Name  |Type  |
|------|------|
|job_id|string|
|field |string|

##### Responses

|Code|Description                       |
|----|----------------------------------|
|404 |The job or the field doesn't exist|

#### GET /archive/{job_id}
Get the job with the given ID

##### Returns
[ArchivedJob](#archivedjob)

##### Path arguments

|Name  |Type  |
|------|------|
|job_id|string|

##### Responses

|Code|Description          |
|----|---------------------|
|404 |The job doesn't exist|

#### GET /archive
Just give the operations that can be performed

#### GET /archive
Just give the operations that can be performed

### Operations on jobs and transfers
#### GET /jobs
Get a list of active jobs, or those that match the filter requirements

##### Returns
Array of [Job](#job)

##### Query arguments

|Name     |Type  |Required|Description                                                         |
|---------|------|--------|--------------------------------------------------------------------|
|dest_se  |string|False   |Destination storage element                                         |
|source_se|string|False   |Source storage element                                              |
|state_in |string|False   |Comma separated list of job states to filter. ACTIVE only by default|
|dlg_id   |string|False   |Filter by delegation ID                                             |
|vo_name  |string|False   |Filter by VO                                                        |
|user_dn  |string|False   |Filter by user DN                                                   |

##### Responses

|Code|Description                      |
|----|---------------------------------|
|400 |DN and delegation ID do not match|
|403 |Operation forbidden              |

#### GET /jobs
Get a list of active jobs, or those that match the filter requirements

##### Returns
Array of [Job](#job)

##### Query arguments

|Name     |Type  |Required|Description                                                         |
|---------|------|--------|--------------------------------------------------------------------|
|dest_se  |string|False   |Destination storage element                                         |
|source_se|string|False   |Source storage element                                              |
|state_in |string|False   |Comma separated list of job states to filter. ACTIVE only by default|
|dlg_id   |string|False   |Filter by delegation ID                                             |
|vo_name  |string|False   |Filter by VO                                                        |
|user_dn  |string|False   |Filter by user DN                                                   |

##### Responses

|Code|Description                      |
|----|---------------------------------|
|400 |DN and delegation ID do not match|
|403 |Operation forbidden              |

#### PUT /jobs
Submits a new job

##### Returns
{"job_id": <job id>}

##### Notes
It returns the information about the new submitted job. To know the format for the<br/>submission, /api-docs/schema/submit gives the expected format encoded as a JSON-schema.<br/>It can be used to validate (i.e in Python, jsonschema.validate)

##### Expected request body
Submission description (SubmitSchema)

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|419 |The credentials need to be re-delegated           |
|403 |The user doesn't have enough permissions to submit|
|400 |The submission request could not be understood    |

#### POST /jobs
Submits a new job

##### Returns
{"job_id": <job id>}

##### Notes
It returns the information about the new submitted job. To know the format for the<br/>submission, /api-docs/schema/submit gives the expected format encoded as a JSON-schema.<br/>It can be used to validate (i.e in Python, jsonschema.validate)

##### Expected request body
Submission description (SubmitSchema)

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|419 |The credentials need to be re-delegated           |
|403 |The user doesn't have enough permissions to submit|
|400 |The submission request could not be understood    |

#### GET /jobs/{job_id}
Get the job with the given ID

##### Returns
[Job](#job)

##### Path arguments

|Name  |Type  |
|------|------|
|job_id|string|

##### Responses

|Code|Description                            |
|----|---------------------------------------|
|413 |The user doesn't have enough privileges|
|404 |The job doesn't exist                  |

#### DELETE /jobs/{job_id}
Cancel the given job

##### Returns
[Job](#job)

##### Notes
Returns the canceled job with its current status. CANCELED if it was canceled,<br/>its final status otherwise

##### Path arguments

|Name  |Type  |
|------|------|
|job_id|string|

##### Responses

|Code|Description                            |
|----|---------------------------------------|
|413 |The user doesn't have enough privileges|
|404 |The job doesn't exist                  |

#### GET /jobs/{job_id}/{field}
Get a specific field from the job identified by id

##### Path arguments

|Name  |Type  |
|------|------|
|job_id|string|
|field |string|

##### Responses

|Code|Description                            |
|----|---------------------------------------|
|413 |The user doesn't have enough privileges|
|404 |The job or the field doesn't exist     |

### Operations on the config audit
#### GET /config/audit
Returns the last 100 entries of the config audit tables

##### Returns
Array of [ConfigAudit](#configaudit)

### Operations to perform the delegation of credentials
#### POST /delegation/{dlg_id}/voms
Generate VOMS extensions for the delegated proxy

##### Notes
The input must be a json-serialized list of strings, where each strings<br/>is a voms command (i.e. ["dteam", "dteam:/dteam/Role=lcgadmin"])

##### Path arguments

|Name  |Type  |
|------|------|
|dlg_id|string|

##### Expected request body
List of voms commands (array)

##### Responses

|Code|Description                                            |
|----|-------------------------------------------------------|
|203 |The obtention of the VOMS extensions succeeded         |
|424 |The obtention of the VOMS extensions failed            |
|400 |Could not understand the request                       |
|403 |The requested delegation ID does not belong to the user|

#### GET /delegation/{dlg_id}
Get the termination time of the current delegated credential, if any

##### Returns
dateTime

##### Path arguments

|Name  |Type  |
|------|------|
|dlg_id|string|

#### DELETE /delegation/{dlg_id}
Delete the delegated credentials from the database

##### Path arguments

|Name  |Type  |
|------|------|
|dlg_id|string|

##### Responses

|Code|Description                                            |
|----|-------------------------------------------------------|
|204 |The credentials were deleted successfully              |
|404 |The credentials do not exist                           |
|403 |The requested delegation ID does not belong to the user|

#### GET /delegation/{dlg_id}/request
First step of the delegation process: get a certificate request

##### Returns
PEM encoded certificate request

##### Notes
The returned certificate request must be signed with the user's original<br/>credentials.

##### Path arguments

|Name  |Type  |
|------|------|
|dlg_id|string|

##### Responses

|Code|Description                                            |
|----|-------------------------------------------------------|
|200 |The request was generated succesfully                  |
|403 |The requested delegation ID does not belong to the user|

#### PUT /delegation/{dlg_id}/credential
Second step of the delegation process: put the generated certificate

##### Notes
The certificate being PUT will have to pass the following validation:<br/>- There is a previous certificate request done<br/>- The certificate subject matches the certificate issuer + '/CN=Proxy'<br/>- The certificate modulus matches the stored private key modulus

##### Path arguments

|Name  |Type  |
|------|------|
|dlg_id|string|

##### Expected request body
Signed certificate (PEM encoded certificate)

##### Responses

|Code|Description                                            |
|----|-------------------------------------------------------|
|201 |The proxy was stored successfully                      |
|400 |The proxy failed the validation process                |
|403 |The requested delegation ID does not belong to the user|

#### POST /delegation/{dlg_id}/credential
Second step of the delegation process: put the generated certificate

##### Notes
The certificate being PUT will have to pass the following validation:<br/>- There is a previous certificate request done<br/>- The certificate subject matches the certificate issuer + '/CN=Proxy'<br/>- The certificate modulus matches the stored private key modulus

##### Path arguments

|Name  |Type  |
|------|------|
|dlg_id|string|

##### Expected request body
Signed certificate (PEM encoded certificate)

##### Responses

|Code|Description                                            |
|----|-------------------------------------------------------|
|201 |The proxy was stored successfully                      |
|400 |The proxy failed the validation process                |
|403 |The requested delegation ID does not belong to the user|

### Optimizer logging tables
#### GET /optimizer/evolution
Returns the optimizer evolution

##### Returns
Array of [OptimizerEvolution](#optimizerevolution)

#### GET /optimizer
Indicates if the optimizer is enabled in the server

##### Returns
boolean

### Snapshot API
#### GET /snapshot
Get the current status of the server

##### Query arguments

|Name     |Type  |Required|Description             |
|---------|------|--------|------------------------|
|dest_se  |string|False   |Filter by destination SE|
|source_se|string|False   |Filter by source SE     |
|vo_name  |string|False   |Filter by VO name       |

Models
------
### ArchivedFile

|Field               |Type    |
|--------------------|--------|
|symbolicname        |string  |
|tx_duration         |float   |
|pid                 |integer |
|num_failures        |integer |
|checksum            |string  |
|retry               |integer |
|job_id              |string  |
|job_finished        |dateTime|
|staging_start       |dateTime|
|filesize            |float   |
|source_se           |string  |
|file_state          |string  |
|start_time          |dateTime|
|internal_file_params|string  |
|reason              |string  |
|file_id             |integer |
|error_phase         |string  |
|source_surl         |string  |
|bringonline_token   |string  |
|selection_strategy  |string  |
|dest_surl           |string  |
|file_index          |integer |
|finish_time         |dateTime|
|dest_se             |string  |
|staging_finished    |dateTime|
|user_filesize       |float   |
|file_metadata       |string  |
|error_scope         |string  |
|transferhost        |string  |
|throughput          |float   |
|current_failures    |integer |
|agent_dn            |string  |
|reason_class        |string  |

### OptimizerEvolution

|Field     |Type    |
|----------|--------|
|dest_se   |string  |
|branch    |integer |
|success   |float   |
|datetime  |dateTime|
|throughput|float   |
|nostreams |integer |
|timeout   |integer |
|active    |integer |
|source_se |string  |

### FileRetryLog

|Field   |Type    |
|--------|--------|
|reason  |string  |
|attempt |integer |
|file_id |integer |
|datetime|dateTime|

### ArchivedJob

|Field                   |Type    |
|------------------------|--------|
|cred_id                 |string  |
|user_dn                 |string  |
|retry                   |integer |
|job_id                  |string  |
|cancel_job              |boolean |
|job_state               |string  |
|submit_host             |string  |
|priority                |integer |
|source_space_token      |string  |
|reuse_job               |boolean |
|job_metadata            |string  |
|source_se               |string  |
|user_cred               |string  |
|max_time_in_queue       |integer |
|files                   |array   |
|source_token_description|string  |
|job_params              |string  |
|bring_online            |integer |
|reason                  |string  |
|space_token             |string  |
|submit_time             |dateTime|
|dest_se                 |string  |
|internal_job_params     |string  |
|finish_time             |dateTime|
|verify_checksum         |boolean |
|overwrite_flag          |boolean |
|copy_pin_lifetime       |integer |
|agent_dn                |string  |
|job_finished            |dateTime|
|vo_name                 |string  |

### Job

|Field                   |Type    |
|------------------------|--------|
|cred_id                 |string  |
|user_dn                 |string  |
|retry                   |integer |
|job_id                  |string  |
|cancel_job              |boolean |
|job_state               |string  |
|submit_host             |string  |
|priority                |integer |
|source_space_token      |string  |
|reuse_job               |string  |
|job_metadata            |string  |
|source_se               |string  |
|user_cred               |string  |
|max_time_in_queue       |integer |
|files                   |array   |
|source_token_description|string  |
|job_params              |string  |
|bring_online            |integer |
|reason                  |string  |
|space_token             |string  |
|submit_time             |dateTime|
|dest_se                 |string  |
|internal_job_params     |string  |
|finish_time             |dateTime|
|verify_checksum         |string  |
|overwrite_flag          |boolean |
|copy_pin_lifetime       |integer |
|agent_dn                |string  |
|job_finished            |dateTime|
|vo_name                 |string  |

### File

|Field               |Type    |
|--------------------|--------|
|symbolicname        |string  |
|tx_duration         |float   |
|pid                 |integer |
|hashed_id           |integer |
|num_failures        |integer |
|log_debug           |integer |
|retry               |integer |
|job_id              |string  |
|job_finished        |dateTime|
|wait_timestamp      |dateTime|
|staging_start       |dateTime|
|filesize            |float   |
|source_se           |string  |
|file_state          |string  |
|start_time          |dateTime|
|activity            |string  |
|dest_se             |string  |
|file_index          |integer |
|reason              |string  |
|wait_timeout        |integer |
|file_id             |integer |
|error_phase         |string  |
|source_surl         |string  |
|bringonline_token   |string  |
|selection_strategy  |string  |
|retries             |array   |
|dest_surl           |string  |
|internal_file_params|string  |
|finish_time         |dateTime|
|checksum            |string  |
|staging_finished    |dateTime|
|user_filesize       |float   |
|file_metadata       |string  |
|error_scope         |string  |
|transferhost        |string  |
|throughput          |float   |
|current_failures    |integer |
|log_file            |string  |
|agent_dn            |string  |
|reason_class        |string  |
|vo_name             |string  |

### ConfigAudit

|Field   |Type    |
|--------|--------|
|dn      |string  |
|action  |string  |
|config  |string  |
|datetime|dateTime|

