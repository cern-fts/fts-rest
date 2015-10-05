#!/usr/bin/env python

#   Copyright notice:
#   Copyright CERN, 2014.
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

import imp
import logging
import os
import sys
from datetime import date


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def _add_to_syspath(base_dir, components):
    path = base_dir
    for c in components:
        path = os.path.join(path, c)
    path = os.path.abspath(path)
    sys.path.append(path)

_base_dir = os.path.dirname(__file__)
_add_to_syspath(_base_dir, ('..', 'src'))


from fts3.cli.base import Base


def sanitize_text(text, **kwargs):
    """
    See how many spaces on the first line, and remove those for all the rest,
    so the visual indent is kept
    """
    lines = text.split('\n')
    if len(lines) == 0:
        return ''
    # Skip first white line
    if len(lines[0]) == 0:
        del lines[0]
    n_spaces = 0
    for c in lines[0]:
        if c.isspace():
            n_spaces += 1
        else:
            break
    return "\n".join(map(lambda l: l[n_spaces:], lines)) % kwargs


def process_cli_impl(cli_name, impl, output_base_path):
    log.debug("Generating doc for %s" % cli_name)
    instance = impl()

    # Override prog
    instance.opt_parser.prog = cli_name

    usage = instance.opt_parser.get_usage()

    output_path = os.path.join(output_base_path, cli_name) + '.md'
    md_file = open(output_path, 'wt')

    print >>md_file, "%% FTS-REST-CLI(1) %s" % cli_name
    print >>md_file, "% fts-devel@cern.ch"
    print >>md_file, "%% %s" % date.today().strftime("%B %d, %Y")

    print >>md_file, "# NAME\n"
    print >>md_file, "%s\n" % cli_name
    print >>md_file, "# SYNOPIS\n"
    print >>md_file, usage

    print >>md_file, "# DESCRIPTION\n"
    try:
        description = sanitize_text(instance.opt_parser.get_description())
        print >>md_file, "%s\n" % description
    except:
        description = ""

    print >>md_file, "# OPTIONS\n"
    options = str()
    for option in instance.opt_parser.option_list:
        option_line = "%s\n:\t%s\n\n" % (str(option), ". ".join(map(lambda s: s.strip().capitalize(), option.help.split('.'))))
        print >>md_file, option_line,
        options += option_line

    if instance.opt_parser.epilog:
        epilog = sanitize_text(instance.opt_parser.epilog, prog=cli_name)
        print >>md_file, "# EXAMPLE"
        print >>md_file, "```\n%s\n```\n" % epilog,
    else:
        epilog = ""

    md_file.close()

    return cli_name, usage, description, options, epilog


def generate_index(cli_list, output_base_path):
    log.debug("Generatic index")
    output_path = os.path.join(output_base_path, 'README.md')
    md_file = open(output_path, 'wt')

    print >>md_file, '# FTS3 REST Command Line Tools'
    print >>md_file
    for name, usage, description, options, epilog in cli_list:
        print >>md_file, '##', name
        print >>md_file, description
        print >>md_file, '### Usage'
        print >>md_file, usage
        print >>md_file, '### Options'
        print >>md_file, options
        if epilog:
            print >>md_file, '### Example'
            print >>md_file, '```'
            print >>md_file, epilog
            print >>md_file, '```'


def process_cli_file(path, output_base_path):
    cli_name = os.path.basename(path)
    module_name = cli_name.replace('-', '_')
    try:
        module = imp.load_source(module_name, path)
        for symbol in dir(module):
            elm = getattr(module, symbol)
            if isinstance(elm, type) and issubclass(elm, Base):
                return process_cli_impl(cli_name, elm, output_base_path)
    except SyntaxError:
        log.debug("%s is not a Python file" % path)
        return None


def process_all_cli(cli_base_path):
    cli_list = []
    for cli_file in os.listdir(cli_base_path):
        cli_path = os.path.join(cli_base_path, cli_file)
        spec = process_cli_file(cli_path, output_base_path)
        if spec:
            cli_list.append(spec)
    generate_index(cli_list, output_base_path)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        output_base_path = sys.argv[1]
    else:
        output_base_path = os.path.join(_base_dir, 'cli')

    cli_base_path = os.path.join(_base_dir, '..', 'src', 'cli')
    log.debug("CLI directory: %s" % cli_base_path)
    log.debug("Output path: %s" % output_base_path)
    process_all_cli(cli_base_path)
