import sqlalchemy
from base        import Base
from banned      import *
from config      import *
from credentials import *
from file        import *
from job         import *
from optimizer   import *
from version     import *

# Convenience method
def connect(connectString):
	engine = sqlalchemy.create_engine(connectString)
	Session = sqlalchemy.orm.sessionmaker(bind = engine)
	#Base.metadata.create_all(engine)
	return Session()	
