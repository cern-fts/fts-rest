from base import Base
from sqlalchemy import Column, DateTime
from sqlalchemy import Integer, String


class BannedDN(Base):
	__tablename__ = 't_bad_dns'
	
	dn            = Column(String(256), primary_key = True)
	message       = Column(String(256))
	addition_time = Column(DateTime)
	admin_dn      = Column(String(1024))
