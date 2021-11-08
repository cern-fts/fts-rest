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

from keystoneauth1 import session, exceptions
from keystoneauth1.identity import v3
import logging

log = logging.getLogger(__name__)


def get_os_token(cloud_user, access_token, cloud_storage):
    project_id = cloud_user.os_project_id

    keystone_auth = v3.oidc.OidcAccessToken(auth_url=cloud_storage.keystone_url,
                                            identity_provider=cloud_storage.keystone_idp,
                                            protocol="openid",
                                            access_token=access_token,
                                            project_id=project_id)
    sess = session.Session(auth=keystone_auth)
    try:
        os_token = sess.get_token()
        log.debug("retrieved OS token %s" % os_token)
        cloud_user.os_token = os_token
    except Exception as ex:
        log.warning("Failed to retrieve OS token because: %s" % str(ex))
    return cloud_user
