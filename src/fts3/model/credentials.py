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

from base import Base
from datetime import datetime, timedelta
from sqlalchemy import Column, DateTime, Text, String


class CredentialCache(Base):
    __tablename__ = 't_credential_cache'

    dlg_id       = Column(String(16), primary_key=True)
    dn           = Column(String(255), primary_key=True)
    cert_request = Column(Text)
    priv_key     = Column(Text)
    voms_attrs   = Column(Text)


class Credential(Base):
    __tablename__ = 't_credential'

    dlg_id           = Column(String(16), primary_key=True)
    dn               = Column(String(255), primary_key=True)
    proxy            = Column(Text)
    voms_attrs       = Column(Text)
    termination_time = Column(DateTime(timezone = True))

    def expired(self):
        return self.termination_time <= datetime.utcnow()

    def remaining(self):
        return self.termination_time - datetime.utcnow()


class AuthorizationByDn(Base):
    __tablename__ = 't_authz_dn'

    dn        = Column(String(255), primary_key=True)
    operation = Column(String(64), primary_key=True)
