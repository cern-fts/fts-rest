#!/usr/bin/env python
import imp
import itertools
import os
import types
from fts3rest.config import routing
from fts3rest.lib.base import BaseController

root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
controllers_path = os.path.join(root_path, 'controllers')


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
    import fts3rest.controllers
    controllers = {}
    for f in os.listdir(controllers_path):
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
    path = []
    for c in routelist:
        if isinstance(c, dict):
            path.append('{' + c['name'] + '}')
        else:
            path.append(c)
    return ''.join(path).rstrip('/')


def route2parameters(routelist):
    params = []
    for c in routelist:
        if isinstance(c, dict):
            params.append({
                'type': 'string',
                'paramType': c['name'],
                'name': c['name'],
                'required': True
            })
    return params


def get_operations_for_method(route, function):
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
            notes = ''.join(doc_lines[1:])
    
    operations = []
    for m in methods:        
        operations.append({
            'method': m,
            'nickname': function.__name__,
            'summary': summary,
            'notes': notes,
            #'type': 'void',
            'parameters': route2parameters(route.routelist),
            #'responseMessages': [
            #    {
            #        'code': 400,
            #        'message': 'Upsy'
            #    }
            #]
        })
    
    return operations

def actions_from_controller(controller):
    actions = []
    for (name, value) in controller.__dict__.iteritems():
        if isinstance(value, types.FunctionType) and not name.startswith('_'):
            actions.append(name)
    return actions

    
def generate_apis_and_models(routes, controllers):
    apis = {}
    models = {}
    for route in routes:
        cname = route.defaults.get('controller', None)
        if cname:
            controller = controllers[str(cname)]
            
            resource_root = get_root_from_route(route)
            if resource_root not in apis:
                apis[resource_root] = {}
            
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

                api = {
                   'path': path,
                   'operations': get_operations_for_method(route, function)
                }
                
                if path in apis[resource_root]:
                    apis[resource_root][path]['operations'].extend(api['operations'])
                else:
                    apis[resource_root][path] = api
    
                methods = map(lambda o: o['method'], api['operations'])

    # Remove keys used for convenience
    for api in apis:
        apis[api] = apis[api].values()
    return (apis, models)
