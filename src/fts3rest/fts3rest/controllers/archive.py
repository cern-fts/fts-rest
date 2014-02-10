from fts3.model import ArchivedJob
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.middleware.fts3auth import authorized
from fts3rest.lib.middleware.fts3auth.constants import *


class ArchiveController(BaseController):
    """
    Controller for the archived tables
    """

    def _getJob(self, id):
        job = Session.query(ArchivedJob).get(id)
        if job is None:
            abort(404,
                  'No job with the id "%s" has been found in the archive' % id)
        if not authorized(TRANSFER,
                          resource_owner=job.user_dn, resource_vo=job.vo_name):
            abort(403,
                  'Not enough permissions to check the job "%s"' % id)
        return job

    @jsonify
    def index(self, **kwargs):
        """
        Just give the operations that can be performed
        """
        return {
            '_links': {
                'curies': [{
                    'name': 'fts',
                    'href': 'https://svnweb.cern.ch/trac/fts3'
                }],
                'fts:archivedJob': {
                    'href': '/archive/{id}',
                    'title': 'Archived job information',
                    'templated': True
                }
            }
        }

    @jsonify
    def show(self, id, **kwargs):
        """GET /jobs/id: Show a specific item"""
        job = self._getJob(id)
        # Trigger the query, so it is serialized
        files = job.files
        return job

    @jsonify
    def showField(self, id, field, **kwargs):
        """GET /jobs/id/field: Show a specific field from an item"""
        job = self._getJob(id)
        if hasattr(job, field):
            return getattr(job, field)
        else:
            abort(404, 'No such field')
