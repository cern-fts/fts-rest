import os
from distutils.core import setup


setup(
    name='fts3',
    version='3.2.28',
    description='FTS3 Python Libraries',
    author='FTS3 Developers',
    author_email='fts-devel@cern.ch',
    url='http://fts3-service.web.cern.ch/',
    license='Apache 2',
    packages=['fts3', 'fts3.model', 'fts3.rest', 'fts3.rest.client', 'fts3.rest.client.easy'],
    package_dir={'fts3': os.path.join(os.path.dirname(__file__), 'src', 'fts3')}
)
