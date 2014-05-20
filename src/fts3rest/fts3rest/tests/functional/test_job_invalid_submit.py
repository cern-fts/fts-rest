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

from datetime import timedelta
import json

from fts3rest.tests import TestController


class TestJobInvalidSubmits(TestController):
    """
    Collection of invalid submissions. Intended to check if the
    job controller filters properly malformed and/or invalid requests.
    """

    def test_submit_malformed(self):
        """
        Submit a piece of data that is not well-formed json
        """
        self.setup_gridsite_environment()

        response = self.app.put(
            url="/jobs",
            params='thisXisXnotXjson',
            status=400
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '400 Bad Request')
        self.assertEquals(error['message'], 'Badly formatted JSON request (No JSON object could be decoded)')

    def test_submit_no_transfers(self):
        """
        Submit valid json data, but without actual transfers
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        job = {'parameters': {}}

        response = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=400
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '400 Bad Request')
        self.assertEquals(error['message'], 'Missing parameter: \'files\'')

    def test_submit_different_protocols(self):
        """
        Source and destination protocol mismatch
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['http://source.es:8446/file'],
                'destinations': ['root://dest.ch:8447/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        response = self.app.post(
            url="/jobs",
            content_type='application/json',
            params=json.dumps(job),
            status=400
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '400 Bad Request')
        self.assertEquals(error['message'], 'No pair with matching protocols')

    def test_no_protocol(self):
        """
        Submit a valid transfer, but with urls with no protocol
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['/etc/passwd'],
                'destinations': ['/srv/pub'],
            }]
        }

        response = self.app.post(
            url="/jobs",
            content_type='application/json',
            params=json.dumps(job),
            status=400
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '400 Bad Request')
        self.assertEquals(error['message'], 'Invalid value within the request: Missing scheme (/etc/passwd)')

    def test_no_file(self):
        """
        Submit a valid transfer, but using file://
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['file:///etc/passwd'],
                'destinations': ['file:///srv/pub'],
            }]
        }

        response = self.app.post(
            url="/jobs",
            content_type='application/json',
            params=json.dumps(job),
            status=400
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '400 Bad Request')
        self.assertEquals(error['message'], 'Invalid value within the request: Can not transfer local files (file:///etc/passwd)')

    def test_one_single_slash(self):
        """
        Well-formed json, but source url is malformed
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['gsiftp:/source.es:8446/file'],
                'destinations': ['gsiftp://dest.ch:8446/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        response = self.app.post(
            url="/jobs",
            content_type='application/json',
            params=json.dumps(job),
            status=400
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '400 Bad Request')
        self.assertEquals(error['message'], 'Invalid value within the request: Missing host (gsiftp:/source.es:8446/file)')

    def test_empty_path(self):
        """
        Well-formed json, but source path is missing
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['gsiftp://source.es:8446/'],
                'destinations': ['gsiftp://dest.ch:8446/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }],
            'params': {'overwrite': True, 'verify_checksum': True}
        }

        response = self.app.post(
            url="/jobs",
            content_type='application/json',
            params=json.dumps(job),
            status=400
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '400 Bad Request')
        self.assertEquals(error['message'], 'Invalid value within the request: Missing path (gsiftp://source.es:8446/)')

    def test_submit_missing_surl(self):
        """
        Well-formed json, but source url is missing
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        job = {'transfers': [{'destinations': ['root://dest.ch/file']}]}

        self.app.put(url="/jobs",
                     params=json.dumps(job),
                     status=400)

        job = {'transfers': [{'source': 'root://source.es/file'}]}

        response = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=400
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '400 Bad Request')
        self.assertEquals(error['message'], 'Missing parameter: \'files\'')

    def test_invalid_surl(self):
        """
        Well-formed json, but the urls are malformed
        """
        self.setup_gridsite_environment()
        self.push_delegation()
        job = {
            'files': [{
                'sources': ['http: //source.es/file'],  # Note the space!
                'destinations': ['http: //dest.ch/file'],
                'selection_strategy': 'orderly',
                'checksum': 'adler32:1234',
                'filesize': 1024,
                'metadata': {'mykey': 'myvalue'},
            }]
        }

        response = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=400
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '400 Bad Request')
        self.assertEquals(error['message'], 'Invalid value within the request: Missing host (http:/// //source.es/file)')

    def test_submit_no_creds(self):
        """
        Submission without valid credentials is forbidden
        """
        self.assertFalse('GRST_CRED_AURI_0' in self.app.extra_environ)
        response = self.app.put(
            url="/jobs",
            params='thisXisXnotXjson',
            status=403
        )

        self.assertEquals(response.content_type, 'application/json')

        print response.body

        error = json.loads(response.body)

        self.assertEquals(error['status'], '403 Forbidden')

    def test_submit_no_delegation(self):
        """
        Submission with valid credentials, but without a delegated proxy,
        must request a delegation
        """
        self.setup_gridsite_environment()

        job = {
            'files': [{
                'sources': ['root://source/file'],
                'destinations': ['root://dest/file'],
            }]
        }

        response = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=419
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '419 Authentication Timeout')
        self.assertEquals(error['message'], 'No delegation found for "%s"' % TestController.TEST_USER_DN)

    def test_submit_expired_credentials(self):
        """
        Submission with an expired proxy must request a delegation
        """
        self.setup_gridsite_environment()
        self.push_delegation(lifetime=timedelta(hours=-1))

        job = {
            'files': [{
                'sources': ['root://source/file'],
                'destinations': ['root://dest/file'],
            }]
        }

        response = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=419
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '419 Authentication Timeout')
        self.assertEquals(error['message'][0:33], 'The delegated credentials expired')

    def test_submit_almost_expired_credentials(self):
        """
        Submission with an proxy that expires in minutes
        """
        self.setup_gridsite_environment()
        self.push_delegation(lifetime=timedelta(minutes=30))

        job = {
            'files': [{
                'sources': ['root://source/file'],
                'destinations': ['root://dest/file'],
            }]
        }

        response = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=419
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '419 Authentication Timeout')
        self.assertEquals(error['message'], 'The delegated credentials has less than one hour left')

    def test_submit_missing_path(self):
        """
        Submit with a url that has no path
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': [{
                'sources': ['http://google.com'],
                'destinations': ['root://dest/file'],
            }]
        }

        response = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=400
        )

        self.assertEquals(response.content_type, 'application/json')

        error = json.loads(response.body)

        self.assertEquals(error['status'], '400 Bad Request')
        self.assertEquals(error['message'], 'Invalid value within the request: Missing path (http://google.com)')

    def test_submit_no_files(self):
        """
        Submit with empty files
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {'files': []}

        response = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=400
        )

        error = json.loads(response.body)

        self.assertEqual(error['status'], '400 Bad Request')
        self.assertEqual(error['message'], 'No transfers specified')

    def test_invalid_files(self):
        """
        Set something completely wrong in files
        """
        self.setup_gridsite_environment()
        self.push_delegation()

        job = {
            'files': 48,
        }

        response = self.app.put(
            url="/jobs",
            params=json.dumps(job),
            status=400
        )

        error = json.loads(response.body)

        self.assertEqual(error['status'], '400 Bad Request')
        self.assertEqual(error['message'][0:17], 'Malformed request')
