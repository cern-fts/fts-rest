from sqlalchemy import Column, Integer

from base import Base

class CredentialVersion(Base):
	__tablename__ = 't_credential_vers'
	
	major = Column(Integer, primary_key = True)
	minor = Column(Integer, primary_key = True)
	patch = Column(Integer, primary_key = True)
	
	def __str__(self):
		return "%d.%d.%d" % (self.major, self.minor, self.patch)



class SchemaVersion(Base):
	__tablename__ = 't_schema_vers'
	
	major = Column(Integer, primary_key = True)
	minor = Column(Integer, primary_key = True)
	patch = Column(Integer, primary_key = True)
	
	def __str__(self):
		return "%d.%d.%d" % (self.major, self.minor, self.patch)
