from base import Base
from datetime import datetime, timedelta 
from sqlalchemy import Column, DateTime, LargeBinary, String


class CredentialCache(Base):
	__tablename__ = 't_credential_cache'
	
	dlg_id       = Column(String(100), primary_key = True)
	dn           = Column(String(255), primary_key = True)
	cert_request = Column(LargeBinary)
	priv_key     = Column(LargeBinary)
	voms_attrs   = Column(LargeBinary)


class Credential(Base):
	__tablename__ = 't_credential'
	
	dlg_id           = Column(String(100), primary_key = True)
	dn               = Column(String(255), primary_key = True)
	proxy            = Column(LargeBinary)
	voms_attrs       = Column(LargeBinary)
	termination_time = Column(DateTime)
	
	def expired(self):
		return self.termination_time <= datetime.now() 
	
	def remaining(self):
		return self.termination_time - datetime.now() 
