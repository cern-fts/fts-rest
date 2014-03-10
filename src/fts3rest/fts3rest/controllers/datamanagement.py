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
import gfal2


def _get_valid_surl():
    surl = request.params.get('surl')
    if not surl:
        raise HTTPBadRequest('Missing surl parameter')

    parsed = urlparse.urlparse(surl)
    if parsed.scheme in ['file']:
        raise HTTPBadRequest('Forbiden SURL scheme')

    return str(surl)


def _http_status_from_gerror(e):
    if e.code in (errno.EPERM, errno.EACCES):
        return 403
    elif e.code == errno.ENOENT:
        return 404
    elif e.code in (errno.EAGAIN, errno.EBUSY):
        return 503
    elif e.code in (errno.ENOTDIR, errno.EPROTONOSUPPORT):
        return 400
    else:
        return 500


def _raise_http_error_from_gerror(e):
    abort(_http_status_from_gerror(e), "[%d] %s" % (e.code, e.message))


class DatamanagementController(BaseController):
    """
    Data management operations
    """

    @staticmethod
    def _get_proxy():
        user = request.environ['fts3.User.Credentials']
        cred = Session.query(Credential).get((user.delegation_id, user.user_dn))
        if not cred:
            raise HTTPAuthenticationTimeout('No delegated proxy available')

        if cred.termination_time <= datetime.utcnow():
            raise HTTPAuthenticationTimeout('Delegated proxy expired')

        tmp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', prefix='rest-proxy-')
        tmp_file.write(cred.proxy)
        tmp_file.flush()
        os.fsync(tmp_file.fileno())
        return tmp_file

    @staticmethod
    def _set_x509_env(proxy_file):
        os.environ['X509_USER_CERT'] = proxy_file.name
        os.environ['X509_USER_KEY'] = proxy_file.name
        os.environ['X509_USER_PROXY'] = proxy_file.name

    @staticmethod
    def _clear_x509_env():
        del os.environ['X509_USER_CERT']
        del os.environ['X509_USER_KEY']
        del os.environ['X509_USER_PROXY']

    @staticmethod
    def _dir_listing(surl):
        ctx = gfal2.creat_context()
        try:
            path = ctx.opendir(surl)
            listing = {}
            (entry, st_stat) = path.readpp()
            while entry:
                d_name = entry.d_name
                if stat.S_ISDIR(st_stat.st_mode):
                    d_name += '/'

                listing[d_name] = {
                    'size': st_stat.st_size,
                    'mode': st_stat.st_mode,
                    'mtime': st_stat.st_mtime
                }

                (entry, st_stat) = path.readpp()
            return listing
        except gfal2.GError, e:
            _raise_http_error_from_gerror(e)

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
        proxy = self._get_proxy()
        surl = _get_valid_surl()
        try:
            self._set_x509_env(proxy)
            return self._dir_listing(surl)
        finally:
            self._clear_x509_env()

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
        proxy = self._get_proxy()
        surl = _get_valid_surl()
        try:
            self._set_x509_env(proxy)
            ctx = gfal2.creat_context()
            stat_st = ctx.stat(surl)
            return {
                'mode' : stat_st.st_mode,
                'nlink': stat_st.st_nlink,
                'size' : stat_st.st_size,
                'atime': stat_st.st_atime,
                'mtime': stat_st.st_mtime,
                'ctime': stat_st.st_ctime
            }
        except gfal2.GError, e:
            _raise_http_error_from_gerror(e)
        finally:
            self._clear_x509_env()
