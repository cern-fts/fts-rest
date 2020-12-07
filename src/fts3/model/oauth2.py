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

from base import Base, Set
from sqlalchemy import Column, String, DateTime, ForeignKey


class OAuth2Application(Base):
    __tablename__ = 't_oauth2_apps'

    client_id     = Column(String(64), nullable=False, primary_key=True)
    client_secret = Column(String(128), nullable=False)
    owner         = Column(String(1024), nullable=False)

    name          = Column(String(128), nullable=False, unique=True)
    description   = Column(String(512))
    website       = Column(String(1024))
    scope         = Column(Set(512), nullable=True)
    redirect_to   = Column(String(4096))


class OAuth2Code(Base):
    __tablename__ = 't_oauth2_codes'

    client_id = Column(String(64), nullable=False)
    code      = Column(String(128), nullable=False, primary_key=True)
    scope     = Column(Set(512), nullable=True)
    dlg_id    = Column(String(100), nullable=False)


class OAuth2Token(Base):
    __tablename__ = 't_oauth2_tokens'

    client_id     = Column(String(64), ForeignKey(OAuth2Application.client_id), nullable=False, primary_key=True)
    dlg_id        = Column(String(100), nullable=False)
    scope         = Column(Set(512), nullable=True)
    access_token  = Column(String(128), nullable=False)
    token_type    = Column(String(64), nullable=False)
    expires       = Column(DateTime, nullable=False)
    refresh_token = Column(String(128), nullable=False, primary_key=True)

class OAuth2Providers(Base):
    __tablename__ = 't_oauth2_providers'

    provider_url     = Column(String(250), nullable=False, primary_key=True)
    provider_jwk        = Column(String(1000), nullable=False)