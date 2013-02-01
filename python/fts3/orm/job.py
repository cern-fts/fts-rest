from sqlalchemy import Column, DateTime, Integer, String 
from sqlalchemy.orm import relation, backref

from base import Base

JobActiveStates = ['SUBMITTED', 'READY', 'ACTIVE']

class Job(Base):
	__tablename__ = 't_job'
    
	job_id                   = Column(String(36), primary_key = True)
	job_state                = Column(String(32))
	reuse_job                = Column(String(3))
	cancel_job               = Column(String(1))
	job_params               = Column(String(255))
	submitHost               = Column(String(255))
	source                   = Column(String(255))
	dest                     = Column(String(255))
	source_se                = Column(String(255))
	dest_se                  = Column(String(255))
	user_dn                  = Column(String(1024))
	agent_dn                 = Column(String(1024))
	user_cred                = Column(String(255))
	cred_id                  = Column(String(100))
	voms_cred                = Column(String)
	vo_name                  = Column(String(50))
	reason                   = Column(String(2048))
	submit_time              = Column(DateTime)
	finish_time              = Column(DateTime)
	priority                 = Column(Integer)
	max_time_in_queue        = Column(Integer)
	space_token              = Column(String(255))
	storage_class            = Column(String(255))
	myproxy_server           = Column(String(255))
	src_catalog              = Column(String(1024))
	src_catalog_type         = Column(String(1024))
	dest_catalog             = Column(String(1024))
	dest_catalog_type        = Column(String(1024))
	internal_job_params      = Column(String(255))
	overwrite_flag           = Column(String(1))
	job_finished             = Column(DateTime)
	source_space_token       = Column(String(255))
	source_token_description = Column(String(255)) 
	copy_pin_lifetime        = Column(Integer)
	lan_connection           = Column(String(1))
	fail_nearline            = Column(String(1))
	checksum_method          = Column(String(1))
	bring_online             = Column(Integer)
	job_metadata             = Column(String(255))
	
	
	files = relation("File", uselist = True, lazy = True,
					 backref = backref("job", lazy = False))
	
	def isFinished(self):
		return self.job_state not in JobActiveStates
	
	def __str__(self):
		return self.job_id
