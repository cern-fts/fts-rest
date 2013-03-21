"""Setup the fts3rest application"""
import logging
import os

import pylons.test

from fts3rest.config.environment import load_environment
from fts3rest.model.meta import Session, Base

log = logging.getLogger(__name__)

def setup_app(command, conf, vars):
	"""Place any commands to setup fts3rest here"""
	cfgFilename = os.path.split(conf.filename)[-1]
   
	# Don't reload the app if it was loaded under the testing environment
	if not pylons.test.pylonsapp:
		load_environment(conf.global_conf, conf.local_conf)
		
	# Connect
	Base.metadata.bind = Session.bind

	# Drop tables if running tests
	if cfgFilename == 'test.ini':
		log.info("Dropping existing tables for the testing environment")
		Base.metadata.drop_all(checkfirst = True)

	# Create the tables if they don't already exist
	log.info("Creating tables if they do not exist")
	Base.metadata.create_all(checkfirst = True)
