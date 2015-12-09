#   Copyright notice:
#   Copyright CERN, 2014.
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

from sqlalchemy import Column, DateTime, Boolean, String

from base import Base


class Host(Base):
    __tablename__ = 't_hosts'

    hostname     = Column(String(64), primary_key=True)
    service_name = Column(String(64), primary_key=True)
    beat         = Column(DateTime)
    drain        = Column(Boolean)
