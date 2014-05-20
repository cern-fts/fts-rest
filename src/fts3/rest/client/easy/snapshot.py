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


def get_snapshot(context, vo=None, source=None, destination=None):
    """
    Get a snapshot of the server

    Args:
        context: fts3.rest.client.context.Context instance
        vo:      Filter by vo. Can be left empty.
        source:  Filter by source SE. Can be left empty
        destination: Filter by destination SE. Can be left empty.

    Returns:
        Decoded JSON message returned by the server (server snapshot)
    """
    inquirer = Inquirer(context)
    return inquirer.get_snapshot(vo, source, destination)
