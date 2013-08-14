from file import ArchivedFile
from sqlalchemy import Column, DateTime, Integer, String 
from sqlalchemy.orm import relation, backref

from base import Base, Flag, Json

JobActiveStates = ['SUBMITTED', 'READY', 'ACTIVE', 'STAGING']

class Job(Base):
	__tablename__ = 't_job'
    
	job_id                   = Column(String(36), primary_key = True)
	source_se                = Column(String(255))
	dest_se                  = Column(String(255))
	job_state                = Column(String(32))
	reuse_job                = Column(Flag(negative = 'N'))
	cancel_job               = Column(Flag(negative = None))
	job_params               = Column(String(255))
	submit_host              = Column(String(255))
	user_dn                  = Column(String(1024))
	agent_dn                 = Column(String(1024))
	user_cred                = Column(String(255))
	cred_id                  = Column(String(100))
	vo_name                  = Column(String(50))
	reason                   = Column(String(2048))
	submit_time              = Column(DateTime)
	finish_time              = Column(DateTime)
	priority                 = Column(Integer)
	max_time_in_queue        = Column(Integer)
	space_token              = Column(String(255))
	internal_job_params      = Column(String(255))
	overwrite_flag           = Column(Flag)
	job_finished             = Column(DateTime)
	source_space_token       = Column(String(255))
	source_token_description = Column(String(255)) 
	copy_pin_lifetime        = Column(Integer)
	verify_checksum          = Column(Flag(positive = 'c'), name = 'checksum_method')
	bring_online             = Column(Integer)
	job_metadata             = Column(Json(255))
	retry                    = Column(Integer)
	
	
	files = relation("File", uselist = True, lazy = True,
					 backref = backref("job", lazy = True))
	
	def isFinished(self):
		return self.job_state not in JobActiveStates
	
	def __str__(self):
		return self.job_id


class ArchivedJob(Base):
	__tablename__ = 't_job_backup'

	job_id                   = Column(String(36), primary_key = True)
	source_se                = Column(String(255))
	dest_se                  = Column(String(255))
	job_state                = Column(String(32))
	reuse_job                = Column(Flag(negative = 'N'))
	cancel_job               = Column(Flag(negative = None))
	job_params               = Column(String(255))
	submit_host              = Column(String(255))
	user_dn                  = Column(String(1024))
	agent_dn                 = Column(String(1024))
	user_cred                = Column(String(255))
	cred_id                  = Column(String(100))
	vo_name                  = Column(String(50))
	reason                   = Column(String(2048))
	submit_time              = Column(DateTime)
	finish_time              = Column(DateTime)
	priority                 = Column(Integer)
	max_time_in_queue        = Column(Integer)
	space_token              = Column(String(255))
	internal_job_params      = Column(String(255))
	overwrite_flag           = Column(Flag)
	job_finished             = Column(DateTime)
	source_space_token       = Column(String(255))
	source_token_description = Column(String(255)) 
	copy_pin_lifetime        = Column(Integer)
	verify_checksum          = Column(Flag(positive = 'c'), name = 'checksum_method')
	bring_online             = Column(Integer)
	job_metadata             = Column(Json(255))
	retry                    = Column(Integer)
	
	files = relation("ArchivedFile", uselist = True, lazy = True,
					 backref = backref("job", lazy = True),
					 primaryjoin = (ArchivedFile.job_id == job_id))
	
	def __str__(self):
		return self.job_id
	
	