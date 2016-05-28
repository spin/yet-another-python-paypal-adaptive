import unittest
from unittest.mock import MagicMock, patch

from yappa.endpoints import PreApproval


class PreApprovalTestCase(unittest.TestCase):
    def setUp(self):
        self.credentials = MagicMock(
            user='fakeuser',
            password='fakepassword',
            signature='1234567',
            app_id='APP-11111',
            return_url='',
            cancel_url='',
        )

    def tearDown(self):
        pass

    @patch('yappa.models.requests')
    def test_request_preapproval_in_sandbox_mode(self):
        preapproval = PreApproval(credentials=self.credentials, debug=True)

        preapproval.request()
        # redirect_url = preapproval.authorization_url