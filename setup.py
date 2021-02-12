import os
import platform
import tempfile
import sys
from distutils.core import setup
from glob import glob

del os.link
# On Scientific Linux, installing M2Crypto may give this error
# "This openssl-devel package does not work your architecture?"
# To work around that, set the environment variable
# export SWIG_FEATURES="-includeall -D__`uname -m`__"
# and do the installation from here
def apply_m2crypto_workaround():
    print "Applying workaround for M2Crypto in RedHat"
    os.environ['SWIG_FEATURES'] = "-includeall -D__%s__" % platform.machine()
    tmp_dir = tempfile.mkdtemp()
    os.system('pip install --build %s  M2Crypto>=0.16' % tmp_dir)


# On EL6, you will probably have trouble installing pycurl due to this:
# http://stackoverflow.com/questions/7391638/pycurl-installed-but-not-found
# If so, modify pycurl's setup.py and replace --static-libs with --libs
#
# pip uninstall pycurl
# pip install pycurl==7.19.0 --no-clean --no-install
# sed -i s/--static-libs/--libs/g build/pycurl/setup.py
# pip install build/pycurl
def apply_pycurl_workaround():
    print "Applying workaround for pycurl in EL6"
    tmp_dir = tempfile.mkdtemp()
    is_pycurl_installed = (os.system('pip list | grep pycurl &> /dev/null') == 0)
    if not is_pycurl_installed:
        pythonVersion = sys.version_info[1]
        if pythonVersion == 6:
            os.system('pip install --build %s pycurl%s --no-clean --no-install' % (tmp_dir, pycurl_ver))
        elif pythonVersion == 7:
            os.system('pip download --no-clean --build %s  pycurl%s'%(tmp_dir, pycurl_ver))
        os.system('sed -i s/--static-libs/--libs/g %s/pycurl/setup.py' % tmp_dir)
        os.system('pip install --build %s %s/pycurl' % (tmp_dir, tmp_dir))


# On EL7, you will probably have trouble installing pycurl due to this:
# https://github.com/pycurl/pycurl/issues/526 which has not yet released
# so we need to install a previos version of pycurl with 
# pip install pycurl==7.43.0.1 --global-option="--with-nss
#def apply_pycurl_workaround_on_el7():
#    print "Applying workaround for pycurl in EL7"
#    is_pycurl_installed = (os.system('pip list | grep pycurl &> /dev/null') == 0)
#    if not is_pycurl_installed:
#         os.system('pip install pycurl%s --global-option="--with-nss"' % pycurl_ver)


# Ugly hack to pick a version that compiles in SLC6
pycurl_ver = '==7.19.0'
dist = platform.dist()
if dist[0] in ('redhat', 'centos'):
    os_major = dist[1].split('.')[0]
    if os_major == '6':
        apply_pycurl_workaround()
        apply_m2crypto_workaround()

base_dir = os.path.dirname(__file__)

setup(
    name='fts3-rest',
    version='3.10.1',
    description='FTS3 Python Libraries',
    long_description='FTS3 Python Libraries',
    author='FTS3 Developers',
    author_email='fts-devel@cern.ch',
    url='http://fts.web.cern.ch/',
    download_url='https://gitlab.cern.ch/fts/fts-rest',
    license='Apache 2',
    packages=['fts3', 'fts3.cli', 'fts3.model', 'fts3.util', 'fts3.rest', 'fts3.rest.client', 'fts3.rest.client.easy'],
    package_dir={'fts3': os.path.join(base_dir, 'src', 'fts3')},
    scripts=glob(os.path.join(base_dir, 'src', 'cli', 'fts-*')),
    keywords='fts3, grid, rest api, data management clients',
    platforms=['GNU/Linux'],
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: Apache Software License",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: Unix",
        "Programming Language :: Python"
    ],

    install_requires=['M2Crypto>=0.16', 'pycurl%s' % pycurl_ver, 'requests']
)

# Need to install these first so the dependencies can be built!
#   gcc
#   libcurl-devel
#   libcurl-openssl-devel
#   openssl-devel
#   swig
