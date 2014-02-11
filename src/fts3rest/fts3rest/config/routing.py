"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper


def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    map.explicit = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # Root
    map.connect('/', controller='misc', action='apiVersion')

    # Whoami
    map.connect('/whoami', controller='misc', action='whoami')

    # Delegation
    map.connect('/delegation/{id}', controller='delegation', action='view',
                conditions=dict(method=['GET']))
    map.connect('/delegation/{id}', controller='delegation', action='delete',
                conditions=dict(method=['DELETE']))
    map.connect('/delegation/{id}/request', controller='delegation', action='request',
                conditions=dict(method=['GET']))
    map.connect('/delegation/{id}/credential', controller='delegation', action='credential',
                conditions=dict(method=['PUT', 'POST']))
    map.connect('/delegation/{id}/voms', controller='delegation', action='voms',
                conditions=dict(method=['POST']))

    # Jobs
    map.connect('/jobs', controller='jobs', action='index',
                conditions=dict(method=['GET']))
    map.connect('/jobs/', controller='jobs', action='index',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{id}', controller='jobs', action='show',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{id}/{field}', controller='jobs', action='showField',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{id}', controller='jobs', action='cancel',
                conditions=dict(method=['DELETE']))
    map.connect('/jobs', controller='jobs', action='submit',
                conditions=dict(method=['PUT', 'POST']))

    # Archive
    map.connect('/archive', controller='archive', action='index',
                conditions=dict(method=['GET']))
    map.connect('/archive/', controller='archive', action='index',
                conditions=dict(method=['GET']))
    map.connect('/archive/{id}', controller='archive', action='show',
                conditions=dict(method=['GET']))
    map.connect('/archive/{id}/{field}', controller='archive',
                action='showField',
                conditions=dict(method=['GET']))

    # Schema definition
    map.connect('/schema/submit', controller='schema', action='submit')

    # Configuration audit
    map.connect('/config/audit', controller='config', action='audit')

    # Optimizer
    map.connect('/optimizer/', controller='optimizer', action='isEnabled')
    map.connect('/optimizer/evolution', controller='optimizer',
                action='evolution')
    map.connect('/optimizer/snapshot', controller='optimizer',
                action='snapshot')
    
    # GFAL2 bindings
    map.connect('/dm/', controller='datamanagement', action='index')
    map.connect('/dm/list', controller='datamanagement', action='list')
    map.connect('/dm/stat', controller='datamanagement', action='stat')

    return map
