Installation
============
If you are performing the installation on the same machine where FTS3 is running:

1. Install all the build requires packages located in fts-rest/packaging/rpm/fts-spec
2. Install also MySQL-python
3. create the following directory and provide the following permissions: 
```
mkdir /var/log/fts3rest
chown -R fts3:fts3 /var/log/fts3rest
```

4. Copy the following files in the proper locations:
```
cp fts3rest.ini /etc/fts3/
cp fts3rest.wsgi /usr/libexec/fts3/ to be read by apache
cp fts3rest.conf /etc/httpd/conf.d/
```

5. In fts3rest.wsgi comment out the sys.path.

6. In fts3rest.conf, indicate the python-path parameter where your source is located.
```
WSGIDaemonProcess fts3rest python-path=/your-path/fts-rest/src and keep the rest of parameters
```
Then give the corresponding permissions in order to be accesible by apache

```
chmod 0755 /your-path
```

7. Disable SELinux in /etc/sysconfig/selinux and reboot and check the status 
```
sestatus
```

8. stop iptables and ip6tables and firewall

```
service iptables stop
service ip6tables stop
service firewalld stop
```

9. Make sure that DEBUG is false in fts3rest.ini

10. Restart apache
```
systemctl restart httpd.service
```

```
yum install fts-rest
service httpd restart
```

11. If you are installing in a different host, the steps are the same, but you will need to copy the FTS3 configuration file to the new host (since it is used by the rest front-end) and make sure you have installed the proper certificates under /etc/grid-security/certificates.

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
{"dn": ["/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=ftssuite/CN=737188/CN=Robot: fts3 testsuite"], "vos_id": ["363cb54e-b3c2-51f1-8d97-82464d0b1546"], "roles": [], "delegation_id": "bb33e23d77bcf67f", "user_dn": "/DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=ftssuite/CN=737188/CN=Robot: fts3 testsuite", "level": {"transfer": "vo"}, "is_root": false, "base_id": "01874efb-4735-4595-bc9c-591aef8240c9", "vos": ["ftssuite@cern.ch"], "voms_cred": [], "method": "certificate"}
```
