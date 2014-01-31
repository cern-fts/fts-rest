from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, String
import json
import types


Base = declarative_base()


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
            return len(value) > 0 and value.upper() != self.negative


# This is used for the verify_checksum flag, which actually can be
# True, False and 'Relaxed' (r)
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
