#!/usr/bin/env python

#   Copyright notice:
#   Copyright  Members of the EMI Collaboration, 2010.
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

import os
import sys


def _add_to_syspath(base_dir, components):
    path = base_dir
    for c in components:
        path = os.path.join(path, c)
    path = os.path.abspath(path)
    sys.path.append(path)

_base_dir = os.path.dirname(__file__)
_add_to_syspath(_base_dir, ('..', 'src'))
_add_to_syspath(_base_dir, ('..', 'src', 'fts3rest'))


from fts3rest.lib import api


class MarkDown(object):
    def __init__(self, stream):
        self.stream = stream

    def h1(self, msg):
        self.stream.write(msg.strip())
        self.stream.write('\n')
        self.stream.write('=' * len(msg.strip()))
        self.stream.write('\n')

    def h2(self, msg):
        self.stream.write(msg.strip())
        self.stream.write('\n')
        self.stream.write('-' * len(msg.strip()))
        self.stream.write('\n')

    def _h(self, n, msg):
        self.stream.write('#' * n + ' ')
        self.stream.write(msg.strip())
        self.stream.write('\n')

    def h3(self, msg):
        self._h(3, msg)

    def h4(self, msg):
        self._h(4, msg)

    def h5(self, msg):
        self._h(5, msg)

    def paragraph(self, msg):
        if msg:
            self.stream.write(msg.strip())
        self.stream.write('\n\n')

    def table(self, headers, rows):
        n_cols = len(headers)
        cols_width = [0] * n_cols
        # Figure out the width of the columns first
        for col in xrange(n_cols):
            header_len = len(headers[col])
            max_row_len = reduce(lambda a, b: max(a, b), map(lambda r: len(str(r[col])), rows))
            cols_width[col] = max(header_len, max_row_len)
        # Headers
        self.stream.write('\n')
        separator = ''
        for col in xrange(n_cols):
            self.stream.write(('|{0: <%d}' % cols_width[col]).format(headers[col]))
            separator += '|' + '-' * cols_width[col]
        self.stream.write('|\n')
        separator += '|\n'
        self.stream.write(separator)
        for row in rows:
            for col in xrange(n_cols):
                self.stream.write(('|{0: <%d}' % cols_width[col]).format(str(row[col])))
            self.stream.write('|\n')
        self.stream.write('\n')

    def href_to_header(self, header):
        link = '#' + header.lower().replace(' ', '-')
        return "[%s](%s)" % (header, link)


def write_markdown(resources, apis, models, md):
    filtered_models = filter(lambda m: len(m) > 0, models.values())
    model_dict = dict()
    available_models = list()
    for model_list in [ml for ml in filtered_models]:
        for model, model_desc in model_list.iteritems():
            model_dict[model] = model_desc
            available_models.append(model)

    md.h1('API')
    md.paragraph('This document has been generated automatically')

    for resource in sorted(resources):
        path = resource.get('path')
        description = resource.get('description', None)
        if not description:
            description = path
        md.h3(description)
        for call in apis[path]:
            path = call['path']
            for operation in call['operations']:
                md.h4("%s %s" % (operation['method'], path))
                md.paragraph(operation['summary'])

                type = operation.get('type', None)
                if type == 'array':
                    item_type = operation['items']['$ref']
                    if item_type in available_models:
                        type = 'Array of ' + md.href_to_header(item_type)
                    else:
                        type = 'Array of ' + item_type
                elif type and type in available_models:
                        type = md.href_to_header(type)

                if type:
                    md.h5('Returns')
                    md.paragraph(type)

                if operation['notes']:
                    md.h5('Notes')
                    md.paragraph(operation['notes'])

                parameters = operation['parameters']
                responses = operation['responseMessages']

                query_args = filter(lambda a: a['paramType'] == 'query', parameters)
                path_args = filter(lambda a: a['paramType'] == 'path', parameters)
                body_args = filter(lambda a: a['paramType'] == 'body', parameters)

                if path_args:
                    md.h5('Path arguments')
                    md.table(
                        ('Name', 'Type'),
                        map(lambda a: (a['name'], a['type']), path_args)
                    )
                if query_args:
                    md.h5('Query arguments')
                    md.table(
                        ('Name', 'Type', 'Required', 'Description'),
                        map(lambda a: (a['name'], a['type'], a['required'], a['description']), query_args)
                    )
                if body_args:
                    md.h5('Expected request body')
                    md.paragraph("%s (%s)" % (body_args[0]['description'], body_args[0]['type']))

                if responses:
                    md.h5('Responses')
                    md.table(
                        ('Code', 'Description'),
                        map(lambda r: (r['code'], r['message']), responses)
                    )
    md.h2('Models')
    printed_models = []
    for model, model_desc in model_dict.iteritems():
        if model not in printed_models:
            md.h3(model)
            fields = model_desc['properties']
            md.table(
                ('Field', 'Type'),
                map(lambda (name, desc): (name, desc['type']) ,fields.iteritems())
            )


if __name__ == '__main__':
    resources, apis, models = api.introspect()
    write_markdown(resources, apis, models, MarkDown(sys.stdout))
