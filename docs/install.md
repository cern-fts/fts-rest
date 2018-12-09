Installation
============
If you are performing the installation on the same machine where FTS3 is running, these steps should be enough:

```
yum install fts-rest
service httpd restart
```

To connect to a MySQL database, you will need to install MySQL-python

```
yum install MySQL-python
```

If you are installing in a different host, the steps are the same, but you will need to copy the FTS3 configuration file to the new host (since it is used by the rest front-end) and make sure you have installed the proper certificates under /etc/grid-security/certificates.

If you have enabled SELinux, for convenience you can install fts-rest-selinux, which contains the rules needed to have REST working (i.e. allow Apache to connect to the database, allow Apache to bind to 8446)

```
yum install fts-rest-selinux
```

If you are installing in a separate machine, remember to install the CA Certificates (`ca-policy-egi-core`) and `fetch-crl` first!

```
yum install ca-policy-egi-core fetch-crl
fetch-crl -v
```

Configuration
=============
If the REST interface is installed in an FTS3 host, it will load automatically its configuration for `/etc/fts3/fts3config`, so generally there is no need to do anything special.

If is is installed in a separated machine, you have two choices:

1. Copy `/etc/fts3/fts3config` from a FTS3 machine (recommended)
1. Manually adjust `/etc/fts3/fts3rest.ini`, uncommenting and setting properly the parameter [`sqlalchemy.url`](http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html#database-urls)

That configuration file can also be used to [tune the logging](http://pylonsbook.com/en/1.1/logging.html#introducing-logging-configuration)

Is it up?
=========
You can check the service is up and running just opening with your browser <https://yourhost:8446/whoami>. If everything is properly set, you will see something like

```json
{
  "delegation_id": "123456789abcdef", 
  "dn": [
    "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=12345/CN=Alejandro Alvarez Ayllon"
  ], 
  "level": {
    "config": "all", 
    "transfer": "vo"
  }, 
  "roles": [], 
  "user_dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=12345/CN=Alejandro Alvarez Ayllon", 
  "voms_cred": [], 
  "vos": [
    "AlejandroAlvarezAyllon@cern.ch"
  ]
}
```

Optional components
===================

There are two optional components that are shipped in differen packages, since most FTS3 instances will not likely be interested in them. Making them two separate packages instead of just configuration options allows to run the service without even having the code installed.

## fts-rest-cloud-storage
This package adds support for non-grid storage integration. For the moment being, just Dropbox is supported.
Installing this rpm will add support for the OAuth negotiation required to get read and write authorization
to the user's folders.
This functionallity is required by WebFTS.

## fts-rest-oauth2
Installing the package will enable the FTS3 server to act as a OAuth2 provider. This is, external third-party
applications can be developed so they use the FTS3 REST API in name of a user that grant them access.
This allows the development of additional tools that use FTS3 as their workhorse, without worrying with credential
delegation, proxy support (the built-in one can be used instead), etc.

