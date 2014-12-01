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


def do_connect(config, map):
    """
    Base urls
    """
    # Root
    map.connect('/', controller='misc', action='api_version')

    # OPTIONS handler
    map.connect('/{path:.*?}', controller='api', action='options_handler',
                conditions=dict(method=['OPTIONS']))

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
    map.connect('/jobs/{job_list}', controller='jobs', action='get',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id}/files', controller='jobs', action='get_files',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id}/files/{file_id}/retries', controller='jobs', action='get_file_retries',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id}/{field}', controller='jobs', action='get_field',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id_list}', controller='jobs', action='cancel',
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
    map.connect('/dm/mkdir', controller='datamanagement', action='mkdir', conditions=dict(method=['POST']))
    map.connect('/dm/unlink', controller='datamanagement', action='unlink', conditions=dict(method=['POST']))
    map.connect('/dm/rmdir', controller='datamanagement', action='rmdir', conditions=dict(method=['POST']))
    map.connect('/dm/rename', controller='datamanagement', action='rename', conditions=dict(method=['POST']))

    # Snapshot
    map.connect('/snapshot', controller='snapshot', action='snapshot')

    # Banning
    map.connect('/ban/se', controller='banning', action='ban_se', conditions=dict(method=['POST']))
    map.connect('/ban/se', controller='banning', action='unban_se', conditions=dict(method=['DELETE']))
    map.connect('/ban/dn', controller='banning', action='ban_dn', conditions=dict(method=['POST']))
    map.connect('/ban/dn', controller='banning', action='unban_dn', conditions=dict(method=['DELETE']))
