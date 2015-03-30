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

def _json_type_name(type):
    if not type:
        return None
    elif isinstance(type, str):
        return type
    else:
        name = type.__name__
        if name == 'str':
            name = 'string'
        elif name == 'bool':
            name = 'boolean'
        return name


def query_arg(name, description, type=str, required=False):
    """
    Decorates a function with a set of arguments accepted through query
    arguments.

    Args:
        arg_name: The argument name
        description: A human readable description
        type: A Python type. str by default
        required: A boolean specifying if it is required or not
    """
    def query_arg_inner(function):
        if not hasattr(function, 'doc_query'):
            setattr(function, 'doc_query', [])
        function.doc_query.append((name, description, _json_type_name(type), required))
        return function
    return query_arg_inner


def input(description, type=None, required=True):
    """
    Decorates a function with its accepted input parameter
    (i.e. the body of a PUT)

    Args:
        description: A human readable description
        type: The type of the body
        required: A boolean spec
    """
    def input_body_inner(function):
        function.doc_input = (description, _json_type_name(type), required)
        return function
    return input_body_inner


def response(code, description):
    """
    Decorates a function with a set of possible HTTP response codes that
    it can return.

    Args:
        code: The HTTP code (i.e 404)
        description: A human readable description
    """
    def response_inner(function):
        if not hasattr(function, 'doc_responses'):
            setattr(function, 'doc_responses', [])
        function.doc_responses.append((code, description))
        return function
    return response_inner


def return_type(type=None, array_of=None):
    """
    Decorates a function with its return type.

    Args:
        type: A Python type that can be returned
        array_of: If the type if an array, the contained items in the array

    Notes:
        Either type or array_of must be specified, but at least one!
    """
    assert (type or array_of) and not (type and array_of)
    def return_type_inner(function):
        if array_of:
            function.doc_return_type = 'array'
            function.doc_return_item_type = _json_type_name(array_of)
        else:
            function.doc_return_type = _json_type_name(type)
        return function
    return return_type_inner
