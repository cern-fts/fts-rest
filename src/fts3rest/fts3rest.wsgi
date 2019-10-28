#!/usr/bin/env python

# Need to override the PYTHONPATH for EL6, so slqlachemy 0.8
# is found
#import sys
#sys.path.insert(0, '/usr/lib64/python2.6/site-packages/SQLAlchemy-0.8.2-py2.6-linux-x86_64.egg/')

from paste.deploy import loadapp
from paste.script.util.logging_config import fileConfig

fileConfig('/etc/fts3/fts3rest.ini')
application = loadapp('config:/etc/fts3/fts3rest.ini')

#from gevent import pywsgi
#server = pywsgi.WSGIServer(('', 8447), application, keyfile='/etc/grid-security/hostkey.pem', certfile='/etc/grid-security/hostcert.pem')
# to start the server asynchronously, call server.start()
# we use blocking serve_forever() here because we have no other jobs
#server.serve_forever()




#####from gevent import pywsgi
#####server = pywsgi.WSGIServer(('', 8446), application, keyfile='/etc/grid-security/hostkey.pem', certfile='/etc/grid-security/hostcert.pem')
# to start the server asynchronously, call server.start()
# we use blocking serve_forever() here because we have no other jobs
####server.serve_forever()

#from wsgiref import simple_server
#httpd = simple_server.WSGIServer(('',8446), simple_server.WSGIRequestHandler)
#httpd.set_app(application)
#httpd.serve_forever()
