#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2013.
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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, String
import json
import types


class BaseAsDict(object):
    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        else:
            raise KeyError()

Base = declarative_base(cls=BaseAsDict)


class Json(TypeDecorator):
    impl = String

    def process_bind_param(self, value, dialect):
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        try:
            return json.loads(str(value))
        except ValueError:
            return str(value)


class Flag(TypeDecorator):
    impl = String

    def __init__(self, positive='Y', negative='', *args, **kwargs):
        super(Flag, self).__init__(1, *args, **kwargs)
        self.positive = positive
        self.negative = negative

    def process_bind_param(self, value, dialect):
        if isinstance(value, types.StringType):
            if len(value) > 0 and value[0].upper() == 'Y':
                return self.positive
            else:
                return self.negative
        elif value:
            return self.positive
        else:
            return self.negative

    def process_result_value(self, value, dialect):
        if value is None:
            return False
        else:
            return len(value) > 0 and value.upper() != self.negative.upper()


# This is used for flags that can be True, False, or some other thing
# i.e. verify_checksum flag, which can be True, False and 'Relaxed' (r)
#      reuse_job, which can be True, False and 'Multihop' (h)
class TernaryFlag(TypeDecorator):
    impl = String

    def __init__(self, positive='Y', negative='', *args, **kwargs):
        super(TernaryFlag, self).__init__(1, *args, **kwargs)
        self.positive = positive
        self.negative = negative

    def process_bind_param(self, value, dialect):
        if isinstance(value, types.StringType) and len(value):
            if value[0].upper() == 'Y':
                return self.positive
            elif value[0].upper() == 'N':
                return self.negative
            else:
                return value[0]
        elif value:
            return self.positive
        else:
            return self.negative

    def process_result_value(self, value, dialect):
        if value is None or len(value) == 0:
            return False
        elif value == self.negative:
            return False
        elif value == self.positive:
            return True
        else:
            return value
