from sqlalchemy import Column, DateTime, Float
from sqlalchemy import ForeignKey, Integer, String

from base import Base

class File(Base):
	__tablename__ = 't_file'
	
	file_id      	     = Column(Integer, primary_key = True)
	job_id         	     = Column(String(36), ForeignKey('t_job.job_id'))
	symbolicName 	     = Column(String(255))
	file_state   	     = Column(String(32))
	transferHost 	     = Column(String(255))
	logical_name 	     = Column(String(1100))
	source_surl          = Column(String(1100))
	dest_surl            = Column(String(1100))
	agent_dn             = Column(String(1024))
	error_scope          = Column(String(32))
	error_phase          = Column(String(32))
	reason_class         = Column(String(32))
	reason               = Column(String(2048))
	num_failures         = Column(Integer)
	current_failures     = Column(Integer)
	catalog_failures     = Column(Integer)
	prestage_failures    = Column(Integer)
	filesize             = Column(Integer)
	checksum             = Column(String(100))
	finish_time          = Column(DateTime)
	start_time           = Column(DateTime)
	internal_file_params = Column(String(255))
	job_finished         = Column(DateTime)
	pid          	     = Column(Integer)
	tx_duration  	     = Column(Float)
	throughput   	     = Column(Float)
	retry       	     = Column(Integer)
	
	def isFinished(self):
		return self.job_state in ['SUBMITTED', 'READY', 'ACTIVE']
	
	def __str__(self):
		return str(self.file_id)
