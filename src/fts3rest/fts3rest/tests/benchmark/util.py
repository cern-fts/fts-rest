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

from sqlalchemy import create_engine
import logging
import pycallgraph
import sys

from fts3rest.model import Base, Session


def setup_logging(log_queries):
    """
    Configure the logging of the benchmark, and SqlAlchemy

    Args:
        log_queries: If True, the logging of the queries will go to stderr

    Returns:
        The logger for the benchmark
    """
    formatter = logging.Formatter("%(levelname)s\t%(message)s")
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    stdout_handler.setFormatter(formatter)
    if log_queries:
        sqlalchemy_logger = logging.getLogger("sqlalchemy.engine")
        sqlalchemy_logger.setLevel(logging.INFO)
        sqlalchemy_logger.addHandler(stderr_handler)

    benchmark_logger = logging.getLogger("benchmark")
    benchmark_logger.setLevel(logging.INFO)
    benchmark_logger.addHandler(stdout_handler)

    return benchmark_logger


def setup_database(db_connect, proxy=None):
    """
    Setup the database connection

    Args:
        db_connect: A valid connection string for SqlAlchemy
        proxy: An instance of ConnectionProxy (i.e QueryCounter)
    """
    log = logging.getLogger('benchmark')
    log.info("Connecting to the database %s" % db_connect)
    db_engine = create_engine(db_connect, proxy=proxy)
    Session.configure(bind=db_engine)
    Base.metadata.bind = Session.bind
    Base.metadata.create_all(checkfirst=True)


class ProfiledFunction(object):
    """
    Wraps the callable f, and generated a callgraph when called
    """

    def __init__(self, func):
        pycallgraph.reset_trace()
        self.func = func

    def __call__(self, *args, **kwargs):
        pycallgraph.start_trace(reset=False)
        return_value = self.func(*args, **kwargs)
        pycallgraph.stop_trace()
        return return_value

    def generate_callgraph(self, output_filename):
        pycallgraph.make_dot_graph(output_filename)


__all__ = ["setup_logging", "setup_database", "ProfiledFunction"]
