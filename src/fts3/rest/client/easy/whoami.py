#   Copyright notice:
#   Copyright CERN, 2014.
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

from fts3.rest.client import Inquirer


def whoami(context):
    """
    Queries the server to see how does it see us

    Args:
        context: fts3.rest.client.context.Context instance

    Returns:
        Decoded JSON message returned by the server with a representation of
        the user credentials (as set in context)
    """
    inquirer = Inquirer(context)
    return inquirer.whoami()
