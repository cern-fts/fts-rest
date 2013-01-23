from django.http import HttpResponse
from fts3.orm import SchemaVersion
from session import session
import json
 
def ping(request, api_name = None):
	sess = session()
	sv = sess.query(SchemaVersion)[0]
	
	ping = {'schema': str(sv),
		    'api': api_name}

	response = HttpResponse(json.dumps(ping))
	return response
