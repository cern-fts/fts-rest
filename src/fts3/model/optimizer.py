#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2010.
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

from sqlalchemy import Column, DateTime, Float, Integer, String

from base import Base


class OptimizerEvolution(Base):
    __tablename__ = 't_optimizer_evolution'

    datetime   = Column(DateTime(), primary_key=True)
    source_se  = Column(String(), primary_key=True)
    dest_se    = Column(String(), primary_key=True)
    nostreams  = Column(Integer())
    timeout    = Column(Integer())
    active     = Column(Integer())
    throughput = Column(Float())
    branch     = Column(Integer(), name='buffer')
    success    = Column(Float(), name='filesize')


class OptimizerActive(Base):
    __tablename__ = 't_optimize_active'

    source_se = Column(String(255), primary_key=True)
    dest_se   = Column(String(255), primary_key=True)
    active    = Column(Integer(), default = 5)


class Optimize(Base):
    __tablename__ = 't_optimize'

    source_se = Column(String(), primary_key=True)
    dest_se   = Column(String(), primary_key=True)
    active    = Column(Integer())
    throughput = Column(Float())
