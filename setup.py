import os
import platform
from distutils.core import setup
from glob import glob

# Ugly hack to pick a version that compiles in SLC6
pycurl_ver = '>=7.19'
dist = platform.dist()
if dist[0] == 'redhat':
    major = dist[1].split('.')[0]
    if major == '6':
        pycurl_ver = '==7.19.0'
    elif major == '5':
        pycurl_ver = '==7.15.5'

base_dir = os.path.dirname(__file__)

setup(
    name='fts3',
    version='3.2.28',
    description='FTS3 Python Libraries',
    author='FTS3 Developers',
    author_email='fts-devel@cern.ch',
    url='http://fts3-service.web.cern.ch/',
    license='Apache 2',
    packages=['fts3', 'fts3.cli', 'fts3.model', 'fts3.rest', 'fts3.rest.client', 'fts3.rest.client.easy'],
    package_dir={'fts3': os.path.join(base_dir, 'src', 'fts3')},
    scripts=glob(os.path.join(base_dir, 'src', 'cli', 'fts-*')),

    install_requires=['M2Crypto>=0.16', 'pycurl%s' % pycurl_ver]
)

# Need to install these first so the dependencies can be built!
#   gcc
#   libcurl-devel
#   libcurl-openssl-devel
#   openssl-devel
#   swig
#
# If running Swig you get something like
# "This openssl-devel package does not work your architecture?"
# Do
# export SWIG_FEATURES="-includeall -D__`uname -m`__"
#
# On SL6, you will probably have trouble installing pycurl due to this:
# http://stackoverflow.com/questions/7391638/pycurl-installed-but-not-found
# If so, modify pycurl's setup.py and replace --static-libs with --libs
#
# pip uninstall pycurl
# pip install pycurl==7.19.0 --no-clean --no-install
# sed -i s/--static-libs/--libs/g build/pycurl/setup.py
# pip install build/pycurl
