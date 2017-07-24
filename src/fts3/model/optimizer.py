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
    filesize_stddev = Column(Float)



class Optimizer(Base):
    __tablename__ = 't_optimizer'

    source_se  = Column(String(150), nullable=True, primary_key=True)
    dest_se    = Column(String(150), nullable=True, primary_key=True)
    ema        = Column(Float)
    active     = Column(Integer)
    datetime   = Column(DateTime)
    nostreams  = Column(Integer)
    def __str__(self):
        return "%s => %s" % (self.source_se, self.dest_se)
    
