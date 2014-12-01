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

from datetime import datetime
from pylons import request
from pylons.controllers.util import abort
from webob.exc import HTTPBadRequest
import errno
import os
import stat
import tempfile
import urlparse
import urllib
import json
import pylons

from fts3.model import Credential
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.http_exceptions import HTTPAuthenticationTimeout
from fts3rest.lib.gfal2_wrapper import Gfal2Wrapper, Gfal2Error
from fts3rest.controllers.CSdropbox import DropboxConnector;

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
        raise HTTPAuthenticationTimeout('Delegated proxy expired (%s)' % user.delegation_id)

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

def _is_dropbox(uri):
    return uri.startswith("dropbox")

def _set_dropbox_headers(context):
    # getting the tokens and add them to the context
    user = request.environ['fts3.User.Credentials']
    dropbox_con = DropboxConnector(user.user_dn,"dropbox")
    dropbox_info = dropbox_con._get_dropbox_info()
    dropbox_user_info = dropbox_con._get_dropbox_user_info();
    context.set_opt_string("DROPBOX","APP_KEY",dropbox_info.app_key)
    context.set_opt_string("DROPBOX","APP_SECRET",dropbox_info.app_secret)
    context.set_opt_string("DROPBOX","ACCESS_TOKEN",dropbox_user_info.access_token)
    context.set_opt_string("DROPBOX","ACCESS_TOKEN_SECRET",dropbox_user_info.access_token_secret)
    return context


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


def _rename_impl(context, rename_dict):
    if (len(rename_dict['old']) == 0) or (len(rename_dict['new'])) == 0:
        raise HTTPBadRequest('No old or name specified')

    old_path = rename_dict['old']
    new_path = rename_dict['new']

    if _is_dropbox(str(old_path)):
        context = _set_dropbox_headers(context)

    return context.rename(str(old_path), str(new_path))


def _unlink_impl(context, unlink_dict):
    if len(unlink_dict['surl']) == 0:
        raise HTTPBadRequest('No parameter "surl" specified')

    path = unlink_dict['surl']

    if _is_dropbox(str(path)):
        context = _set_dropbox_headers(context)

    return context.unlink(str(path))


def _rmdir_impl(context, rmdir_dict):
    if len(rmdir_dict['surl']) == 0:
        raise HTTPBadRequest('No parameter "surl" specified')

    path = rmdir_dict['surl']

    if _is_dropbox(str(path)):
        context = _set_dropbox_headers(context)

    return context.rmdir(str(path))


def _mkdir_impl(context, mkdir_dict):
    if len(mkdir_dict['surl']) == 0:
        raise HTTPBadRequest('No parameter "surl" specified')

    path = mkdir_dict['surl']

    if _is_dropbox(str(path)):
        context = _set_dropbox_headers(context)

    return context.mkdir(str(path), 0775)


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
    def list(self):
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
        finally:
            os.unlink(proxy.name)

    @doc.query_arg('surl', 'Remote SURL', required=True)
    @doc.response(400, 'Protocol not supported OR the SURL is not a directory')
    @doc.response(403, 'Permission denied')
    @doc.response(404, 'The SURL does not exist')
    @doc.response(419, 'The credentials need to be re-delegated')
    @doc.response(503, 'Try again later')
    @doc.response(500, 'Internal error')
    @jsonify
    def stat(self):
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
        finally:
            os.unlink(proxy.name)

    @doc.query_arg('surl', 'Remote SURL', required=True)
    @doc.response(400, 'Protocol not supported OR the SURL is not a directory')
    @doc.response(403, 'Permission denied')
    @doc.response(404, 'The SURL does not exist')
    @doc.response(419, 'The credentials need to be re-delegated')
    @doc.response(503, 'Try again later')
    @doc.response(500, 'Internal error')
    @jsonify
    def rename(self):
        """
        Stat a remote file
        """
        proxy = _get_proxy()

        try:

            if request.method == 'POST':
                if request.content_type == 'application/json':
                    unencoded_body = request.body
                else:
                    unencoded_body = urllib.unquote_plus(request.body)
            else:
                raise HTTPBadRequest('Unsupported method %s' % request.method)

            rename_dict = json.loads(unencoded_body)

            m = Gfal2Wrapper(proxy, _rename_impl)
            try:
                return m(rename_dict)
            except Gfal2Error, e:
                _raise_http_error_from_gfal2_error(e)
            finally:
                os.unlink(proxy.name)

        except ValueError, e:
            raise HTTPBadRequest('Invalid value within the request: %s' % str(e))
        except TypeError, e:
            raise HTTPBadRequest('Malformed request: %s' % str(e))
        except KeyError, e:
            raise HTTPBadRequest('Missing parameter: %s' % str(e))

    @doc.response(400, 'Protocol not supported OR the SURL is not a directory')
    @doc.response(403, 'Permission denied')
    @doc.response(404, 'The SURL does not exist')
    @doc.response(419, 'The credentials need to be re-delegated')
    @doc.response(503, 'Try again later')
    @doc.response(500, 'Internal error')
    @jsonify
    def unlink(self):
        """
        Remove a remote file
        """
        proxy = _get_proxy()

        try:

            if request.method == 'POST':
                if request.content_type == 'application/json':
                    unencoded_body = request.body
                else:
                    unencoded_body = urllib.unquote_plus(request.body)
            else:
                raise HTTPBadRequest('Unsupported method %s' % request.method)

            unlink_dict = json.loads(unencoded_body)

            m = Gfal2Wrapper(proxy, _unlink_impl)
            try:
                return m(unlink_dict)
            except Gfal2Error, e:
                _raise_http_error_from_gfal2_error(e)
            finally:
                os.unlink(proxy.name)

        except ValueError, e:
            raise HTTPBadRequest('Invalid value within the request: %s' % str(e))
        except TypeError, e:
            raise HTTPBadRequest('Malformed request: %s' % str(e))
        except KeyError, e:
            raise HTTPBadRequest('Missing parameter: %s' % str(e))

    @doc.response(400, 'Protocol not supported OR the SURL is not a directory')
    @doc.response(403, 'Permission denied')
    @doc.response(404, 'The SURL does not exist')
    @doc.response(419, 'The credentials need to be re-delegated')
    @doc.response(503, 'Try again later')
    @doc.response(500, 'Internal error')
    @jsonify
    def rmdir(self):
        """
        Remove a remote folder
        """
        proxy = _get_proxy()

        try:
            if request.method == 'POST':
                if request.content_type == 'application/json':
                    unencoded_body = request.body
                else:
                    unencoded_body = urllib.unquote_plus(request.body)
            else:
                raise HTTPBadRequest('Unsupported method %s' % request.method)

            rmdir_dict = json.loads(unencoded_body)

            m = Gfal2Wrapper(proxy, _rmdir_impl)
            try:
                return m(rmdir_dict)
            except Gfal2Error, e:
                _raise_http_error_from_gfal2_error(e)
            finally:
                os.unlink(proxy.name)

        except ValueError, e:
            raise HTTPBadRequest('Invalid value within the request: %s' % str(e))
        except TypeError, e:
            raise HTTPBadRequest('Malformed request: %s' % str(e))
        except KeyError, e:
            raise HTTPBadRequest('Missing parameter: %s' % str(e))

    @doc.query_arg('surl', 'Remote SURL', required=True)
    @doc.response(400, 'Protocol not supported OR the SURL is not a directory')
    @doc.response(403, 'Permission denied')
    @doc.response(404, 'The SURL does not exist')
    @doc.response(419, 'The credentials need to be re-delegated')
    @doc.response(503, 'Try again later')
    @doc.response(500, 'Internal error')
    @jsonify
    def mkdir(self):
        """
        Create a remote file
        """
        proxy = _get_proxy()

        try:
            if request.method == 'POST':
                if request.content_type == 'application/json':
                    unencoded_body = request.body
                else:
                    unencoded_body = urllib.unquote_plus(request.body)
            else:
                raise HTTPBadRequest('Unsupported method %s' % request.method)

            mkdir_dict = json.loads(unencoded_body)
            m = Gfal2Wrapper(proxy, _mkdir_impl)
            try:
                return m(mkdir_dict)
            except Gfal2Error, e:
                _raise_http_error_from_gfal2_error(e)
            finally:
                os.unlink(proxy.name)

        except ValueError, e:
            raise HTTPBadRequest('Invalid value within the request: %s' % str(e))
        except TypeError, e:
            raise HTTPBadRequest('Malformed request: %s' % str(e))
        except KeyError, e:
            raise HTTPBadRequest('Missing parameter: %s' % str(e))
