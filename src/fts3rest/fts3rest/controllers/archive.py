from fts3.model import ArchivedJob
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.middleware.fts3auth import authorized
from fts3rest.lib.middleware.fts3auth.constants import *
from pylons.controllers.util import abort


class ArchiveController(BaseController):
    """
    Operations on archived jobs and transfers
    """

    def _get_job(self, id):
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

    @doc.response(404, 'The job doesn\'t exist')
    @doc.return_type(ArchivedJob)
    @jsonify
    def get(self, id, **kwargs):
        """
        Get the job with the given ID
        """
        job = self._get_job(id)
        # Trigger the query, so it is serialized
        files = job.files
        return job

    @doc.response(404, 'The job or the field doesn\'t exist')
    @jsonify
    def get_field(self, id, field, **kwargs):
        """
        Get a specific field from the job identified by id
        """
        job = self._get_job(id)
        if hasattr(job, field):
            return getattr(job, field)
        else:
            abort(404, 'No such field')
