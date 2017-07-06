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

from sqlalchemy import Column, DateTime, Float, Integer, String, Text, ForeignKeyConstraint

from base import Base, Flag


class OptimizerEvolution(Base):
    __tablename__ = 't_optimizer_evolution'

    datetime   = Column(DateTime, primary_key=True)
    source_se  = Column(String(150), primary_key=True)
    dest_se    = Column(String(150), primary_key=True)
    active     = Column(Integer)
    throughput = Column(Float)
    success    = Column(Float)
    rationale  = Column(Text)
    diff       = Column(Integer)
    actual_active = Column(Integer)
    queue_size    = Column(Integer)
    ema         = Column(Float)
    filesize_avg = Column(Float)
    filesize_stddeve = Column(Float)


class OptimizerActive(Base):
    __tablename__ = 't_optimize_active'

    source_se = Column(String(150), primary_key=True)
    dest_se   = Column(String(150), primary_key=True)
    active    = Column(Integer, default=5)
    datetime  = Column(DateTime, default=None)
    ema       = Column(Float, default=0)
    fixed     = Column(Flag(negative='off', positive='on'), default='off')
    min_active = Column(Integer, default=None)
    max_active = Column(Integer, default=None)


class OptimizerStreams(Base):
    __tablename__ = 't_optimize_streams'

    source_se  = Column(String(150), primary_key=True)
    dest_se    = Column(String(150), primary_key=True)
    nostreams  = Column(Integer, primary_key=True)
    datetime   = Column(DateTime)
    throughput = Column(Float)
    tested     = Column(Integer, default=0)

    __table_args__ = (
        ForeignKeyConstraint(['source_se', 'dest_se'],
                             [OptimizerActive.source_se, OptimizerActive.dest_se]),
    )


class Optimize(Base):
    __tablename__ = 't_optimize'

    auto_number = Column(Integer, autoincrement=True, primary_key=True)
    source_se  = Column(String(150), nullable=True)
    dest_se    = Column(String(150), nullable=True)
    active     = Column(Integer)
    throughput = Column(Float)
    datetime   = Column(DateTime)
    udt        = Column(Flag(negative='off', positive='on'))
    ipv6       = Column(Flag(negative='off', positive='on'), default='off')
