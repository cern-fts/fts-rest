/usr/bin/python2.7 /opt/pycharm-community-2018.1/helpers/pydev/pydevd.py --multiproc --qt-support=auto --client 127.0.0.1 --port 33255 --file /home/aris/projects/fts-rest/docs/generate-api-md.py
pydev debugger: process 24104 is connecting

Connected to pydev debugger (build 181.4203.547)
Using SQLAlchemy 1.2.7
Found controller banning
Recurse for controllers into /home/aris/projects/fts-rest/src/fts3rest/fts3rest/controllers/config
Found controller config/audit
Found controller config/authz
Found controller config/se
Found controller config/cloud
Found controller config/links
Found controller config/activities
Found controller config/global
Found controller config/drain
Found controller config/shares
Found controller cloudStorage
Found controller files
Found controller error
Found controller api
No module named CSdropbox
Found controller datamanagement
Could not get controller CSInterface
Could not get controller CSdropbox
Found controller autocomplete
Found controller archive
Found controller delegation
Found controller optimizer
Found controller jobs
Found controller oauth2
Found controller serverstatus
config not found in controllers
content not found in controllers
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
#### GET /autocomplete/dn
Autocomplete for users' dn

##### Query arguments

|Name|Type  |Required|Description        |
|----|------|--------|-------------------|
|term|string|False   |Beginning of the DN|

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

#### GET /autocomplete/source
Autocomplete source SE

##### Query arguments

|Name|Type  |Required|Description                    |
|----|------|--------|-------------------------------|
|term|string|False   |Beginning of the source storage|

#### GET /autocomplete/destination
Autocomplete destination SE

##### Query arguments

|Name|Type  |Required|Description                         |
|----|------|--------|------------------------------------|
|term|string|False   |Beginning of the destination storage|

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

### Activity shares configuration
#### GET /config/activity_shares
Get all activity shares

##### Responses

|Code|Description                                     |
|----|------------------------------------------------|
|403 |The user is not allowed to see the configuration|

#### POST /config/activity_shares
Set a new/modify an activity share

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|
|400 |Malformed activity share request                   |

#### GET /config/activity_shares/{vo_name}
Get activity shares for a given VO

##### Path arguments

|Name   |Type  |
|-------|------|
|vo_name|string|

##### Responses

|Code|Description                                     |
|----|------------------------------------------------|
|403 |The user is not allowed to see the configuration|

#### DELETE /config/activity_shares/{vo_name}
Delete an existing activity share

##### Path arguments

|Name   |Type  |
|-------|------|
|vo_name|string|

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

### Config audit
#### GET /config/audit
Returns the last 100 entries of the config audit tables

##### Returns
Array of [ConfigAudit](#configaudit)

### Static authorizations
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

### Configuration of cloud storages
#### GET /config/cloud_storage
Get a list of cloud storages registered

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

#### POST /config/cloud_storage
Add or modify a cloud storage entry

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

#### DELETE /config/cloud_storage/{storage_name}/{id}
Delete credentials for a given user/vo

##### Path arguments

|Name        |Type  |
|------------|------|
|storage_name|string|
|id          |string|

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

#### GET /config/cloud_storage/{storage_name}
Get a list of users registered for a given storage name

##### Path arguments

|Name        |Type  |
|------------|------|
|storage_name|string|

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

#### DELETE /config/cloud_storage/{storage_name}
Remove a registered cloud storage

##### Path arguments

|Name        |Type  |
|------------|------|
|storage_name|string|

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

#### POST /config/cloud_storage/{storage_name}
Add a user or a VO credentials to the storage

##### Path arguments

|Name        |Type  |
|------------|------|
|storage_name|string|

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to modify the configuration|

### Drain operations
#### POST /config/drain
Set the drain status of a server

##### Responses

|Code|Description                                        |
|----|---------------------------------------------------|
|403 |The user is not allowed to change the configuration|
|400 |Bad request. Invalid host or invalid drain value   |

### Server-wide configuration
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

### Link configuration
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

### Grid storage configuration
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

### VO Share configuration
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

### Data management operations
#### POST /dm/unlink
Remove a remote file

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

#### POST /dm/rename
Stat a remote file

##### Query arguments

|Name|Type  |Required|Description  |
|----|------|--------|-------------|
|new |string|True    |New SURL name|
|old |string|True    |Old SURL name|

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

### Operations on Files
#### GET /files
Get a list of active jobs, or those that match the filter requirements

##### Returns
Array of [File](#file)

##### Query arguments

|Name       |Type  |Required|Description                                                         |
|-----------|------|--------|--------------------------------------------------------------------|
|time_window|string|False   |For terminal states, limit results to hours[:minutes] into the past |
|limit      |string|False   |Limit the number of results                                         |
|dest_surl  |string|False   |Destination SURL                                                    |
|dest_se    |string|False   |Destination storage element                                         |
|source_se  |string|False   |Source storage element                                              |
|state_in   |string|False   |Comma separated list of job states to filter. ACTIVE only by default|
|vo_name    |string|False   |Filter by VO                                                        |

##### Responses

|Code|Description                      |
|----|---------------------------------|
|400 |DN and delegation ID do not match|
|403 |Operation forbidden              |

#### GET /files
Get a list of active jobs, or those that match the filter requirements

##### Returns
Array of [File](#file)

##### Query arguments

|Name       |Type  |Required|Description                                                         |
|-----------|------|--------|--------------------------------------------------------------------|
|time_window|string|False   |For terminal states, limit results to hours[:minutes] into the past |
|limit      |string|False   |Limit the number of results                                         |
|dest_surl  |string|False   |Destination SURL                                                    |
|dest_se    |string|False   |Destination storage element                                         |
|source_se  |string|False   |Source storage element                                              |
|state_in   |string|False   |Comma separated list of job states to filter. ACTIVE only by default|
|vo_name    |string|False   |Filter by VO                                                        |

##### Responses

|Code|Description                      |
|----|---------------------------------|
|400 |DN and delegation ID do not match|
|403 |Operation forbidden              |

### Operations on jobs and transfers
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

#### DELETE /jobs/{job_id}/files/{file_ids}
Cancel individual files - comma separated for multiple - within a job

##### Returns
File final states (array if multiple files were given)

##### Path arguments

|Name    |Type  |
|--------|------|
|job_id  |string|
|file_ids|string|

##### Responses

|Code|Description                            |
|----|---------------------------------------|
|404 |The job doesn't exist                  |
|403 |The user doesn't have enough privileges|

#### GET /jobs/{job_id}/dm
Get the data management tasks within a job

##### Returns
Array of [DataManagement](#datamanagement)

##### Path arguments

|Name  |Type  |
|------|------|
|job_id|string|

##### Responses

|Code|Description                            |
|----|---------------------------------------|
|404 |The job doesn't exist                  |
|403 |The user doesn't have enough privileges|

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

#### POST /jobs/{job_id_list}
Modify a job, or set of jobs

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
|fields     |string|False   |Return only a subset of the fields                                  |
|time_window|string|False   |For terminal states, limit results to hours[:minutes] into the past |
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
|fields     |string|False   |Return only a subset of the fields                                  |
|time_window|string|False   |For terminal states, limit results to hours[:minutes] into the past |
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

|Code|Description                                                                                |
|----|-------------------------------------------------------------------------------------------|
|419 |The credentials need to be re-delegated                                                    |
|409 |The request could not be completed due to a conflict with the current state of the resource|
|403 |The user doesn't have enough permissions to submit                                         |
|400 |The submission request could not be understood                                             |

#### POST /jobs
Submits a new job

##### Returns
{"job_id": <job id>}

##### Notes
It returns the information about the new submitted job. To know the format for the<br/>submission, /api-docs/schema/submit gives the expected format encoded as a JSON-schema.<br/>It can be used to validate (i.e in Python, jsonschema.validate)

##### Expected request body
Submission description (SubmitSchema)

##### Responses

|Code|Description                                                                                |
|----|-------------------------------------------------------------------------------------------|
|419 |The credentials need to be re-delegated                                                    |
|409 |The request could not be completed due to a conflict with the current state of the resource|
|403 |The user doesn't have enough permissions to submit                                         |
|400 |The submission request could not be understood                                             |

#### DELETE /jobs/all
Cancel all files

##### Returns
File final states (array if multiple files were given)

##### Responses

|Code|Description                            |
|----|---------------------------------------|
|404 |The job doesn't exist                  |
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

#### DELETE /jobs/vo/{vo_name}
Cancel all files by the given vo_name

##### Returns
Affected transfers, dm and jobs count

##### Path arguments

|Name   |Type  |
|-------|------|
|vo_name|string|

##### Responses

|Code|Description                                                                                |
|----|-------------------------------------------------------------------------------------------|
|409 |The request could not be completed due to a conflict with the current state of the resource|
|404 |The job doesn't exist                                                                      |
|403 |The user doesn't have enough privileges                                                    |

### OAuth2.0 controller
#### GET /oauth2/token
Get an access token

##### Returns
A JSON with the access_token, token_type, expires_in and refresh_token

##### Query arguments

|Name         |Type  |Required|Description                                               |
|-------------|------|--------|----------------------------------------------------------|
|scope        |string|True    |Comma-separated set of scopes                             |
|redirect_uri |string|True    |One of the registered urls                                |
|refresh_token|string|False   |Refresh token obtained when the initial token was obtained|
|code         |string|False   |Code passed from FTS3 via redirection                     |
|client_secret|string|True    |Application secret key                                    |
|client_id    |string|True    |Application client id                                     |
|grant_type   |string|False   |Must be 'authorization_code' or 'refresh_token'           |

##### Responses

|Code|Description                    |
|----|-------------------------------|
|400 |Missing field, or invalid value|

#### POST /oauth2/token
Get an access token

##### Returns
A JSON with the access_token, token_type, expires_in and refresh_token

##### Query arguments

|Name         |Type  |Required|Description                                               |
|-------------|------|--------|----------------------------------------------------------|
|scope        |string|True    |Comma-separated set of scopes                             |
|redirect_uri |string|True    |One of the registered urls                                |
|refresh_token|string|False   |Refresh token obtained when the initial token was obtained|
|code         |string|False   |Code passed from FTS3 via redirection                     |
|client_secret|string|True    |Application secret key                                    |
|client_id    |string|True    |Application client id                                     |
|grant_type   |string|False   |Must be 'authorization_code' or 'refresh_token'           |

##### Responses

|Code|Description                    |
|----|-------------------------------|
|400 |Missing field, or invalid value|

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
Perform the OAuth2 authorization step. The user must be redirected here.

##### Returns
Confirmation form or error message

##### Query arguments

|Name         |Type  |Required|Description                  |
|-------------|------|--------|-----------------------------|
|scope        |string|True    |Comma-separated set of scopes|
|redirect_uri |string|True    |One of the registered urls   |
|client_id    |string|True    |Application client id        |
|response_type|string|True    |Must be 'code'               |

##### Responses

|Code|Description                  |
|----|-----------------------------|
|400 |Missing or invalid parameters|

#### POST /oauth2/authorize
Triggered by user action. Confirm, or reject, access.

##### Responses

|Code|Description                                           |
|----|------------------------------------------------------|
|303 |Redirect to the redirect_uri passed by the application|

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
#### GET /optimizer/current
Returns the current number of actives and streams

##### Returns
Array of [Optimizer](#optimizer)

#### POST /optimizer/current
Set the number of actives and streams

##### Responses

|Code|Description                         |
|----|------------------------------------|
|400 |Invalid values passed in the request|

#### GET /optimizer/evolution
Returns the optimizer evolution

##### Returns
Array of [OptimizerEvolution](#optimizerevolution)

#### GET /optimizer
Indicates if the optimizer is enabled in the server

##### Returns
boolean

### Server general status
#### GET /status/hosts
What are the hosts doing

Models
------
### Optimizer

|Field    |Type    |
|---------|--------|
|dest_se  |string  |
|datetime |dateTime|
|nostreams|integer |
|active   |integer |
|ema      |float   |
|source_se|string  |

### OptimizerEvolution

|Field          |Type    |
|---------------|--------|
|ema            |float   |
|success        |float   |
|actual_active  |integer |
|diff           |integer |
|datetime       |dateTime|
|queue_size     |integer |
|throughput     |float   |
|rationale      |string  |
|filesize_stddev|float   |
|active         |integer |
|dest_se        |string  |
|source_se      |string  |
|filesize_avg   |float   |

### FileRetryLog

|Field   |Type    |
|--------|--------|
|reason  |string  |
|attempt |integer |
|file_id |integer |
|datetime|dateTime|

### OAuth2Application

|Field        |Type  |
|-------------|------|
|website      |string|
|name         |string|
|redirect_to  |string|
|client_id    |string|
|scope        |string|
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

|Field              |Type    |
|-------------------|--------|
|cred_id            |string  |
|user_dn            |string  |
|retry              |integer |
|job_id             |string  |
|cancel_job         |boolean |
|job_state          |string  |
|submit_host        |string  |
|priority           |integer |
|source_space_token |string  |
|reuse_job          |boolean |
|job_metadata       |string  |
|source_se          |string  |
|max_time_in_queue  |integer |
|files              |array   |
|job_params         |string  |
|bring_online       |integer |
|reason             |string  |
|space_token        |string  |
|submit_time        |dateTime|
|dest_se            |string  |
|internal_job_params|string  |
|vo_name            |string  |
|copy_pin_lifetime  |integer |
|verify_checksum    |string  |
|job_finished       |dateTime|
|overwrite_flag     |boolean |

### Job

|Field              |Type    |
|-------------------|--------|
|cred_id            |string  |
|user_dn            |string  |
|job_type           |string  |
|retry              |integer |
|job_id             |string  |
|cancel_job         |boolean |
|job_state          |string  |
|submit_host        |string  |
|priority           |integer |
|source_space_token |string  |
|max_time_in_queue  |integer |
|job_metadata       |string  |
|source_se          |string  |
|files              |array   |
|dm                 |array   |
|bring_online       |integer |
|reason             |string  |
|space_token        |string  |
|submit_time        |dateTime|
|retry_delay        |integer |
|dest_se            |string  |
|internal_job_params|string  |
|vo_name            |string  |
|copy_pin_lifetime  |integer |
|verify_checksum    |string  |
|job_finished       |dateTime|
|overwrite_flag     |boolean |

### File

|Field               |Type    |
|--------------------|--------|
|transfer_host       |string  |
|tx_duration         |float   |
|pid                 |integer |
|hashed_id           |integer |
|log_debug           |integer |
|retry               |integer |
|job_id              |string  |
|staging_start       |dateTime|
|filesize            |integer |
|source_se           |string  |
|file_state          |string  |
|start_time          |dateTime|
|internal_file_params|string  |
|reason              |string  |
|file_id             |string  |
|staging_host        |string  |
|dest_surl           |string  |
|source_surl         |string  |
|bringonline_token   |string  |
|selection_strategy  |string  |
|retries             |array   |
|dest_se             |string  |
|file_index          |integer |
|finish_time         |dateTime|
|checksum            |string  |
|staging_finished    |dateTime|
|user_filesize       |integer |
|file_metadata       |string  |
|throughput          |float   |
|activity            |string  |
|log_file            |string  |
|vo_name             |string  |
|recoverable         |string  |

### ConfigAudit

|Field   |Type    |
|--------|--------|
|dn      |string  |
|action  |string  |
|config  |string  |
|datetime|dateTime|

### ArchivedFile

|Field               |Type    |
|--------------------|--------|
|tx_duration         |float   |
|pid                 |integer |
|dest_surl           |string  |
|retry               |integer |
|job_id              |string  |
|job_finished        |dateTime|
|staging_start       |dateTime|
|filesize            |integer |
|source_se           |string  |
|file_state          |string  |
|start_time          |dateTime|
|file_index          |integer |
|reason              |string  |
|file_id             |string  |
|staging_host        |string  |
|user_filesize       |integer |
|source_surl         |string  |
|bringonline_token   |string  |
|selection_strategy  |string  |
|dest_se             |string  |
|internal_file_params|string  |
|finish_time         |dateTime|
|checksum            |string  |
|staging_finished    |dateTime|
|file_metadata       |string  |
|transferhost        |string  |
|throughput          |float   |
|current_failures    |integer |


Process finished with exit code 0
