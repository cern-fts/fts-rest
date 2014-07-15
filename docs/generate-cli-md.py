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

    output_path = os.path.join(output_base_path, cli_name) + '.md'
    md_file = open(output_path, 'wt')

    md_file.write("%% FTS-REST-CLI(1) %s\n" % cli_name)
    md_file.write("% fts-devel@cern.ch\n")
    md_file.write("%% %s\n" % date.today().strftime("%B %d, %Y"))

    md_file.write("# NAME\n\n")
    md_file.write("%s\n\n" % cli_name)
    md_file.write("# SYNOPIS\n\n")
    md_file.write("%s\n" % instance.opt_parser.get_usage())

    md_file.write("# DESCRIPTION\n\n")
    try:
        description = sanitize_text(instance.opt_parser.get_description())
        md_file.write("%s\n\n" % description)
    except:
        pass

    md_file.write("# OPTIONS\n\n")
    for option in instance.opt_parser.option_list:
        md_file.write(
            "%s\n:\t%s\n\n" % (str(option), ". ".join(map(lambda s: s.strip().capitalize(), option.help.split('.'))))
        )

    if instance.opt_parser.epilog:
        epilog = sanitize_text(instance.opt_parser.epilog, prog=cli_name)
        md_file.write("# EXAMPLE\n")
        md_file.write("```\n%s\n```\n" % epilog)

    md_file.close()


def process_cli_file(path, output_base_path):
    cli_name = os.path.basename(path)
    module_name = cli_name.replace('-', '_')
    try:
        module = imp.load_source(module_name, path)
        for symbol in dir(module):
            elm = getattr(module, symbol)
            if isinstance(elm, type) and issubclass(elm, Base):
                process_cli_impl(cli_name, elm, output_base_path)
    except SyntaxError:
        log.debug("%s is not a Python file" % path)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        output_base_path = sys.argv[1]
    else:
        output_base_path = os.path.join(_base_dir, 'cli')

    cli_base_path = os.path.join(_base_dir, '..', 'src', 'cli')
    log.debug("CLI directory: %s" % cli_base_path)
    log.debug("Output path: %s" % output_base_path)
    for cli_file in os.listdir(cli_base_path):
        cli_path = os.path.join(cli_base_path, cli_file)
        process_cli_file(cli_path, output_base_path)
