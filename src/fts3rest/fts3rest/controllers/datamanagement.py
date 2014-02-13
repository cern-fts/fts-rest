from datetime import datetime
from fts3.model import Credential
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from pylons import request
from pylons.controllers.util import abort
import errno
import gfal2
import os
import stat
import tempfile
import urlparse


class DatamanagementController(BaseController):
    """
    Data management operations
    """
    
    def _getProxy(self):
        user = request.environ['fts3.User.Credentials']
        cred = Session.query(Credential).get((user.delegation_id, user.user_dn))
        if not cred:
            abort(401, 'No delegated proxy available')
            
        if cred.termination_time <= datetime.utcnow():
            abort(401, 'Delegated proxy expired')

        tmpFile = tempfile.NamedTemporaryFile(mode='w', suffix='.pem', prefix='rest-proxy-')
        tmpFile.write(cred.proxy)
        tmpFile.flush()
        os.fsync(tmpFile.fileno())
        return tmpFile
    
    def _setX509(self, proxyFile):
        os.environ['X509_USER_CERT'] = proxyFile.name
        os.environ['X509_USER_KEY'] = proxyFile.name
        os.environ['X509_USER_PROXY'] = proxyFile.name
        
    def _clearX509(self, proxyFile):
        del os.environ['X509_USER_CERT']
        del os.environ['X509_USER_KEY']
        del os.environ['X509_USER_PROXY']
        
    def _getValidSurl(self):
        surl = request.params.get('surl')
        if not surl:
            abort(400, 'Missing surl parameter')
            
        parsed = urlparse.urlparse(surl)
        if parsed.scheme in ['file']:
            abort(400, 'Forbiden SURL scheme')
            
        return str(surl)
    
    def _httpCodeFromGError(self, e):
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
        
    def _httpErrorFromGerror(self, e):
        abort(self._httpCodeFromGError(e), "[%d] %s" % (e.code, e.message))

    def _dirListing(self, surl):
        ctx = gfal2.creat_context()
        try:
            dir = ctx.opendir(surl)
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
        except gfal2.GError, e:
            self._httpErrorFromGerror(e)
    
    @doc.query_arg('surl', 'Remote SURL', required=True)
    @doc.response(400, 'Protocol not supported OR the SURL is not a directory')
    @doc.response(403, 'Permission denied')
    @doc.response(404, 'The SURL does not exist')
    @doc.response(503, 'Try again later')
    @doc.response(500, 'Internal error') 
    @jsonify
    def list(self, **kwargs):
        """
        List the content of a remote directory
        """
        proxy = self._getProxy()
        surl = self._getValidSurl()
        try:
            self._setX509(proxy)
            return self._dirListing(surl)
        finally:
            self._clearX509(proxy)

    @doc.query_arg('surl', 'Remote SURL', required=True)
    @doc.response(400, 'Protocol not supported OR the SURL is not a directory')
    @doc.response(403, 'Permission denied')
    @doc.response(404, 'The SURL does not exist')
    @doc.response(503, 'Try again later')
    @doc.response(500, 'Internal error') 
    @jsonify
    def stat(self, **kwargs):
        """
        Stat a remote file
        """
        proxy = self._getProxy()
        surl = self._getValidSurl()
        try:
            self._setX509(proxy)
            ctx = gfal2.creat_context()
            stat_st = ctx.stat(surl)
            return {
                'mode':  stat_st.st_mode,
                'nlink': stat_st.st_nlink,
                'size':  stat_st.st_size,
                'atime': stat_st.st_atime,
                'mtime': stat_st.st_mtime,
                'ctime': stat_st.st_ctime
            }
        except gfal2.GError, e:
            self._httpErrorFromGerror(e)
        finally:
            self._clearX509(proxy)
