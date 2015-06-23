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
    map.connect('/', controller='api', action='api_version')

    # OPTIONS handler
    map.connect('/{path:.*?}', controller='api', action='options_handler',
                conditions=dict(method=['OPTIONS']))

    # Delegation and self-identification
    map.connect('/whoami', controller='delegation', action='whoami',
                conditions=dict(method=['GET']))
    map.connect('/whoami/certificate', controller='delegation', action='certificate',
                conditions=dict(method=['GET']))
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
    map.connect('/jobs/{job_id}/files/{file_ids}', controller='jobs', action='cancel_files',
                conditions=dict(method=['DELETE']))
    map.connect('/jobs/{job_id}/files/{file_id}/retries', controller='jobs', action='get_file_retries',
                conditions=dict(method=['GET']))
    map.connect('/jobs/{job_id}/dm', controller='jobs', action='get_dm',
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
    map.connect('/api-docs/schema/submit', controller='api', action='submit_schema',
                conditions=dict(method=['GET']))
    map.connect('/api-docs', controller='api', action='api_docs',
                conditions=dict(method=['GET']))
    map.connect('/api-docs/{resource}', controller='api', action='resource_doc',
                conditions=dict(method=['GET']))

    # Config entry point
    map.connect('/config', controller='config', action='index',
                conditions=dict(method=['GET']))

    # Set/unset draining mode
    map.connect('/config/drain', controller='config', action='set_drain',
                conditions=dict(method=['POST']))

    # Configuration audit
    map.connect('/config/audit', controller='config', action='audit',
                conditions=dict(method=['GET']))

    # Debug level
    map.connect('/config/debug', controller='config', action='set_debug',
                conditions=dict(method=['POST']))
    map.connect('/config/debug', controller='config', action='delete_debug',
                conditions=dict(method=['DELETE']))
    map.connect('/config/debug', controller='config', action='list_debug',
                conditions=dict(method=['GET']))

    # Global settings
    map.connect('/config/global', controller='config', action='set_global_config',
                conditions=dict(method=['POST']))
    map.connect('/config/global', controller='config', action='get_global_config',
                conditions=dict(method=['GET']))
    map.connect('/config/global', controller='config', action='delete_vo_global_config',
                conditions=dict(method=['DELETE']))

    # Groups and group members
    map.connect('/config/groups', controller='config', action='add_to_group',
                conditions=dict(method=['POST']))
    map.connect('/config/groups', controller='config', action='get_all_groups',
                conditions=dict(method=['GET']))
    map.connect('/config/groups/{group_name}', controller='config', action='get_group',
                conditions=dict(method=['GET']))
    map.connect('/config/groups/{group_name}', controller='config', action='delete_from_group',
                conditions=dict(method=['DELETE']))

    # Link config (SE or Group)
    map.connect('/config/links', controller='config', action='set_link_config',
                conditions=dict(method=['POST']))
    map.connect('/config/links', controller='config', action='get_all_link_configs',
                conditions=dict(method=['GET']))
    map.connect('/config/links/{sym_name}', controller='config', action='get_link_config',
                conditions=dict(method=['GET']))
    map.connect('/config/links/{sym_name}', controller='config', action='delete_link_config',
                conditions=dict(method=['DELETE']))

    # Shares
    map.connect('/config/shares', controller='config', action='set_share',
                conditions=dict(method=['POST']))
    map.connect('/config/shares', controller='config', action='get_shares',
                conditions=dict(method=['GET']))
    map.connect('/config/shares', controller='config', action='delete_share',
                conditions=dict(method=['DELETE']))

    # Fixed number of actives
    map.connect('/config/fixed', controller='config', action='fix_active',
                conditions=dict(method=['POST']))
    map.connect('/config/fixed', controller='config', action='get_fixed_active',
                conditions=dict(method=['GET']))

    # Per SE
    map.connect('/config/se', controller='config', action='set_se_config',
                conditions=dict(method=['POST']))
    map.connect('/config/se', controller='config', action='get_se_config',
                conditions=dict(method=['GET']))
    map.connect('/config/se', controller='config', action='delete_se_config',
                conditions=dict(method=['DELETE']))

    # Grant special permissions to given DNs
    map.connect('/config/authorize', controller='config', action='add_authz',
                conditions=dict(method=['POST']))
    map.connect('/config/authorize', controller='config', action='list_authz',
                conditions=dict(method=['GET']))
    map.connect('/config/authorize', controller='config', action='remove_authz',
                conditions=dict(method=['DELETE']))

    # Optimizer
    map.connect('/optimizer', controller='optimizer', action='is_enabled',
                conditions=dict(method=['GET']))
    map.connect('/optimizer/evolution', controller='optimizer',
                action='evolution',
                conditions=dict(method=['GET']))

    # GFAL2 bindings
    map.connect('/dm/list', controller='datamanagement', action='list',
                conditions=dict(method=['GET']))
    map.connect('/dm/stat', controller='datamanagement', action='stat',
                conditions=dict(method=['GET']))
    map.connect('/dm/mkdir', controller='datamanagement', action='mkdir',
                conditions=dict(method=['POST']))
    map.connect('/dm/unlink', controller='datamanagement', action='unlink',
                conditions=dict(method=['POST']))
    map.connect('/dm/rmdir', controller='datamanagement', action='rmdir',
                conditions=dict(method=['POST']))
    map.connect('/dm/rename', controller='datamanagement', action='rename',
                conditions=dict(method=['POST']))

    # Snapshot
    map.connect('/snapshot', controller='snapshot', action='snapshot',
                conditions=dict(method=['GET']))

    # Banning
    map.connect('/ban/se', controller='banning', action='ban_se',
                conditions=dict(method=['POST']))
    map.connect('/ban/se', controller='banning', action='unban_se',
                conditions=dict(method=['DELETE']))
    map.connect('/ban/se', controller='banning', action='list_banned_se',
                conditions=dict(method=['GET']))
    map.connect('/ban/dn', controller='banning', action='ban_dn',
                conditions=dict(method=['POST']))
    map.connect('/ban/dn', controller='banning', action='unban_dn',
                conditions=dict(method=['DELETE']))
    map.connect('/ban/dn', controller='banning', action='list_banned_dn',
                conditions=dict(method=['GET']))

    # Autocomplete
    map.connect('/autocomplete/dn', controller='autocomplete', action='autocomplete_dn',
                conditions=dict(method=['GET']))
    map.connect('/autocomplete/source', controller='autocomplete', action='autocomplete_source',
                conditions=dict(method=['GET']))
    map.connect('/autocomplete/destination', controller='autocomplete', action='autocomplete_destination',
                conditions=dict(method=['GET']))
    map.connect('/autocomplete/storage', controller='autocomplete', action='autocomplete_storage',
                conditions=dict(method=['GET']))
    map.connect('/autocomplete/vo', controller='autocomplete', action='autocomplete_vo',
                conditions=dict(method=['GET']))
    map.connect('/autocomplete/groupname', controller='autocomplete', action='autocomplete_groupname',
                conditions=dict(method=['GET']))
