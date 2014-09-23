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
    OAuth2
    """
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
