import json
import unittest
from unittest.mock import patch
from decimal import Decimal

from yappa.api import PreApproval, PreApprovalDetails


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
            startingDate=self.starting_date,
            endingDate=self.ending_date,
            currencyCode='USD',
            returnUrl=self.return_url,
            cancelUrl=self.cancel_url,
            maxAmountPerPayment=self.max_amount_per_payment,
            maxNumberOfPayments=self.max_number_of_payments,
            maxTotalAmountOfAllPayments=self.max_total_amount_of_all_payments
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

    @patch('yappa.api.requests')
    def test_retrieve_preapproval_details(self, mock_request):
        expected_endpoint = 'https://svcs.sandbox.paypal.com/AdaptivePayments/PreapprovalDetails'
        expected_headers = {
            'X-PAYPAL-SECURITY-USERID': 'fakeuserid',
            'X-PAYPAL-SECURITY-PASSWORD': 'fakepassword',
            'X-PAYPAL-SECURITY-SIGNATURE': '123456789',
            'X-PAYPAL-APPLICATION-ID': 'APP-123456',
            'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
            'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON',
        }
        expected_payload = {
            'preapprovalKey': self.preapproval_key,
            'requestEnvelope': {
                'errorLanguage': 'en_US',
            }
        }

        preapproval_detials = PreApprovalDetails(self.credentials, debug=True)

        preapproval_detials.request(
            preapprovalKey=self.preapproval_key,
        )

        args, kwargs = mock_request.post.call_args

        self.assertEquals(args, (expected_endpoint,))
        self.assertEquals(kwargs['headers'], expected_headers)
        self.assertEquals(json.loads(kwargs['data']), expected_payload)

    @patch('yappa.api.requests.post')
    def test_retrieve_preapproval_details_unapproved(self, mock_post):
        mock_response = {
            'approved': 'false',
            'cancelUrl': self.cancel_url,
            'curPayments': '0',
            'curPaymentsAmount': '0.00',
            'curPeriodAttempts': '0',
            'currencyCode': 'USD',
            'dateOfMonth': '0',
            'dayOfWeek': 'NO_DAY_SPECIFIED',
            'displayMaxTotalAmount': 'false',
            'endingDate': '2016-06-19T18:27:48.000+08:00',
            'maxTotalAmountOfAllPayments': '500.00',
            'paymentPeriod': 'NO_PERIOD_SPECIFIED',
            'pinType': 'NOT_REQUIRED',
            'responseEnvelope': {
                'ack': 'Success',
                'build': '20420247',
                'correlationId': 'c8c558a0c0401',
                'timestamp': '2016-05-29T04:09:05.377-07:00'
            },
            'returnUrl': self.return_url,
            'startingDate': '2016-05-30T18:27:48.000+08:00',
            'status': 'ACTIVE'
        }
        mock_post.return_value.json.return_value = mock_response

        preapproval_detials = PreApprovalDetails(self.credentials, debug=True)
        resp = preapproval_detials.request()

        self.assertEquals(resp.ack, 'Success')
        self.assertEquals(resp.approved, 'false')
        self.assertEquals(resp.status, 'ACTIVE')
        self.assertEquals(resp.maxTotalAmountOfAllPayments, '500.00')

    @patch('yappa.api.requests.post')
    def test_retrieve_preapproval_details_approved(self, mock_post):
        mock_response = {
            'approved': 'true',
            'cancelUrl': self.cancel_url,
            'curPayments': '0',
            'curPaymentsAmount': '0.00',
            'curPeriodAttempts': '0',
            'currencyCode': 'USD',
            'dateOfMonth': '0',
            'dayOfWeek': 'NO_DAY_SPECIFIED',
            'displayMaxTotalAmount': 'false',
            'endingDate': '2016-06-19T18:27:48.000+08:00',
            'maxTotalAmountOfAllPayments': '500.00',
            'paymentPeriod': 'NO_PERIOD_SPECIFIED',
            'pinType': 'NOT_REQUIRED',
            'responseEnvelope': {
                'ack': 'Success',
                'build': '20420247',
                'correlationId': 'c8c558a0c0401',
                'timestamp': '2016-05-29T04:09:05.377-07:00'
            },
            'returnUrl': self.return_url,
            'sender': {'accountId': 'ABCDEFG'},
            'senderEmail': 'fake-buyer@gmail.com',
            'startingDate': '2016-05-30T18:27:48.000+08:00',
            'status': 'ACTIVE'
        }
        mock_post.return_value.json.return_value = mock_response

        preapproval_detials = PreApprovalDetails(self.credentials, debug=True)
        resp = preapproval_detials.request()

        self.assertEquals(resp.ack, 'Success')
        self.assertEquals(resp.approved, 'true')
        self.assertEquals(resp.status, 'ACTIVE')
        self.assertEquals(resp.maxTotalAmountOfAllPayments, '500.00')
        self.assertEquals(resp.sender, {'accountId': 'ABCDEFG'})
        self.assertEquals(resp.senderEmail, 'fake-buyer@gmail.com')

    @patch('yappa.api.requests.post')
    def test_retrieve_preapproval_details_with_invalid_key(self, mock_post):
        mock_response = {
            'error': [{
                'category': 'Application',
                'domain': 'PLATFORM',
                'errorId': '580022',
                'message': 'Invalid request parameter: preapprovalKey with value PA-5W434979gggggg',
                'parameter': ['preapprovalKey', 'PA-5W434979gggggg'],
                'severity': 'Error',
                'subdomain': 'Application'
            }],
            'responseEnvelope': {
                'ack': 'Failure',
                'build': '20420247',
                'correlationId': '9a2ae1abba0ac',
                'timestamp': '2016-05-29T09:13:32.007-07:00'
            }
        }
        mock_post.return_value.json.return_value = mock_response

        preapproval_detials = PreApprovalDetails(self.credentials, debug=True)
        resp = preapproval_detials.request()

        self.assertEquals(resp.ack, 'Failure')
        self.assertEquals(resp.errorId, '580022')
        self.assertEquals(resp.message, 'Invalid request parameter: preapprovalKey with value PA-5W434979gggggg')
        self.assertEquals(resp.timestamp, '2016-05-29T09:13:32.007-07:00')
