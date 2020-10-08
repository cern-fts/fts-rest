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
from sqlalchemy import BigInteger
from sqlalchemy import Boolean, Column, DateTime, Float
from sqlalchemy import ForeignKey, Integer, String, Enum, UniqueConstraint
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import relation, backref

from base import Base, Json

FileActiveStates = ['STAGING', 'STARTED', 'SUBMITTED', 'READY', 'ACTIVE', 'ARCHIVING', 'QOS_TRANSITION', 'QOS_REQUEST_SUBMITTED']
FileTerminalStates = ['FINISHED', 'FAILED', 'CANCELED']
# NOT_USED is not terminal, nor not-terminal
FileOnHoldStates = ['NOT_USED', 'ON_HOLD', 'ON_HOLD_STAGING']

# sqlite doesn't like auto increment with BIGINT, so we need to use a variant
# on that case
FileId = BigInteger().with_variant(sqlite.INTEGER(), 'sqlite')


class File(Base):
    __tablename__ = 't_file'

    file_id              = Column(FileId, primary_key=True)
    hashed_id            = Column(Integer)
    file_index           = Column(Integer)
    job_id               = Column(String(36), ForeignKey('t_job.job_id'))
    dest_surl_uuid       = Column(String(255), unique=True)
    vo_name              = Column(String(50))
    source_se            = Column(String(255))
    dest_se              = Column(String(255))
    priority             = Column(Integer)
    file_state           = Column(Enum(*(FileActiveStates + FileTerminalStates + FileOnHoldStates)))
    transfer_host        = Column(String(255))
    source_surl          = Column(String(1100))
    dest_surl            = Column(String(1100))
    staging_host         = Column(String(1024))
    reason               = Column(String(2048))
    recoverable          = Column('current_failures', Boolean)
    filesize             = Column(BigInteger)
    checksum             = Column(String(100))
    finish_time          = Column(DateTime)
    start_time           = Column(DateTime)
    archive_start_time   = Column(DateTime)
    archive_finish_time  = Column(DateTime)
    internal_file_params = Column(String(255))
    pid                  = Column(Integer)
    tx_duration          = Column(Float)
    throughput           = Column(Float)
    retry                = Column(Integer)
    user_filesize        = Column(BigInteger)
    file_metadata        = Column(Json(255))
    staging_start        = Column(DateTime)
    staging_finished     = Column(DateTime)
    selection_strategy   = Column(String(255))
    bringonline_token    = Column(String(255))
    log_file             = Column(String(2048))
    log_debug            = Column('log_file_debug', Integer)
    activity             = Column(String(255), default = 'default')

    retries = relation("FileRetryLog", uselist=True, lazy=True,
                       backref=backref("file", lazy=False))

    def isFinished(self):
        return self.job_state not in FileActiveStates

    def __str__(self):
        return str(self.file_id)


class ArchivedFile(Base):
    __tablename__ = 't_file_backup'

    file_id              = Column(FileId, primary_key=True)
    file_index           = Column(Integer)
    job_id               = Column(String(36),
                                  ForeignKey('t_job_backup.job_id'))
    dest_surl_uuid       = Column(String(255), unique=True)
    source_se            = Column(String(255))
    dest_se              = Column(String(255))
    priority             = Column(Integer)
    file_state           = Column(String(32))
    transferhost         = Column(String(255))
    source_surl          = Column(String(1100))
    dest_surl            = Column(String(1100))
    staging_host         = Column(String(1024))
    reason               = Column(String(2048))
    current_failures     = Column(Integer)
    filesize             = Column(BigInteger)
    checksum             = Column(String(100))
    finish_time          = Column(DateTime)
    start_time           = Column(DateTime)
    archive_start_time   = Column(DateTime)
    archive_finish_time  = Column(DateTime)
    internal_file_params = Column(String(255))
    job_finished         = Column(DateTime)
    pid                  = Column(Integer)
    tx_duration          = Column(Float)
    throughput           = Column(Float)
    retry                = Column(Integer)
    user_filesize        = Column(BigInteger)
    file_metadata        = Column(Json(255))
    staging_start        = Column(DateTime)
    staging_finished     = Column(DateTime)
    selection_strategy   = Column(String(255))
    bringonline_token    = Column(String(255))

    def __str__(self):
        return str(self.file_id)


class FileRetryLog(Base):
    __tablename__ = 't_file_retry_errors'

    file_id  = Column(Integer, ForeignKey('t_file.file_id'), primary_key=True)
    attempt  = Column(Integer, primary_key=True)
    datetime = Column(DateTime)
    reason   = Column(String(2048))

    def __str__(self):
        return "[%d:%d] %s" % (self.file_id, self.attempt, self.reason)
