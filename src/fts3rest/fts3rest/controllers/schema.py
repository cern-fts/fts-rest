from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from pylons import request

def _schema():
    urlSchema = {
        'title': 'URL',
        'type':  'string'
    }
        
    fileSchema = {
        'title': 'Transfer',
        'type':  'object',
        'required': ['sources', 'destinations'],
        'properties': {
            'sources':      {'type': 'array', 'items': urlSchema, 'minItems': 1},
            'destinations': {'type': 'array', 'items': urlSchema, 'minItems': 1},
            'metadata':     {'type': ['object', 'null']},
            'filesize':     {'type': ['integer','null'], 'minimum': 0},
            'checksum':     {'type': ['string', 'null'], 'title': 'User defined checksum in the form algorithm:value'}
        },
    }
    
    paramSchema = {
        'title': 'Job parameters',
        'type': ['object', 'null'],
        'properties': {
            'verify_checksum':   {'type': ['boolean', 'null']},
            'reuse':             {'type': ['boolean', 'null'], 'title': 'If set to true, srm sessions will be reused'},
            'spacetoken':        {'type': ['string', 'null'], 'title': 'Destination space token'},
            'bring_online':      {'type': ['integer', 'null'], 'title': 'Bring online operation timeout'},
            'copy_pin_lifetime': {'type': ['integer', 'null'], 'title': 'Minimum lifetime when bring online is used. -1 means no bring online', 'minimum': -1},
            'job_metadata':      {'type': ['object', 'null']},
            'source_spacetoken': {'type': ['string', 'null']},
            'overwrite':         {'type': ['boolean', 'null']},
            'gridftp':           {'type': ['string', 'null'], 'title': 'Reserved for future usage'},
            'retry':             {'type': ['integer', 'null']}
        },
    }
        
    schema = {
        'title':      'Job submission',
        'type':       'object',
        'required':   ['files'],
        'properties': {
            'params': paramSchema,
            'files': {'type': 'array',
                      'items': fileSchema}
                     }
    }
    
    return schema

class SchemaController(BaseController):
     
    @jsonify
    def submit(self):
        """
        Return the json-schema for the submission operation, so it can
        be used to validate
        """
        return _schema()
