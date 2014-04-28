from fts3.rest.client import Inquirer


def whoami(context):
    """
    Queries the server to see how does it see us

    Args:
        context: fts3.rest.client.context.Context instance

    Returns:
        The JSON message returned by the server with a representation of
        the user credentials (as set in context)
    """
    inquirer = Inquirer(context)
    return inquirer.whoami()
