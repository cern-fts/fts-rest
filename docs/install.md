Installation
============
If you are performing the installation on the same machine where FTS3 is running, these steps should be enough:

```
yum install fts-rest
service httpd restart
```

If you are going to connect to an Oracle database, you will need to install cx_oracle as well.

$ yum install cx_oracle
If you are installing in a different host, the steps are the same, but you will need to copy the FTS3 configuration file to the new host (since it is used by the rest front-end) and make sure you have installed the proper certificates under /etc/grid-security/certificates.

If you have enabled SELinux, for convenience you can install fts-rest-selinux, which contains the rules needed to have REST working (i.e. allow Apache to connect to the database, allow Apache to bind to 8446)

```
yum install fts-rest-selinux
```

If you are installing in a separate machine, remember to install the CA Certificates (`lcg-CA`) and `fetch-crl` first!

```
yum install lcg-CA fetch-crl
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
    "nil"
  ]
}
```
