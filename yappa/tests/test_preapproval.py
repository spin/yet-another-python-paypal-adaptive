import json
import unittest
from unittest.mock import MagicMock, patch
from decimal import Decimal

from yappa.api import PreApproval


class PreApprovalTestCase(unittest.TestCase):
    def setUp(self):
        self.credentials = {
            'PAYPAL_USER_ID': 'fakeuserid',
            'PAYPAL_PASSWORD': 'fakepassword',
            'PAYPAL_SIGNATURE': '123456789',
            'PAYPAL_APP_ID': 'APP-123456'
        }

        self.starting_date = '2016-05-28T00:33:00+08:0'
        self.ending_date = '2016-06-28T00:33:00+08:0'
        self.currency = 'USD'
        self.return_url = 'http://return.url'
        self.cancel_url = 'http://cancel.url'
        self.max_amount_per_payment = Decimal('35.55')
        self.max_number_of_payments = 15
        self.max_total_amount_of_all_payments = Decimal('500.55')

        self.preapproval_key = 'PA-11111111111111111'

    def tearDown(self):
        pass

    @patch('yappa.api.requests')
    def test_request_preapproval(self, mock_request):
        expected_endpoint = 'https://svcs.sandbox.paypal.com/AdaptivePayments/Preapproval'
        expected_headers = {
            'X-PAYPAL-SECURITY-USERID': 'fakeuserid',
            'X-PAYPAL-SECURITY-PASSWORD': 'fakepassword',
            'X-PAYPAL-SECURITY-SIGNATURE': '123456789',
            'X-PAYPAL-APPLICATION-ID': 'APP-123456',
            'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
            'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON',
        }
        expected_payload = {
            'startingDate': self.starting_date,
            'endingDate': self.ending_date,
            'returnUrl': self.return_url,
            'cancelUrl': self.cancel_url,
            'currencyCode': self.currency,
            'maxAmountPerPayment': 35.55,
            'maxNumberOfPayments': self.max_number_of_payments,
            'maxTotalAmountOfAllPayments': 500.55,
            'requestEnvelope': {
                'errorLanguage': 'en_US',
            }
        }

        preapproval = PreApproval(self.credentials, debug=True)

        preapproval.request(
            starting_date=self.starting_date,
            ending_date=self.ending_date,
            currency='USD',
            return_url=self.return_url,
            cancel_url=self.cancel_url,
            max_amount_per_payment=self.max_amount_per_payment,
            max_number_of_payments=self.max_number_of_payments,
            max_total_amount_of_all_payments=self.max_total_amount_of_all_payments
        )

        args, kwargs = mock_request.post.call_args

        self.assertEquals(args, (expected_endpoint,))
        self.assertEquals(kwargs['headers'], expected_headers)
        self.assertEquals(json.loads(kwargs['data']), expected_payload)

    @patch('yappa.api.requests.post')
    def test_request_preapproval_successfully(self, mock_post):
        mock_response = {
            'preapprovalKey': self.preapproval_key,
            'responseEnvelope': {
                'ack': 'Success',
                'build': '99999999',
                'correlationId': 'd99999eac1e999',
                'timestamp': '2016-05-29T03:27:49.944-07:00'}
        }
        mock_post.return_value.json.return_value = mock_response

        preapproval = PreApproval(self.credentials, debug=True)
        resp = preapproval.request()

        self.assertEquals(resp.ack, 'Success')
        self.assertEquals(resp.preapprovalKey, self.preapproval_key)
        self.assertEqual(resp.nextUrl, ('https://www.sandbox.paypal.com/cgi-bin/webscr?'
                                        'cmd=_ap-preapproval&preapprovalkey=PA-11111111111111111'))

    @patch('yappa.api.requests.post')
    def test_request_preapproval_with_invalid_payment(self, mock_post):
        mock_response = {
            'error': [{
                'category': 'Application',
                'domain': 'PLATFORM',
                'errorId': '580001',
                'message': 'Invalid request: Data validation',
                'parameter': ['Data validation warning(line -1, col 0): null'],
                'severity': 'Error',
                'subdomain': 'Application'
            }],
            'responseEnvelope': {
                'ack': 'Failure',
                'build': '20420247',
                'correlationId': '0d30f655e5515',
                'timestamp': '2016-05-29T04:55:31.432-07:00'
            }
        }
        mock_post.return_value.json.return_value = mock_response

        preapproval = PreApproval(self.credentials, debug=True)
        resp = preapproval.request()

        self.assertEquals(resp.ack, 'Failure')
        self.assertEquals(resp.errorId, '580001')
        self.assertEquals(resp.message, 'Invalid request: Data validation')
        self.assertEquals(resp.timestamp, '2016-05-29T04:55:31.432-07:00')

    @patch('yappa.api.requests.post')
    def test_request_preapproval_with_invalid_date_range(self, mock_post):
        mock_response = {
            'error': [{
                'category': 'Application',
                'domain': 'PLATFORM',
                'errorId': '580024',
                'message': 'The start date must be in the future',
                'parameter': ['startingDate'],
                'severity': 'Error',
                'subdomain': 'Application'
            }],
            'responseEnvelope': {
                'ack': 'Failure',
                'build': '20420247',
                'correlationId': '1b392fdd4b4f2',
                'timestamp': '2016-05-29T09:25:28.817-07:00'
            }
        }
        mock_post.return_value.json.return_value = mock_response

        preapproval = PreApproval(self.credentials, debug=True)
        resp = preapproval.request()

        self.assertEquals(resp.ack, 'Failure')
        self.assertEquals(resp.errorId, '580024')
        self.assertEquals(resp.message, 'The start date must be in the future')
        self.assertEquals(resp.timestamp, '2016-05-29T09:25:28.817-07:00')
