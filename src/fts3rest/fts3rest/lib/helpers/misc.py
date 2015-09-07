import json
import urllib
from fts3rest.lib.http_exceptions import *


def timedelta_to_seconds(td):
    """
    Returns timedelta td total number of seconds
    """
    return (td.microseconds + ((td.seconds + (td.days * 24 * 3600)) * 10**6)) / float(10**6)


def average(iterable, start=None, transform=None):
    """
    Returns the average, or None if there are no elements
    """
    if len(iterable):
        if start is not None:
            addition = sum(iterable, start)
        else:
            addition = sum(iterable)
        if transform:
            addition = transform(addition)
        return addition / float(len(iterable))
    else:
        return None


def get_input_as_dict(request, from_query=False):
    """
    Return a valid dictionary from the request imput
    """
    if from_query:
        input_dict = request.params
    elif request.content_type == 'application/json' or request.method == 'PUT':
        try:
            input_dict = json.loads(request.body)
        except Exception:
            raise HTTPBadRequest('Badly formatted JSON request')
    elif request.content_type.startswith('application/x-www-form-urlencoded'):
        input_dict = dict(request.params)
    elif request.content_type == 'application/json, application/x-www-form-urlencoded':
        input_dict = json.loads(urllib.unquote_plus(request.body))
    else:
        raise HTTPBadRequest('Expecting application/json or application/x-www-form-urlencoded')

    if not hasattr(input_dict, '__getitem__') or not hasattr(input_dict, 'get'):
        raise HTTPBadRequest('Expecting a dictionary')
    return input_dict
