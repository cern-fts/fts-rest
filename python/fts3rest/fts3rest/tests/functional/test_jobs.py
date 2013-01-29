from fts3rest.tests import *

class TestJobsController(TestController):

    def test_index(self):
        response = self.app.get(url('jobs'))
        # Test response...

    def test_index_as_xml(self):
        response = self.app.get(url('formatted_jobs', format='xml'))

    def test_create(self):
        response = self.app.post(url('jobs'))

    def test_new(self):
        response = self.app.get(url('new_job'))

    def test_new_as_xml(self):
        response = self.app.get(url('formatted_new_job', format='xml'))

    def test_update(self):
        response = self.app.put(url('job', id=1))

    def test_update_browser_fakeout(self):
        response = self.app.post(url('job', id=1), params=dict(_method='put'))

    def test_delete(self):
        response = self.app.delete(url('job', id=1))

    def test_delete_browser_fakeout(self):
        response = self.app.post(url('job', id=1), params=dict(_method='delete'))

    def test_show(self):
        response = self.app.get(url('job', id=1))

    def test_show_as_xml(self):
        response = self.app.get(url('formatted_job', id=1, format='xml'))

    def test_edit(self):
        response = self.app.get(url('edit_job', id=1))

    def test_edit_as_xml(self):
        response = self.app.get(url('formatted_edit_job', id=1, format='xml'))
