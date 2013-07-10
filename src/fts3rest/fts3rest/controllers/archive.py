from fts3.model import ArchivedJob
from fts3rest.lib.base import Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.middleware.fts3auth import authorized
from fts3rest.lib.middleware.fts3auth.constants import *
from jobs import JobsController


class ArchiveController(JobsController):
    
    def _getJob(self, id):
        job = Session.query(ArchivedJob).get(id)
        if job is None:
            abort(404, 'No job with the id "%s" has been found in the archive' % id)
        if not authorized(TRANSFER, resource_owner = job.user_dn, resource_vo = job.vo_name):
            abort(403, 'Not enough permissions to check the job "%s"' % id)
        return job
    
    @jsonify
    def index(self, **kwargs):
        return {'_links': {
                    'curies': [{'name': 'fts', 'href': 'https://svnweb.cern.ch/trac/fts3'}],
                    
                    'fts:archivedJob': {
                        'href': '/archive/{id}', 'title': 'Archived job information',
                        'templated': True
                    }
                }
            }
