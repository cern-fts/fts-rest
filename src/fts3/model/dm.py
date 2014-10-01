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

from sqlalchemy import Column, DateTime, Float
from sqlalchemy import ForeignKey, Integer, String

from base import Base, Json


DataManagementActiveStates = ['DELETE']


class DataManagement(Base):
    __tablename__ = 't_dm'

    file_id              = Column(Integer, primary_key=True)
    job_id               = Column(String(36), ForeignKey('t_job.job_id'))
    file_state           = Column(String(32))
    dmHost               = Column('DMHOST', String(255))
    source_surl          = Column(String(900))
    dest_surl            = Column(String(900))
    source_se            = Column(String(150))
    dest_se              = Column(String(150))
    reason               = Column(String(2048))
    checksum             = Column(String(100))
    finish_time          = Column(DateTime)
    start_time           = Column(DateTime)
    job_finished         = Column(DateTime)
    tx_duration          = Column(Float)
    retry                = Column(Integer)
    user_filesize        = Column(Float)
    file_metadata        = Column(Json(1024))
    activity             = Column(String(255))
    dm_token             = Column(String(255))
    retry_timestamp      = Column(DateTime)
    wait_timestamp       = Column(DateTime)
    wait_timeout         = Column(Integer)
    hashed_id            = Column(Integer, default=0)
    vo_name              = Column(String(100))
