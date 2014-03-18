import json

from fts3rest.tests import TestController


class TestJobListing(TestController):
    """
    Tests for the job controller, listing, stating, etc.
    """

    def _submit(self):
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
        self.assertTrue(len(job_id) > 0)
        return job_id

    def test_show_job(self):
        """
        Get information about a job
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job_id = self._submit()
        answer = self.app.get(url="/jobs/%s" % job_id, status=200)
        job = json.loads(answer.body)

        self.assertEqual(job['job_id'], job_id)
        self.assertEqual(job['job_state'], 'SUBMITTED')

    def test_list_job_default(self):
        """
        List active jobs
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job_id = self._submit()

        answer = self.app.get(url="/jobs",
                              status=200)
        job_list = json.loads(answer.body)
        self.assertTrue(job_id in map(lambda j: j['job_id'], job_list))

    def test_list_with_dlg_id(self):
        """
        List active jobs with the right delegation id
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        job_id = self._submit()

        answer = self.app.get(url="/jobs",
                              params={'dlg_id': creds.delegation_id},
                              status=200)
        job_list = json.loads(answer.body)
        self.assertTrue(job_id in map(lambda j: j['job_id'], job_list))

    def test_list_bad_dlg_id(self):
        """
        Trying to list jobs belonging to a different delegation id
        must be forbidden
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        self.app.get(url="/jobs",
                     params={'dlg_id': creds.delegation_id + '1234'},
                     status=403)

    def test_list_bad_dn(self):
        """
        Trying to list with the right delegation id mismatched bad DN is a bad
        request
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        self.app.get(url="/jobs",
                     params={'dlg_id': creds.delegation_id, 'user_dn': '/CN=1234'},
                     status=400)

    def test_list_with_state_empty(self):
        """
        Filter by state (no match)
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        job_id = self._submit()

        answer = self.app.get(url="/jobs",
                              params={'dlg_id': creds.delegation_id, 'state_in': 'FINISHED,FAILED,CANCELED'},
                              status=200)
        job_list = json.loads(answer.body)
        self.assertFalse(job_id in map(lambda j: j['job_id'], job_list))

    def test_list_with_state_match(self):
        """
        Filter by state (match)
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        creds = self.get_user_credentials()

        job_id = self._submit()

        answer = self.app.get(url="/jobs",
                              params={'dlg_id': creds.delegation_id, 'state_in': 'ACTIVE,SUBMITTED'},
                              status=200)
        job_list = json.loads(answer.body)
        self.assertTrue(job_id in map(lambda j: j['job_id'], job_list))

    def test_list_with_state_no_dlg_id(self):
        """
        When specifying the statuses in the query, dlg_id is mandatory
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        self.app.get(url="/jobs",
                     params={'state_in': 'SUBMITTED,ACTIVE'},
                     status=403)

    def test_list_no_vo(self):
        """
        Submit a valid job with no VO data in the credentials. Listing it should be possible
        afterwards (regression test for FTS-18)
        """
        self.setup_gridsite_environment(no_vo=True)
        self.push_delegation()

        job_id = self._submit()

        # Must be in the listings!
        answer = self.app.get(url="/jobs",
                              status=200)
        job_list = json.loads(answer.body)
        self.assertTrue(job_id in map(lambda j: j['job_id'], job_list))

    def test_get_no_vo(self):
        """
        Submit a valid job with no VO data in the credentials. Stating it should be possible
        afterwards (regression test for FTS-18)
        """
        self.setup_gridsite_environment(no_vo=True)
        self.push_delegation()

        job_id = self._submit()

        # Must be in the listings!
        answer = self.app.get(url="/jobs/%s" % job_id,
                              status=200)
        job_info = json.loads(answer.body)
        self.assertEqual(job_id, job_info['job_id'])
        self.assertEqual('nil', job_info['vo_name'])

    def test_get_field(self):
        """
        Request a field from a job
        """
        self.setup_gridsite_environment(no_vo=True)
        self.push_delegation()

        job_id = self._submit()

        answer = self.app.get(url="/jobs/%s/job_state" % job_id,
                              status=200)
        state = json.loads(answer.body)
        self.assertEqual(state, 'SUBMITTED')
