#   Copyright notice:
#   Copyright CERN, 2014.
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

# Dropbox specific connector
#
# Andres Abad Rodriguez <andres.abad.rodriguez@cern.ch>
#
# Based on https://www.dropbox.com/developers/core/docs
from webob.exc import HTTPNotFound
from pylons import request
from webob.exc import HTTPBadRequest
import urlparse


from fts3rest.lib.helpers import jsonify
from fts3rest.lib.base import BaseController, Session
from pylons.controllers.util import abort
from fts3.model import CloudStorage, CloudStorageUser

import urllib
import urllib2

#Url = 'https://api.dropbox.com'
dropboxEndpoint = "https://www.dropbox.com"
dropboxApiEndpoint = "https://api.dropbox.com"


class DropboxConnector(object):

    def __init__(self, userDN, service):
        self.service = service.strip().upper()
        self.userDN = userDN.strip()


    @jsonify
    def isCSRegistered(self):
        info = self._getDropboxUserInfo()
        return info.isRegistered()


    def getCSAccessRequested(self):
        dropboxInfo = self._getDropboxInfo()
        requestTokens = self._makeCall(dropboxApiEndpoint + "/1/oauth/request_token", 'OAuth oauth_version="1.0", oauth_signature_method="PLAINTEXT", oauth_consumer_key="' + dropboxInfo.app_key + '", oauth_signature="' + dropboxInfo.app_secret + '&"', None)
        #url = apiUrl + '/1/oauth/request_token'
        #headers = { 'Authorization' : 'OAuth oauth_version="1.0", oauth_signature_method="PLAINTEXT", oauth_consumer_key="' + app_key + '", oauth_signature="' + app_secret + '"' }
        #values = {}
        #data = urllib.urlencode(values)
        #req = urllib2.Request(url, data, headers)
        #response = urllib2.urlopen(req)
        #return response.read()

        #It returns: oauth_token_secret=b9q1n5il4lcc&oauth_token=mh7an9dkrg59
        rTokens = requestTokens.split('&')
        newuser = CloudStorageUser(user_dn=self.userDN, cloudStorage_name=dropboxInfo.cloudStorage_name, request_token=rTokens[1].split('=')[1], request_token_secret=rTokens[0].split('=')[1])
        Session.add(newuser)
        Session.commit()

        return requestTokens

    @jsonify
    def isCSAccessRequested(self):
        info = self._getDropboxUserInfo()
        if (info is None):
            raise HTTPNotFound('No registered user for the service "%s" has been found' % self.service)

        if info.isRegistered() == True:
            res = self._getCSContent("/")
            if res.startswith("401"):
                Session.delete(info)
                Session.commit()
                raise HTTPNotFound('No registered user for the service "%s" has been found' % self.service)

        return info;


    def getCSAccessGranted(self):
        dropboxUserInfo = self._getDropboxUserInfo()
        dropboxInfo = self._getDropboxInfo()

        accessTokens = self._makeCall(dropboxApiEndpoint + "/1/oauth/access_token", 'OAuth oauth_version="1.0", oauth_signature_method="PLAINTEXT", oauth_consumer_key="' + dropboxInfo.app_key + '", oauth_token="' + dropboxUserInfo.request_token + '", oauth_signature="' + dropboxInfo.app_secret + '&' + dropboxUserInfo.request_token_secret + '"', None)

        #It returns: oauth_token=<access-token>&oauth_token_secret=<access-token-secret>&uid=<user-id>
        aTokens = accessTokens.split('&')
        dropboxUserInfo.access_token = aTokens[1].split('=')[1]
        dropboxUserInfo.access_token_secret= aTokens[0].split('=')[1]
        #Resquest tokens are not needed anymore. Store something not None to mark them as done
        #dropboxUserInfo.request_token = ""
        #dropboxUserInfo.request_token_secret = ""
        Session.add(dropboxUserInfo)
        Session.commit()

        return accessTokens

    def getCSFolderContent(self):
        #If we are receiving "null" means that the user is asking for the root folder
        #abort(403, 'Correct path?? %s' % urllib.unquote(folderPath))
        surl = self._get_valid_surl()

        return self._getCSContent(surl)
#        if path == None:
#            path = "/"
#        else:
#            path = "/" + urllib.unquote(path)
#            import logging
#            log = logging.getLogger(__name__)
#            log.info("Init folder path received: " + path)
#            log.info("Transformed folder path: " + urllib.unquote(path))

        #if folderPath == "null":
        #    folderPath = "/"
        # "dropbox" could be also "sandbox"
    def _getCSContent(self, surl):
        return self._makeCall(dropboxApiEndpoint + "/1/metadata/dropbox" + surl, self._getAuthKey(), "list=true")


    def getCSFileLink(self, path):
        # "dropbox" could be also "sandbox"
        return self._makeCall(dropboxApiEndpoint + "/1/media/dropbox/" + path, self._getAuthKey())

    #Internal functions

    def _getDropboxUserInfo(self):
        dropboxUserInfo = Session.query(CloudStorageUser).get((self.userDN, self.service))
       # if dropboxUserInfo is None:
       #     abort(403, 'No registration information found for the user "%s" in the service %s' % (self.userDN, self.service))
        return dropboxUserInfo

    def _get_valid_surl(self):
        surl = request.params.get('surl')
        if not surl:
            raise HTTPBadRequest('Missing surl parameter')
        parsed = urlparse.urlparse(surl)
        if parsed.scheme in ['file']:
            raise HTTPBadRequest('Forbiden SURL scheme')
        return str(surl)

    def _getDropboxInfo(self):
        dropboxInfo = Session.query(CloudStorage).get(self.service)
       # if dropboxInfo is None:
        #    abort(403, 'No registration information found for the service %s' % self.service)
        return dropboxInfo


    def _getAuthKey(self):
        dropboxUserInfo = self._getDropboxUserInfo()
        dropboxInfo = self._getDropboxInfo()
        return 'OAuth oauth_version="1.0", oauth_signature_method="PLAINTEXT", oauth_consumer_key="' + dropboxInfo.app_key + '", oauth_token="' + dropboxUserInfo.access_token + ', oauth_signature="' + dropboxInfo.app_secret + '&' + dropboxUserInfo.access_token_secret + '"'


    def _makeCall(self, commandUrl, commandAuthHeaders, parameters):
        if parameters is not None:
            commandUrl += '?' + parameters
        headers = { 'Authorization' : commandAuthHeaders }
        values = {}

        try:
            data = urllib.urlencode(values)
            req = urllib2.Request(commandUrl, data, headers)
            response = urllib2.urlopen(req)
            res_con = response.read()
            return res_con
        except Exception, e:
            print e.code
            print e.read()
            return str(e.code) + e.read()
