from datetime import timedelta
from fts3.rest.client import Delegator


def delegate(context, lifetime=timedelta(hours=7), force=False):
    """
    Delegates the credentials

    Args:
        context:  fts3.rest.client.context.Context instance
        lifetime: The delegation life time
        force:    If true, credentials will be re-delegated regardless
                  of the remaining life of the previous delegation

    Returns:
        The delegation ID
    """
    delegator = Delegator(context)
    return delegator.delegate(lifetime, force)
