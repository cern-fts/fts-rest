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
The usage documentation is inside the [cli](cli/) subdirectory.

Bulk submission
---------------
You can also check everything you can do with the [bulk format](bulk.md).

*Hint*: Try --dry-run to see what would be sent to the server
