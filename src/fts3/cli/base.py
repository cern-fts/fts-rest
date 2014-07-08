#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
#
#   See www.eu-emi.eu for details on the copyright holders
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from ConfigParser import SafeConfigParser
from optparse import OptionParser
import logging
import os

from fts3.rest.client import Context


CONFIG_FILENAMES = [
    '/etc/fts3/fts3client.cfg',
    os.path.expanduser('~/.fts3client.cfg')
]

CONFIG_DEFAULTSECTION = 'Main'
CONFIG_DEFAULTS = {
    'verbose': 'false',
    'endpoint': 'None',
    'json': 'false',
    'ukey': 'None',
    'ucert': 'None'
}


class Base(object):

    def __init__(self, extra_args=None):
        self.logger = logging.getLogger('fts3')

        # Common CLI options
        usage = None
        if extra_args:
            usage = "usage: %prog [options] " + extra_args

        config = SafeConfigParser(defaults=CONFIG_DEFAULTS)

        section = CONFIG_DEFAULTSECTION
        config.read(CONFIG_FILENAMES)

        # manually set the section in edge cases
        if not config.has_section('Main'):
            section = 'DEFAULT'

        # manually get values for which we need to support None
        opt_endpoint = config.get(section, 'endpoint')
        if opt_endpoint == 'None':
            opt_endpoint = None
        opt_ukey = config.get(section, 'ukey')
        if opt_ukey == 'None':
            opt_ukey = None
        opt_ucert = config.get(section, 'ucert')
        if opt_ucert == 'None':
            opt_ucert = None

        self.opt_parser = OptionParser(usage=usage)

        self.opt_parser.add_option('-v', '--verbose', dest='verbose', action='store_true',
                                   help='verbose output.', default=config.getboolean(section, 'verbose'))
        self.opt_parser.add_option('-s', '--endpoint', dest='endpoint',
                                   help='FTS3 REST endpoint.', default=opt_endpoint)
        self.opt_parser.add_option('-j', '--json', dest='json', action='store_true',
                                   help='print the output in JSON format.',
                                   default=config.getboolean(section, 'json'))
        self.opt_parser.add_option('--key', dest='ukey',
                                   help='the user certificate private key.', default=opt_ukey)
        self.opt_parser.add_option('--cert', dest='ucert',
                                   help='the user certificate.', default=opt_ucert)
        self.opt_parser.add_option('--insecure', dest='verify', default=True, action='store_false',
                                   help='do not validate the server certificate')

    def _create_context(self):
        return Context(self.options.endpoint, ukey=self.options.ukey, ucert=self.options.ucert, verify=self.options.verify)

