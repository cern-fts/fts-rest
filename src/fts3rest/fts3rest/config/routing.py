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
    map.connect('/whoami/certificate', controller='misc', action='certificate')

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

    # Delegation HTML view
    map.connect('/delegation', controller='delegation', action='delegation_page',
                conditions=dict(method=['GET']))

    # Jobs
    map.connect('/jobs', controller='jobs', action='index',
                conditions=dict(method=['GET']))
    map.connect('/jobs/', controller='jobs', action='index',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id}', controller='jobs', action='get',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id}/files', controller='jobs', action='get_files',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id}/files/{file_id}/retries', controller='jobs', action='get_file_retries',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id}/{field}', controller='jobs', action='get_field',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id}', controller='jobs', action='cancel',
                conditions=dict(method=['DELETE']))
    map.connect('/jobs', controller='jobs', action='submit',
                conditions=dict(method=['PUT', 'POST']))

    map.connect('/jobs/{job_id}', controller='jobs', action='job_options',
                conditions=dict(method=['OPTIONS']))
    map.connect('/jobs', controller='jobs', action='options',
                conditions=dict(method=['OPTIONS']))

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

    # Snapshot
    map.connect('/snapshot', controller='snapshot', action='snapshot')

    # Banning
    map.connect('/ban/se', controller='banning', action='ban_se', conditions=dict(method=['POST']))
    map.connect('/ban/se', controller='banning', action='unban_se', conditions=dict(method=['DELETE']))
    map.connect('/ban/dn', controller='banning', action='ban_dn', conditions=dict(method=['POST']))
    map.connect('/ban/dn', controller='banning', action='unban_dn', conditions=dict(method=['DELETE']))

    # Cloud Storage
    map.connect('/cs/registered/{service}', controller='cloudStorage', action='is_registered',
                conditions=dict(method=['GET']))
    map.connect('/cs/access_request/{service}', controller='cloudStorage', action='is_access_requested',
                conditions=dict(method=['GET']))
    map.connect('/cs/access_request/{service}/', controller='cloudStorage', action='is_access_requested',
                conditions=dict(method=['GET']))
    map.connect('/cs/access_request/{service}/request', controller='cloudStorage', action='get_access_requested',
                conditions=dict(method=['GET']))
    map.connect('/cs/access_grant/{service}', controller='cloudStorage', action='get_access_granted',
                conditions=dict(method=['GET']))
    map.connect('/cs/remote_content/{service}', controller='cloudStorage', action='get_folder_content',
                conditions=dict(method=['GET']))
    map.connect('/cs/file_urllink/{service}/{path}', controller='cloudStorage', action='get_file_link',
                conditions=dict(method=['GET']))

    # OAuth 2.0
    map.redirect('/oauth2', '/oauth2/apps')
    map.connect('/oauth2/apps', controller='oauth2', action='get_my_apps', conditions=dict(method=['GET']))
    map.connect('/oauth2/register', controller='oauth2', action='register_form', conditions=dict(method=['GET']))
    map.connect('/oauth2/register', controller='oauth2', action='register', conditions=dict(method=['POST']))
    map.connect('/oauth2/apps/{client_id}', controller='oauth2', action='get_app', conditions=dict(method=['GET']))
    map.connect('/oauth2/apps/{client_id}', controller='oauth2', action='update_app', conditions=dict(method=['POST']))
    map.connect('/oauth2/apps/{client_id}', controller='oauth2', action='delete_app', conditions=dict(method=['DELETE']))

    map.connect('/oauth2/authorize', controller='oauth2', action='authorize', conditions=dict(method=['GET']))
    map.connect('/oauth2/authorize', controller='oauth2', action='confirm', conditions=dict(method=['POST']))
    map.connect('/oauth2/token', controller='oauth2', action='get_token', conditions=dict(method=['GET', 'POST']))
    map.connect('/oauth2/revoke/{client_id}', controller='oauth2', action='revoke_token', conditions=dict(method=['GET']))

    return map
