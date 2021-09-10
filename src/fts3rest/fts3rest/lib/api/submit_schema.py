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
        'priority': {
            'type': ['integer', 'null'],
            'title': 'Job priority'
        },
        'metadata':     {'type': ['object', 'null']},
        'filesize':     {'type': ['integer', 'null'], 'minimum': 0},
        'checksum':     {
            'type': ['string', 'null'],
            'title': 'User defined checksum in the form algorithm:value'
        },
        'activity': {
            'type': ['string', 'null'],
            'title': 'Activity share'
        }
    },
}

paramSchema = {
    'title': 'Job parameters',
    'type': ['object', 'null'],
    'properties': {
        'verify_checksum': {
            'type': ['boolean', 'null']
        },
        'reuse': {
            'type': ['boolean', 'null'],
            'title': 'If set to true, srm sessions will be reused'
        },
        'spacetoken': {
            'type': ['string', 'null'],
            'title': 'Destination space token'
        },
        'bring_online': {
            'type': ['integer', 'null'],
            'title': 'Bring online operation timeout'
        },
        'copy_pin_lifetime': {
            'type': ['integer', 'null'],
            'title': 'Minimum lifetime when bring online is used. -1 means no bring online',
            'minimum': -1
        },
        'job_metadata': {
            'type': ['object', 'null']
        },
        'source_spacetoken': {
            'type': ['string', 'null']
        },
        'overwrite': {
            'type': ['boolean', 'null']
        },
        'dst_file_report': {
            'type': ['boolean', 'null']
        },
        'gridftp': {
            'type': ['string', 'null'],
            'title': 'Reserved for future usage'
        },
        'retry': {'type': ['integer', 'null']},
        'multihop': {
            'type': ['boolean', 'null']
        },
        'timeout': {
            'type': ['integer', 'null'],
            'title': 'Timeout in seconds'
        },
        'nostreams': {
            'type': ['integer', 'null'],
            'title': 'Number of streams'
        },
        'buffer_size': {
            'type': ['integer', 'null'],
            'title': 'Buffer size'
        },
        'strict_copy': {
            'type': ['boolean', 'null'],
            'title': 'Disable all checks, just copy the file'
        },
        'priority': {
            'type': ['integer', 'null'],
            'title': 'Job priority'
        },
        'ipv4': {
            'type': ['boolean', 'null'],
            'title': 'Force IPv4 if the underlying protocol supports it'
        },
        'ipv6': {
            'type': ['boolean', 'null'],
            'title': 'Force IPv6 if the underlying protocol supports it'
        }
    }
}

deleteSchema = {
    'type': ['object', 'string']
}

SubmitSchema = {
    'title':      'Job submission',
    'type':       'object',
    'properties': {
        'params': paramSchema,
        'files': {
            'type': 'array',
            'items': fileSchema
        },
        'delete': {
            'type': 'array',
            'items': deleteSchema
        }
    }
}
