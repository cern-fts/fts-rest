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

from distutils.version import StrictVersion
from sqlalchemy import Column, DateTime, ForeignKeyConstraint, Float
from sqlalchemy import Integer, String
from sqlalchemy import and_
from sqlalchemy import __version__ as sqlalchemy_version
from sqlalchemy.orm import relation

from base import Base, Flag, Json
from file import File


class  ConfigAudit(Base):
    __tablename__ = 't_config_audit'

    datetime = Column(DateTime, primary_key=True)
    dn       = Column(String(1024), primary_key=True)
    config   = Column(String(4000), primary_key=True)
    action   = Column(String(100), primary_key=True)

    def __str__(self):
        return "%s %s: %s" % (self.datetime, self.action, self.config)


class LinkConfig(Base):
    __tablename__ = 't_link_config'

    source            = Column(String(150), primary_key=True, name='source_se')
    destination       = Column(String(150), primary_key=True, name='dest_se')
    symbolicname      = Column(String(255), unique=True, name='symbolic_name')
    min_active        = Column(Integer)
    max_active        = Column(Integer)
    optimizer_mode    = Column(Integer)
    tcp_buffer_size   = Column(Integer)
    nostreams         = Column(Integer)
    no_delegation     = Column(Flag(negative='off', positive='on'), default='off')

    def __str__(self):
        return "%s => %s" % (self.source, self.destination)


class Se(Base):
    __tablename__ = 't_se'

    storage                 = Column(String(150), primary_key=True)
    site                    = Column(String(45))
    se_metadata             = Column(String(255), name='metadata')
    ipv6                    = Column(Integer)
    udt                     = Column(Integer)
    debug_level             = Column(Integer)
    inbound_max_active      = Column(Integer)
    inbound_max_throughput  = Column(Float)
    outbound_max_active     = Column(Integer)
    outbound_max_throughput = Column(Float)
    

    def __str__(self):
        return self.storage


class ShareConfig(Base):
    __tablename__ = 't_share_config'

    source      = Column(String(150), primary_key=True)
    destination = Column(String(150), primary_key=True)
    vo          = Column(String(100), primary_key=True)
    share       = Column(Integer, name='active')

    __table_args__ = (ForeignKeyConstraint(['source', 'destination'],
                                           [LinkConfig.source,
                                            LinkConfig.destination]),)

    def __str__(self):
        return "%s: %s => %s" % (self.vo, self.source, self.destination)


class ServerConfig(Base):
    __tablename__ = 't_server_config'

    retry          = Column(Integer, default=0)
    max_time_queue = Column(Integer, default=0)
    global_timeout = Column(Integer, default=0)
    sec_per_mb     = Column(Integer, default=0)
    vo_name        = Column(String(100), primary_key=True)
    no_streaming   = Column(Flag(negative='off', positive='on'), default='off')
    show_user_dn   = Column(Flag(negative='off', positive='on'), default='off')


class OperationConfig(Base):
    __tablename__ = 't_stage_req'

    vo_name        = Column(String(255), primary_key=True)
    host           = Column(String(255), primary_key=True)
    concurrent_ops = Column(Integer, default=0)
    operation      = Column(String(150), primary_key=True)


class ActivityShare(Base):
    __tablename__ = 't_activity_share_config'

    vo             = Column(String(100), primary_key=True)
    activity_share = Column(Json(1024))
    active         = Column(Flag(negative='off', positive='on'), default='on')
