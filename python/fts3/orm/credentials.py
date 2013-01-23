from sqlalchemy import Column, DateTime, LargeBinary, String

from base import Base

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
