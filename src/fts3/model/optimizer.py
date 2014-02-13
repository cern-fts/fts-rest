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
