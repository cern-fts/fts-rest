from sqlalchemy import create_engine
import logging
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


__all__ = ["setup_logging", "setup_database"]
