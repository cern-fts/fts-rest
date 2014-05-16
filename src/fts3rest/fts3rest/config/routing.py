#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2010.
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
    map.connect('/', controller='misc', action='api_version')

    # Whoami
    map.connect('/whoami', controller='misc', action='whoami')

    # Delegation
    map.connect('/delegation/{dlg_id}', controller='delegation', action='view',
                conditions=dict(method=['GET']))
    map.connect('/delegation/{dlg_id}', controller='delegation', action='delete',
                conditions=dict(method=['DELETE']))
    map.connect('/delegation/{dlg_id}/request', controller='delegation', action='request',
                conditions=dict(method=['GET']))
    map.connect('/delegation/{dlg_id}/credential', controller='delegation', action='credential',
                conditions=dict(method=['PUT', 'POST']))
    map.connect('/delegation/{dlg_id}/voms', controller='delegation', action='voms',
                conditions=dict(method=['POST']))

    # Jobs
    map.connect('/jobs', controller='jobs', action='index',
                conditions=dict(method=['GET']))
    map.connect('/jobs/', controller='jobs', action='index',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id}', controller='jobs', action='get',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id}/{field}', controller='jobs', action='get_field',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id}', controller='jobs', action='cancel',
                conditions=dict(method=['DELETE']))
    map.connect('/jobs', controller='jobs', action='submit',
                conditions=dict(method=['PUT', 'POST']))

    # Archive
    map.connect('/archive', controller='archive', action='index',
                conditions=dict(method=['GET']))
    map.connect('/archive/', controller='archive', action='index',
                conditions=dict(method=['GET']))
    map.connect('/archive/{job_id}', controller='archive', action='get',
                conditions=dict(method=['GET']))
    map.connect('/archive/{job_id}/{field}', controller='archive',
                action='get_field',
                conditions=dict(method=['GET']))

    # Schema definition
    map.connect('/api-docs/schema/submit', controller='api', action='submit_schema')
    map.connect('/api-docs', controller='api', action='api_docs')
    map.connect('/api-docs/{resource}', controller='api', action='resource_doc')

    # Configuration audit
    map.connect('/config/audit', controller='config', action='audit')

    # Optimizer
    map.connect('/optimizer', controller='optimizer', action='is_enabled')
    map.connect('/optimizer/evolution', controller='optimizer',
                action='evolution')
    
    # GFAL2 bindings
    map.connect('/dm/list', controller='datamanagement', action='list')
    map.connect('/dm/stat', controller='datamanagement', action='stat')

    return map
