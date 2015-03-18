API
===
This document has been generated automatically

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

### Autocomplete API
#### GET /autocomplete/source
Autocomplete source SE

##### Query arguments

|Name|Type  |Required|Description                    |
|----|------|--------|-------------------------------|
|term|string|False   |Beginning of the source storage|

#### GET /autocomplete/vo
Autocomplete VO

##### Query arguments

|Name|Type  |Required|Description        |
|----|------|--------|-------------------|
|term|string|False   |Beginning of the VO|

#### GET /autocomplete/storage
Autocomplete a storage, regardless of it being source or destination

##### Query arguments

|Name|Type  |Required|Description                         |
|----|------|--------|------------------------------------|
|term|string|False   |Beginning of the destination storage|

#### GET /autocomplete/destination
Autocomplete destination SE

##### Query arguments

|Name|Type  |Required|Description                         |
|----|------|--------|------------------------------------|
|term|string|False   |Beginning of the destination storage|

#### GET /autocomplete/dn
Autocomplete for users' dn

##### Query arguments

|Name|Type  |Required|Description        |
|----|------|--------|-------------------|
|term|string|False   |Beginning of the DN|

#### GET /autocomplete/groupname
Autocomplete group names

##### Query arguments

|Name|Type  |Required|Description                |
|----|------|--------|---------------------------|
|term|string|False   |Beginning of the group name|

### Banning API
#### POST /ban/se
Ban a storage element. Returns affected jobs ids.

##### Returns
Array of string

##### Query arguments

|Name        |Type  |Required|Description                                                                                      |
|------------|------|--------|-------------------------------------------------------------------------------------------------|
|message     |string|False   |Explanatory message if desired                                                                   |
|timeout     |string|False   |If status==wait, timeout for the queued jobs. 0 = will not timeout (default)                     |
|status      |string|False   |What to do with the queued jobs: cancel (default, cancel immediately) or wait(wait for some time)|
|allow_submit|string|False   |If true, transfers will not run, but submissions will be accepted                                |
|vo_name     |string|False   |Limit the banning to a given VO                                                                  |
|storage     |string|True    |Storage to ban                                                                                   |

##### Responses

|Code|Description                                                   |
|----|--------------------------------------------------------------|
|403 |The user is not allowed to change the configuration           |
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

#### GET /ban/se
List banned storage elements

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to check the configuration|

#### POST /ban/dn
Ban a user

##### Query arguments

|Name   |Type  |Required|Description                   |
|-------|------|--------|------------------------------|
|message|string|False   |Explanatory message if desired|
|user_dn|string|True    |User DN to ban                |

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|409 |The user tried to ban (her|his)self                |
|403 |The user is not allowed to change the configuration|
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

#### GET /ban/dn
List banned users

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to check the configuration|

### Cloud storage support
#### GET /cs/remote_content/{service}
Get the content of the given directory

##### Path arguments

|Name   |Type  |
|-------|------|
|service|string|

##### Query arguments

|Name|Type  |Required|Description|
|----|------|--------|-----------|
|surl|string|False   |The folder |

##### Responses

|Code|Description                   |
|----|------------------------------|
|403 |No token for the given storage|

#### GET /cs/access_request/{service}/request
First authorization step: obtain a request token

##### Path arguments

|Name   |Type  |
|-------|------|
|service|string|

##### Responses

|Code|Description          |
|----|---------------------|
|200 |Got the request token|

#### GET /cs/access_request/{service}
Returns the status of the authorization

##### Path arguments

|Name   |Type  |
|-------|------|
|service|string|

##### Responses

|Code|Description                                      |
|----|-------------------------------------------------|
|404 |The user has not registered for the given service|

#### GET /cs/access_request/{service}
Returns the status of the authorization

##### Path arguments

|Name   |Type  |
|-------|------|
|service|string|

##### Responses

|Code|Description                                      |
|----|-------------------------------------------------|
|404 |The user has not registered for the given service|

#### GET /cs/file_urllink/{service}/{path}
Get the final HTTP url from the logical file_path inside the cloud storage

##### Path arguments

|Name   |Type  |
|-------|------|
|service|string|
|path   |string|

##### Responses

|Code|Description                   |
|----|------------------------------|
|403 |No token for the given storage|

#### DELETE /cs/access_grant/{service}
Remove the token associated with the given service

##### Path arguments

|Name   |Type  |
|-------|------|
|service|string|

##### Responses

|Code|Description          |
|----|---------------------|
|404 |No token for the user|
|204 |Token deleted        |

#### GET /cs/access_grant/{service}
Third authorization step: get a valid access token

##### Path arguments

|Name   |Type  |
|-------|------|
|service|string|

##### Responses

|Code|Description                                 |
|----|--------------------------------------------|
|404 |The storage has not been properly configured|
|400 |Previous steps failed or didn' happen       |

#### GET /cs/registered/{service}
Return a boolean indicating if the user has a token registered

##### Returns
boolean

##### Notes
for the given certificate

##### Path arguments

|Name   |Type  |
|-------|------|
|service|string|

### Operations on the config audit
#### POST /config/debug
Sets the debug level status for a storage

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to change the configuration|

#### DELETE /config/debug
Removes a debug entry

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to change the configuration|

#### GET /config/debug
Return the debug settings

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|

#### POST /config/fixed
Fixes the number of actives for a pair

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

#### GET /config/fixed
Gets the fixed pairs

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|

#### GET /config/groups/{group_name}
Get the members of a group

##### Path arguments

|Name      |Type  |
|----------|------|
|group_name|string|

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|404 |The group does not exist                          |
|403 |The user is not allowed to query the configuration|

#### DELETE /config/groups/{group_name}
Delete a member from a group. If the group is left empty, the group will be removed

##### Path arguments

|Name      |Type  |
|----------|------|
|group_name|string|

##### Query arguments

|Name  |Type  |Required|Description                                         |
|------|------|--------|----------------------------------------------------|
|member|string|False   |Storage to remove. All group if left empty or absent|

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|404 |The group or the member does not exist            |
|403 |The user is not allowed to query the configuration|
|204 |Member removed                                    |

#### POST /config/se
Set the configuration parameters for a given SE

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|
|400 |Invalid values passed in the request              |

#### GET /config/se
Get the configurations status for a given SE

##### Query arguments

|Name|Type  |Required|Description    |
|----|------|--------|---------------|
|se  |string|False   |Storage element|

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|

#### DELETE /config/se
Delete the configuration for a given SE

##### Query arguments

|Name|Type  |Required|Description    |
|----|------|--------|---------------|
|se  |string|True    |Storage element|

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

#### POST /config/authorize
Give special access to someone

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

#### GET /config/authorize
List granted accesses

##### Query arguments

|Name     |Type  |Required|Description        |
|---------|------|--------|-------------------|
|operation|string|False   |Filter by operation|
|dn       |string|False   |Filter by DN       |

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|

#### DELETE /config/authorize
Revoke access for a DN for a given operation, or all

##### Query arguments

|Name     |Type  |Required|Description                |
|---------|------|--------|---------------------------|
|operation|string|False   |The operation to be removed|
|dn       |string|True    |The user DN to be removed  |

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

#### GET /config/links/{sym_name}
Get the existing configuration for a given link

##### Path arguments

|Name    |Type  |
|--------|------|
|sym_name|string|

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|404 |The group or the member does not exist            |
|403 |The user is not allowed to query the configuration|

#### DELETE /config/links/{sym_name}
Deletes an existing link configuration

##### Path arguments

|Name    |Type  |
|--------|------|
|sym_name|string|

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|404 |The group or the member does not exist            |
|403 |The user is not allowed to query the configuration|
|204 |Link removed                                      |

#### POST /config/groups
Add a SE to a group

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|
|400 |Invalid values passed in the request              |

#### GET /config/groups
Get a list with all group names

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|

#### GET /config
Entry point. Only makes sense with html

#### POST /config/global
Set the global configuration

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|
|400 |Invalid values passed in the request              |

#### GET /config/global
Get the global configuration

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|
|400 |Invalid values passed in the request              |

#### DELETE /config/global
Delete the global configuration for the given VO

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|
|400 |Invalid values passed in the request              |

#### POST /config/shares
Add or modify a share

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

#### GET /config/shares
List the existing shares

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|

#### DELETE /config/shares
Delete a share

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

#### GET /config/audit
Returns the last 100 entries of the config audit tables

##### Returns
Array of [ConfigAudit](#configaudit)

#### POST /config/drain
Set the drain status of a server

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to change the configuration|
|400 |Bad request. Invalid host or invalid drain value   |

#### POST /config/links
Set the configuration for a given link

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|
|400 |Invalid values passed in the request              |

#### GET /config/links
Get a list of all the links configured

##### Responses

|Code|Description                                       |
|----|--------------------------------------------------|
|403 |The user is not allowed to query the configuration|

### Data management operations
#### POST /dm/unlink
Remove a remote file

##### Responses

|Code|Description                                          |
|----|-----------------------------------------------------|
|500 |Internal error                                       |
|503 |Try again later                                      |
|419 |The credentials need to be re-delegated              |
|404 |The SURL does not exist                              |
|403 |Permission denied                                    |
|400 |Protocol not supported OR the SURL is not a directory|

#### POST /dm/rename
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

#### POST /dm/rmdir
Remove a remote folder

##### Responses

|Code|Description                                          |
|----|-----------------------------------------------------|
|500 |Internal error                                       |
|503 |Try again later                                      |
|419 |The credentials need to be re-delegated              |
|404 |The SURL does not exist                              |
|403 |Permission denied                                    |
|400 |Protocol not supported OR the SURL is not a directory|

#### POST /dm/mkdir
Create a remote file

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

### Operations to perform the delegation of credentials
#### GET /whoami
Returns the active credentials of the user

#### GET /delegation
Render an HTML form to delegate the credentials

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

#### GET /whoami/certificate
Returns the user certificate

### Operations on jobs and transfers
#### DELETE /jobs/{job_id_list}
Cancel the given job

##### Returns
[Job](#job)

##### Notes
Returns the canceled job with its current status. CANCELED if it was canceled,<br/>its final status otherwise

##### Path arguments

|Name       |Type  |
|-----------|------|
|job_id_list|string|

##### Responses

|Code|Description                                          |
|----|-----------------------------------------------------|
|404 |The job doesn't exist                                |
|403 |The user doesn't have enough privileges              |
|207 |For multiple job requests if there has been any error|

#### GET /jobs/{job_list}
Get the job with the given ID

##### Returns
[Job](#job)

##### Path arguments

|Name    |Type  |
|--------|------|
|job_list|string|

##### Query arguments

|Name |Type  |Required|Description                                                  |
|-----|------|--------|-------------------------------------------------------------|
|files|string|False   |Comma separated list of file fields to retrieve in this query|

##### Responses

|Code|Description                            |
|----|---------------------------------------|
|404 |The job doesn't exist                  |
|403 |The user doesn't have enough privileges|
|207 |Some job had an error                  |
|200 |The jobs exist                         |

#### GET /jobs
Get a list of active jobs, or those that match the filter requirements

##### Returns
Array of [Job](#job)

##### Query arguments

|Name       |Type  |Required|Description                                                         |
|-----------|------|--------|--------------------------------------------------------------------|
|time_window|string|False   |For terminal states, limit results to N hours into the past         |
|limit      |string|False   |Limit the number of results                                         |
|dest_se    |string|False   |Destination storage element                                         |
|source_se  |string|False   |Source storage element                                              |
|state_in   |string|False   |Comma separated list of job states to filter. ACTIVE only by default|
|dlg_id     |string|False   |Filter by delegation ID                                             |
|vo_name    |string|False   |Filter by VO                                                        |
|user_dn    |string|False   |Filter by user DN                                                   |

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

|Name       |Type  |Required|Description                                                         |
|-----------|------|--------|--------------------------------------------------------------------|
|time_window|string|False   |For terminal states, limit results to N hours into the past         |
|limit      |string|False   |Limit the number of results                                         |
|dest_se    |string|False   |Destination storage element                                         |
|source_se  |string|False   |Source storage element                                              |
|state_in   |string|False   |Comma separated list of job states to filter. ACTIVE only by default|
|dlg_id     |string|False   |Filter by delegation ID                                             |
|vo_name    |string|False   |Filter by VO                                                        |
|user_dn    |string|False   |Filter by user DN                                                   |

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
|404 |The job or the field doesn't exist     |
|403 |The user doesn't have enough privileges|

#### GET /jobs/{job_id}/files/{file_id}/retries
Get the retries for a given file

##### Path arguments

|Name   |Type  |
|-------|------|
|job_id |string|
|file_id|string|

##### Responses

|Code|Description                            |
|----|---------------------------------------|
|404 |The job or the file don't exist        |
|403 |The user doesn't have enough privileges|

#### GET /jobs/{job_id}/files
Get the files within a job

##### Returns
Array of [File](#file)

##### Path arguments

|Name  |Type  |
|------|------|
|job_id|string|

##### Responses

|Code|Description                            |
|----|---------------------------------------|
|404 |The job doesn't exist                  |
|403 |The user doesn't have enough privileges|

### OAuth2.0 controller
#### GET /oauth2/token
Get an access token

#### POST /oauth2/token
Get an access token

#### GET /oauth2/apps
Returns the list of registered apps

##### Returns
Array of [OAuth2Application](#oauth2application)

#### GET /oauth2/register
Registration form

#### POST /oauth2/register
Register a new third party application

##### Returns
client_id

##### Responses

|Code|Description                                                     |
|----|----------------------------------------------------------------|
|403 |Tried to update an application that does not belong to the user |
|400 |Bad request                                                     |
|303 |Application registered, follow redirection (when html requested)|
|201 |Application registered                                          |

#### GET /oauth2/authorize
Perform OAuth2 authorization step

#### POST /oauth2/authorize
Triggered by user action. Confirm, or reject, access.

#### GET /oauth2/apps/{client_id}
Return information about a given app

##### Returns
[OAuth2Application](#oauth2application)

##### Path arguments

|Name     |Type  |
|---------|------|
|client_id|string|

##### Responses

|Code|Description                                |
|----|-------------------------------------------|
|404 |Application not found                      |
|403 |The application does not belong to the user|

#### POST /oauth2/apps/{client_id}
Update an application

##### Path arguments

|Name     |Type  |
|---------|------|
|client_id|string|

##### Responses

|Code|Description                                |
|----|-------------------------------------------|
|404 |Application not found                      |
|403 |The application does not belong to the user|

#### DELETE /oauth2/apps/{client_id}
Delete an application from the database

##### Path arguments

|Name     |Type  |
|---------|------|
|client_id|string|

##### Responses

|Code|Description                                |
|----|-------------------------------------------|
|404 |Application not found                      |
|403 |The application does not belong to the user|

#### GET /oauth2/revoke/{client_id}
Current user revokes all tokens for a given application

##### Path arguments

|Name     |Type  |
|---------|------|
|client_id|string|

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

### FileRetryLog

|Field   |Type    |
|--------|--------|
|reason  |string  |
|attempt |integer |
|file_id |integer |
|datetime|dateTime|

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

### OAuth2Application

|Field        |Type  |
|-------------|------|
|website      |string|
|name         |string|
|redirect_to  |string|
|client_id    |string|
|owner        |string|
|client_secret|string|
|description  |string|

### DataManagement

|Field          |Type    |
|---------------|--------|
|dm_token       |string  |
|tx_duration    |float   |
|hashed_id      |integer |
|retry          |integer |
|job_id         |string  |
|retry_timestamp|dateTime|
|job_finished   |dateTime|
|wait_timestamp |dateTime|
|source_se      |string  |
|file_state     |string  |
|start_time     |dateTime|
|dest_se        |string  |
|reason         |string  |
|wait_timeout   |integer |
|file_id        |integer |
|user_filesize  |float   |
|source_surl    |string  |
|dest_surl      |string  |
|finish_time    |dateTime|
|checksum       |string  |
|file_metadata  |string  |
|activity       |string  |
|dmHost         |string  |
|vo_name        |string  |

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
|dm                      |array   |
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

