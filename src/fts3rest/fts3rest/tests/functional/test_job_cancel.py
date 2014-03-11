import json

from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import Job


class TestJobCancel(TestController):
    """
    Tests for the job cancellation
    """

    def _submit(self):
        """
        Submit a valid job
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['root://source.es/file'],
                'destinations': ['root://dest.ch/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        answer = self.app.put(url="/jobs",
                              params=json.dumps(job),
                              status=200)

        # Make sure it was commited to the DB
        job_id = json.loads(answer.body)['job_id']
        return str(job_id)

    def test_cancel(self):
        """
        Cancel a job
        """
        job_id = self._submit()
        answer = self.app.delete(url="/jobs/%s" % job_id,
                                 status=200)
        job = json.loads(answer.body)

        self.assertEqual(job['job_id'], job_id)
        self.assertEqual(job['job_state'], 'CANCELED')
        self.assertEqual(job['reason'], 'Job canceled by the user')

        # Is it in the database?
        job = Session.query(Job).get(job_id)
        self.assertEqual(job.job_state, 'CANCELED')
        for f in job.files:
            self.assertEqual(f.file_state, 'CANCELED')
