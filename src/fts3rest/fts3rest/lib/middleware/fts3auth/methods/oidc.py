import re
import dateutil.parser
import logging
import urllib
from datetime import datetime, timedelta

from fts3rest.lib.middleware.fts3auth.credentials import InvalidCredentials, build_vo_from_dn, generate_delegation_id, vo_from_fqan
from fts3rest.lib.helpers.voms import VomsClient


def do_authentication(credentials, env):
    """
    Retrieve credentials from REMOTE USER
    """
    log = logging.getLogger(__name__)
    if not 'REMOTE_USER' in env:
        log.info('NO REMOTE_USER')
        return False
        
    log.info('REMOTE USER '+ env['REMOTE_USER'])
    credentials.user_dn =  env['REMOTE_USER']
    return True
