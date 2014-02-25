import json

from fts3rest.tests import TestController
from fts3rest.lib.base import Session
from fts3.model import ArchivedJob, ArchivedFile


class TestArchive(TestController):
    """
    Archived jobs
    """

    def _insert_job(self):
        job = ArchivedJob()

        job.job_id = '111-222-333'
        job.job_state = 'CANCELED'

        file = ArchivedFile()
        file.job_id = job.job_id
        file.file_id = 1234
        file.file_state = 'CANCELED'
        file.source_se = 'srm://source'
        file.dest_se = 'srm://dest'

        Session.merge(job)
        Session.merge(file)
        Session.commit()
        return job.job_id

    def test_get_from_archive(self):
        """
        Query an archived job must succeed
        """
        self.setupGridsiteEnvironment()

        job_id = self._insert_job()
        answer = self.app.get(url="/archive/%s" % job_id, status=200)
        job = json.loads(answer.body)

        self.assertEqual(job['job_id'], job_id)
        self.assertEqual(job['job_state'], 'CANCELED')

        self.assertEqual(len(job['files']), 1)

        self.assertEqual(job['files'][0]['file_state'], 'CANCELED')
        self.assertEqual(job['files'][0]['source_se'], 'srm://source')
        self.assertEqual(job['files'][0]['dest_se'], 'srm://dest')
        self.assertEqual(job['files'][0]['file_id'], 1234)

    def test_get_field_from_archive(self):
        """
        Query a specific field from an archived job
        """
        self.setupGridsiteEnvironment()

        job_id = self._insert_job()
        answer = self.app.get(url="/archive/%s/job_state" % job_id, status=200)

        state = json.loads(answer.body)
        self.assertEqual(state, 'CANCELED')
