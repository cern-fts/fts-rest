from base import Base
from datetime import datetime, timedelta 
from sqlalchemy import Column, DateTime, Binary, String


class CredentialCache(Base):
	__tablename__ = 't_credential_cache'
	
	dlg_id       = Column(String(100), primary_key = True)
	dn           = Column(String(255), primary_key = True)
	cert_request = Column(Binary)
	priv_key     = Column(Binary)
	voms_attrs   = Column(Binary)


class Credential(Base):
	__tablename__ = 't_credential'
	
	dlg_id           = Column(String(100), primary_key = True)
	dn               = Column(String(255), primary_key = True)
	proxy            = Column(Binary)
	voms_attrs       = Column(Binary)
	termination_time = Column(DateTime)
	
	def expired(self):
		return self.termination_time <= datetime.now() 
	
	def remaining(self):
		return self.termination_time - datetime.now() 
