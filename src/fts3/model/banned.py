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
from sqlalchemy import Column, DateTime
from sqlalchemy import Integer, String


class BannedDN(Base):
    __tablename__ = 't_bad_dns'

    dn            = Column(String(256), primary_key=True)
    message       = Column(String(256))
    addition_time = Column(DateTime)
    admin_dn      = Column(String(1024))
    status        = Column(String(10))


class BannedSE(Base):
    __tablename__ = 't_bad_ses'

    se            = Column(String(256), primary_key=True)
    message       = Column(String(256))
    addition_time = Column(DateTime)
    admin_dn      = Column(String(1024))
    vo            = Column(String(100), primary_key=True, nullable=True)
    status        = Column(String(10))

