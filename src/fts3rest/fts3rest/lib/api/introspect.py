#!/usr/bin/env python
import imp
import itertools
import os
import fts3.model
from fts3.model.base import Flag, TernaryFlag, Json
from fts3rest.config import routing
from sqlalchemy import types
from sqlalchemy.orm import Mapper
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.properties import ColumnProperty, RelationProperty
from types import FunctionType


root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
controllers_path = os.path.join(root_path, 'controllers')


def get_column_type_description(sql_type):
    """
    Infers the type from the SQLAlchemy type
    """
    if isinstance(sql_type, types.String) or \
       isinstance(sql_type, Json) or \
       isinstance(sql_type, TernaryFlag) or \
       isinstance(sql_type, types.CLOB):
        return {'type': 'string'}
    elif isinstance(sql_type, types.Integer):
        return {'type': 'integer'}
    elif isinstance(sql_type, types.Float):
        return {'type': 'float'}
    elif isinstance(sql_type, types.DateTime):
        return {'type': 'dateTime'}
    elif isinstance(sql_type, Flag):
        return {'type': 'boolean'}
    return {'type': 'string'}


def get_relation_type_description(prop, model_list):
    """
    Injects into model_list the additional types that may be needed
    """
    if isinstance(prop.argument, Mapper):
        return None
    ref_type = prop.argument().__name__
    model_list.append(ref_type)
    if prop.uselist:
        return {
            'type': 'array',
            'items': {'$ref': ref_type}
        }
    else:
        return {'type': ref_type}


def get_model_fields(model_name, model_list):
    """
    Get a description of the fields of the model 'model_name'
    Injects into model_list the additional types that may be needed
    """
    model = getattr(fts3.model, model_name, None)
    if not model:
        return {}
    fields = {}
    for field in model.__dict__.values():
        if isinstance(field, InstrumentedAttribute):
            name = field.key
            prop = field.property
            if isinstance(prop, ColumnProperty):
                column = prop.columns[0]
                fields[name] = get_column_type_description(column.type)
            elif isinstance(prop, RelationProperty):
                relation_description = get_relation_type_description(prop, model_list)
                if relation_description:
                    fields[name] = relation_description
    return fields


def get_model_definitions(model_list):
    """
    Generate the definitions of the model list passed
    as parameter
    """
    definitions = {}
    for model in model_list:
        if model != 'array':
            fields = get_model_fields(model, model_list)
            if fields:
                definitions[model] = {
                    'id': model,
                    'properties': fields,
                    'required': fields.keys()
                }
    return definitions


def get_mapper():
    """
    Get the list of Route elements for the application
    """
    mock_config = {
        'pylons.paths': {
            'controllers': controllers_path
        },
        'debug': False
    }
    return routing.make_map(mock_config)


def get_controller_from_module(module, cname):
    """
    Extract classes that inherit from BaseController
    """
    controller_classname = cname.title() + 'Controller'
    controller_class = module.__dict__.get(controller_classname, None)
    return controller_class


def get_controllers():
    """
    Return a list of controllers
    """
    controllers = {}
    for f in os.listdir(controllers_path):
        imp.load_source('fts3rest.controllers', os.path.join(controllers_path, '__init__.py'))
        if not f.endswith('__init__.py') and f.endswith('.py'):
            path = os.path.join(controllers_path, f)
            cname = f.split('.')[0]
            module = imp.load_source('fts3rest.controllers.' + cname, path)
            controller = get_controller_from_module(module, cname)
            if controller:
                controllers[cname] = controller
    return controllers


def get_routes(mapper):
    """
    Return the routes from the mapper skipping the errors
    """
    return filter(lambda r: not r.routelist[0].startswith('/error/') and r.routelist[0] != '/',
                  itertools.chain.from_iterable(mapper.maxkeys.values()))


def get_root_from_route(route):
    return '/' + route.routelist[0].strip('/').split('/')[0]


def generate_resources(routes, controllers):
    """
    Generate the dictionary documenting the resources.
    One resource per controller
    """
    resources = {}
    for r in routes:
        cname = r.defaults.get('controller', None)
        if cname:
            if cname not in resources:
                resource_root = get_root_from_route(r)
                doc = controllers[str(cname)].__doc__
                if doc:
                    doc = doc.strip()
                resources[cname] = {
                    'path': resource_root,
                    'description': doc
                }
            else:
                pass

    return resources.values()


def route2path(routelist):
    """
    Convert a routelist to a regular path
    """
    path = []
    for c in routelist:
        if isinstance(c, dict):
            path.append('{' + c['name'] + '}')
        else:
            path.append(c)
    return ''.join(path).rstrip('/')


def route2parameters(routelist):
    """
    Return a list of parameters found in the given routelist
    """
    params = []
    for c in routelist:
        if isinstance(c, dict):
            params.append({
                'type': 'string',
                'paramType': 'path',
                'name': c['name'],
                'required': True
            })
    return params


def get_function_parameters(function):
    """
    Return a list of query parameters that are documented
    using api.decorators.query_arg
    """
    parameters = []
    for (name, description, return_type, required) in getattr(function, 'doc_query', []):
        parameters.append({
            'name': name,
            'description': description,
            'type': return_type,
            'paramType': 'query',
            'required': bool(required),
        })
    return parameters


def get_function_input(function):
    """
    Return a  with the single input that is documented using
    api.decoratos.input
    """
    parameters = []
    if hasattr(function, 'doc_input'):
        (description, return_type, required) = function.doc_input
        parameters.append({
            'name': 'body',
            'description': description,
            'type': return_type,
            'paramType': 'body',
            'required': bool(required)
        })
    return parameters


def get_function_responses(function):
    """
    Return a list of responses that are documented using
    api.decorators.response
    """
    responses = []
    for (code, description) in getattr(function, 'doc_responses', []):
        responses.append({
            'code': code,
            'message': description
        })
    return responses


def get_function_return(function):
    """
    Return a tuple with the type of the return value of the function
    and the item type (if type is an array)
    """
    return_type = getattr(function, 'doc_return_type', None)
    if not return_type:
        return None, None
    elif return_type != 'array':
        return return_type, None
    else:
        item_type = getattr(function, 'doc_return_item_type', 'string')
        return 'array', item_type


def get_operations_for_function(route, function):
    """
    Populate the operations allowed for a given function
    (that belongs to a controller)
    Returns a tuple (operations, models), where models is populated
    depending on the return types of the operations
    """
    methods = None
    if route.conditions:
        methods = route.conditions.get('method', None)
    if methods is None:
        methods = ['GET']

    summary = None
    notes = None
    if function.__doc__:
        doc_lines = filter(lambda l: len(l) > 0,
                           map(lambda l: l.strip(), function.__doc__.split('\n')))
        summary = doc_lines[0]
        if len(doc_lines) > 1:
            notes = "<br/>".join(doc_lines[1:])

    required_models = []
    operations = []
    for m in methods:
        input_parameters = get_function_input(function)
        operation = {
            'method': m,
            'nickname': function.__name__,
            'summary': summary,
            'notes': notes,
            'parameters':
                route2parameters(route.routelist) +
                get_function_parameters(function) +
                input_parameters,
            'responseMessages': get_function_responses(function)
        }
        return_type, return_item_type = get_function_return(function)
        if return_type:
            operation['type'] = return_type
            required_models.append(return_type)
        if return_item_type:
            operation['items'] = {'$ref': return_item_type}
            required_models.append(return_item_type)
        if len(input_parameters) > 0:
            input_type = input_parameters[0].get('type', None)
            if input_type:
                required_models.append(input_type)

        operations.append(operation)

    return operations, get_model_definitions(required_models)


def actions_from_controller(controller):
    """
    Returns the actions that belong to a controller, this is,
    methods that do not start with _
    """
    actions = []
    for (name, value) in controller.__dict__.iteritems():
        if isinstance(value, FunctionType) and not name.startswith('_'):
            actions.append(name)
    return actions


def generate_apis_and_models(routes, controllers):
    """
    Generate the dictionary documenting the different APIS (methods)
    and Models provided by the application
    """
    all_apis = {}
    all_models = {}
    for route in routes:
        cname = route.defaults.get('controller', None)
        if cname:
            controller = controllers[str(cname)]

            resource_root = get_root_from_route(route)
            if resource_root not in all_apis:
                all_apis[resource_root] = {}
                all_models[resource_root] = {}

            raw_path = route2path(route.routelist)
            params = route2parameters(route.routelist)
            param_names = map(lambda p: p['name'], params)

            if 'action' in param_names:
                actions = actions_from_controller(controller)
            else:
                action = route.defaults.get('action', None)
                if action:
                    actions = [action]
                else:
                    actions = []

            for action in actions:
                path = raw_path.replace('{action}', action)
                function = controller.__dict__.get(action, None)
                if function is None:
                    break

                operations, models = get_operations_for_function(route, function)

                api = {
                    'path': path,
                    'operations': operations
                }

                if path in all_apis[resource_root]:
                    all_apis[resource_root][path]['operations'].extend(api['operations'])
                else:
                    all_apis[resource_root][path] = api
                all_models[resource_root].update(models)

                methods = map(lambda o: o['method'], api['operations'])

    # Remove keys used for convenience
    for resource_root in all_apis:
        all_apis[resource_root] = all_apis[resource_root].values()
    return all_apis, all_models


def introspect():
    """
    Returns a tuple (resources, apis, models) populated instrospecting the API
    """
    mapper = get_mapper()
    controllers = get_controllers()
    routes = get_routes(mapper)
    resources = generate_resources(routes, controllers)
    apis, models = generate_apis_and_models(routes, controllers)
    return resources, apis, models
