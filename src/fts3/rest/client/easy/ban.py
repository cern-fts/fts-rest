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

from fts3.rest.client import Ban


def ban_se(context, storage, status='cancel', timeout=0, allow_submit=False):
    """
    Ban a storage element

    Args:
        context: fts3.rest.client.context.Context instance
        storage: The storage to ban
        status:  The status of the banning: cancel or wait (leave queued jobs for some time)
        timeout: The wait timeout (0 means leave the queued jobs until they are done)
        allow_submit: If True, submissions will be accepted. Only meaningful if status=active

    Returns:
        List of job ids affected by the banning
    """
    ban = Ban(context)
    return ban.ban_se(storage, status, timeout, allow_submit)

def ban_dn(context, dn):
    """
    Ban a user

    Args:
        context: fts3.rest.client.context.Context instance
        dn:      The dn of the user to be banned

    Returns:
        List of job ids affected by the banning
    """
    ban = Ban(context)
    return ban.ban_dn(dn)

def unban_se(context, storage):
    """
    Unban a storage element

    Args:
        context: fts3.rest.client.context.Context instance
        storage: The storage to unban

    Returns:
        Nothing
    """
    ban = Ban(context)
    return ban.unban_se(storage)

def unban_dn(context, dn):
    """
    Unban a user

    Args:
        context: fts3.rest.client.context.Context instance
        dn:      The dn of the user to be unbanned

    Returns:
        Nothing
    """
    ban = Ban(context)
    ban.unban_dn(dn)
