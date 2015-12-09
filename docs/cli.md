FTS3 RESTful CLI
================

Installation
------------
### EPEL
You can install the stable clients from EPEL repositories, or the release candidate from our continuous build repository.

```ini
[fts3-prod-el6]
name=FTS3 Continuous Build Repository (Production)
baseurl=http://grid-deployment.web.cern.ch/grid-deployment/dms/fts3/repos/el6/$basearch
gpgcheck=0
enabled=1
protect=0
```

The package needed is ```fts-rest-cli```

### Checking out the code
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

### Using [pip](https://pypi.python.org/pypi/pip)
Starting with fts-rest 3.2.28 we provide a setup.py script that allows easy installation using pip in a virtual environment.

```bash
virtualenv fts-rest
cd fts-rest/
. ./bin/activate
pip install "git+https://github.com/cern-it-sdc-id/fts3-rest.git"
fts-rest-whoami -s "https://fts3-devel.cern.ch:8446"
User DN: /DC=ch/DC=cern/OU=Organic Units/OU=Users/CN=aalvarez/CN=678984/CN=Alejandro Alvarez Ayllon
VO: dteam
Delegation id: xxxxxxxxxxxxxxxx
```

Note that some native packages will be required (libcurl, libcurl development, swig), and in EL6 some manual
tinkering is required: see the comments in [setupy.py](../setup.py).

Of course, you can get the code from a branch or a tag if you wish. Just check [pip's documentation](http://pip.readthedocs.org/en/latest/reference/pip_install.html#git).


Usage
-----
The usage documentation is inside the [cli](cli/README.md) subdirectory.

Bulk submission
---------------
You can also check everything you can do with the [bulk format](bulk.md).

*Hint*: Try --dry-run to see what would be sent to the server
