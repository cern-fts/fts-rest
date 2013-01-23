from django.conf import settings
from fts3 import orm
import threading



def session():
	local = threading.local()
	if not hasattr(local, 'session'):
		local.session = orm.connect(settings.FTS3_ORM_CONNECT_STRING)
	return local.session
