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

from datetime import timedelta
from fts3.rest.client import Delegator


def delegate(context, lifetime=timedelta(hours=7), force=False, delegate_when_lifetime_lt=timedelta(hours=2)):
    """
    Delegates the credentials

    Args:
        context:  fts3.rest.client.context.Context instance
        lifetime: The delegation life time
        force:    If true, credentials will be re-delegated regardless
                  of the remaining life of the previous delegation
        delegate_when_lifetime_lt: If the remaining lifetime on the delegated proxy is less than this interval,
                  do a new delegation

    Returns:
        The delegation ID
    """
    delegator = Delegator(context)
    return delegator.delegate(lifetime, force, delegate_when_lifetime_lt)
