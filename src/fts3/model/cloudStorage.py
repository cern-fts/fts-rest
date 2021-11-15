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

from sqlalchemy import Column, String, ForeignKey, DateTime
from datetime import datetime, timedelta

from base import Base


class CloudStorage(Base):
    __tablename__ = 't_cloudStorage'

    storage_name    = Column(String(150), primary_key=True, name='cloudStorage_name')
    app_key         = Column(String(255))
    app_secret      = Column(String(255))
    service_api_url = Column(String(1024))
    keystone_url    = Column(String(255))
    keystone_idp    = Column(String(50))


class CloudStorageUser(Base):
    __tablename__ = 't_cloudStorageUser'

    user_dn              = Column(String(700), primary_key=True)
    storage_name         = Column(String(150), ForeignKey('t_cloudStorage.cloudStorage_name'),
                                  primary_key=True, name='cloudStorage_name')
    access_token         = Column(String(255))
    access_token_secret  = Column(String(255))
    request_token        = Column(String(255))
    request_token_secret = Column(String(255))
    os_token             = Column(String(255))
    os_project_id        = Column(String(255))
    vo_name              = Column(String(100), primary_key=True)

    def is_access_requested(self):
        return not (self.request_token is None or self.request_token_secret is None)

    def is_registered(self):
        return not (self.access_token is None or self.access_token_secret is None)


class CloudCredentialCache(Base):
    __tablename__ = 't_cloudCredentialCache'

    user_dn              = Column(String(700), primary_key=True)
    storage_name         = Column(String(150), ForeignKey('t_cloudStorage.cloudStorage_name'),
                                  primary_key=True, name='cloudStorage_name')
    os_project_id        = Column(String(255), primary_key=True)
    os_token             = Column(String(255))
    os_token_recvtime    = Column(DateTime(timezone=True))

    def os_token_is_expired(self):
        if self.os_token_recvtime:
            return datetime.utcnow() - self.os_token_recvtime >= timedelta(hours=6)
        return False
