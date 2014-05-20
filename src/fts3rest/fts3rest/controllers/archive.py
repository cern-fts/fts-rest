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

from webob.exc import HTTPNotFound, HTTPForbidden

from fts3.model import ArchivedJob
from fts3rest.lib.api import doc
from fts3rest.lib.base import BaseController, Session
from fts3rest.lib.helpers import jsonify
from fts3rest.lib.middleware.fts3auth import authorized
from fts3rest.lib.middleware.fts3auth.constants import *


class ArchiveController(BaseController):
    """
    Operations on archived jobs and transfers
    """

    def _get_job(self, job_id):
        job = Session.query(ArchivedJob).get(job_id)
        if job is None:
            raise HTTPNotFound('No job with the id "%s" has been found in the archive' % job_id)
        if not authorized(TRANSFER,
                          resource_owner=job.user_dn, resource_vo=job.vo_name):
            raise HTTPForbidden('Not enough permissions to check the job "%s"' % job_id)
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
    def get(self, job_id, **kwargs):
        """
        Get the job with the given ID
        """
        job = self._get_job(job_id)
        # Trigger the query, so it is serialized
        files = job.files
        return job

    @doc.response(404, 'The job or the field doesn\'t exist')
    @jsonify
    def get_field(self, job_id, field, **kwargs):
        """
        Get a specific field from the job identified by id
        """
        job = self._get_job(job_id)
        if hasattr(job, field):
            return getattr(job, field)
        else:
            raise HTTPNotFound('No such field')
