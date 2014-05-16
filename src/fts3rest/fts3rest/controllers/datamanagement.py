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

from datetime import datetime
from pylons import request
from pylons.controllers.util import abort
from webob.exc import HTTPBadRequest
import errno
import os
import stat
import tempfile
import urlparse

from fts3.model import Credential
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.http_exceptions import HTTPAuthenticationTimeout
from fts3rest.lib.gfal2_wrapper import Gfal2Wrapper, Gfal2Error


def _get_valid_surl():
    surl = request.params.get('surl')
    if not surl:
        raise HTTPBadRequest('Missing surl parameter')
    parsed = urlparse.urlparse(surl)
    if parsed.scheme in ['file']:
        raise HTTPBadRequest('Forbiden SURL scheme')
    return str(surl)


def _get_proxy():
    user = request.environ['fts3.User.Credentials']
    cred = Session.query(Credential).get((user.delegation_id, user.user_dn))
    if not cred:
        raise HTTPAuthenticationTimeout('No delegated proxy available')

    if cred.termination_time <= datetime.utcnow():
        raise HTTPAuthenticationTimeout('Delegated proxy expired')

    tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', prefix='rest-proxy-', delete=False)
    tmp_file.write(cred.proxy)
    tmp_file.flush()
    os.fsync(tmp_file.fileno())
    return tmp_file


def _http_status_from_errno(e):
    if e in (errno.EPERM, errno.EACCES):
        return 403
    elif e == errno.ENOENT:
        return 404
    elif e in (errno.EAGAIN, errno.EBUSY, errno.ETIMEDOUT):
        return 503
    elif e in (errno.ENOTDIR, errno.EPROTONOSUPPORT):
        return 400
    else:
        return 500


def _raise_http_error_from_gfal2_error(e):
    abort(_http_status_from_errno(e.errno), "[%d] %s" % (e.errno, e.message))


def _stat_impl(context, surl):
    st_stat = context.stat(surl)
    return {
        'mode' : st_stat.st_mode,
        'nlink': st_stat.st_nlink,
        'size' : st_stat.st_size,
        'atime': st_stat.st_atime,
        'mtime': st_stat.st_mtime,
        'ctime': st_stat.st_ctime
    }


def _list_impl(context, surl):
    dir = context.opendir(surl)
    listing = {}
    (entry, st_stat) = dir.readpp()
    while entry:
        d_name = entry.d_name
        if stat.S_ISDIR(st_stat.st_mode):
            d_name += '/'
        listing[d_name] = {
            'size': st_stat.st_size,
            'mode': st_stat.st_mode,
            'mtime': st_stat.st_mtime
        }
        (entry, st_stat) = dir.readpp()
    return listing


class DatamanagementController(BaseController):
    """
    Data management operations
    """

    @doc.query_arg('surl', 'Remote SURL', required=True)
    @doc.response(400, 'Protocol not supported OR the SURL is not a directory')
    @doc.response(403, 'Permission denied')
    @doc.response(404, 'The SURL does not exist')
    @doc.response(419, 'The credentials need to be re-delegated')
    @doc.response(503, 'Try again later')
    @doc.response(500, 'Internal error')
    @jsonify
    def list(self, **kwargs):
        """
        List the content of a remote directory
        """
        surl = _get_valid_surl()
        proxy = _get_proxy()

        m = Gfal2Wrapper(proxy, _list_impl)
        try:
            return m(surl)
        except Gfal2Error, e:
            _raise_http_error_from_gfal2_error(e)

    @doc.query_arg('surl', 'Remote SURL', required=True)
    @doc.response(400, 'Protocol not supported OR the SURL is not a directory')
    @doc.response(403, 'Permission denied')
    @doc.response(404, 'The SURL does not exist')
    @doc.response(419, 'The credentials need to be re-delegated')
    @doc.response(503, 'Try again later')
    @doc.response(500, 'Internal error')
    @jsonify
    def stat(self, **kwargs):
        """
        Stat a remote file
        """
        surl = _get_valid_surl()
        proxy = _get_proxy()

        m = Gfal2Wrapper(proxy, _stat_impl)
        try:
            return m(surl)
        except Gfal2Error, e:
            _raise_http_error_from_gfal2_error(e)
