from sqlalchemy import Column, DateTime, Float, Integer, String

from base import Base


class OptimizerEvolution(Base):
    __tablename__ = 't_optimizer_evolution'
    
    datetime   = Column(DateTime(), primary_key = True)
    source_se  = Column(String(), primary_key = True)
    dest_se    = Column(String(), primary_key = True)
    nostreams  = Column(Integer())
    timeout    = Column(Integer())
    active     = Column(Integer())
    throughput = Column(Float())
    buffer     = Column(Integer())
    filesize   = Column(Integer())


class Optimizer(Base):
    __tablename__ = 't_optimize'
    
    source_se  = Column(String(), primary_key = True)
    dest_se    = Column(String(), primary_key = True)
    nostreams  = Column(Integer(), primary_key = True)
    timeout    = Column(Integer(), primary_key = True)
    active     = Column(Integer(), primary_key = True)
    buffer     = Column(Integer(), primary_key = True)
    #filesize   = Column(Integer(), primary_key = True)
    datetime   = Column(DateTime())
    throughput = Column(Float())
