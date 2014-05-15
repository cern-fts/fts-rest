#   Copyright notice:
#   Copyright © Members of the EMI Collaboration, 2010.
# 
#   See www.eu-emi.eu for details on the copyright holders
# 
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
# 
#       http://www.apache.org/licenses/LICENSE-2.0
# 
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import sqlalchemy
from base import Base
from banned import *
from config import *
from credentials import *
from file import *
from job import *
from optimizer import *
from version import *


# Convenience method
def connect(connectString):
    engine = sqlalchemy.create_engine(connectString)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    #Base.metadata.create_all(engine)
    return Session()
