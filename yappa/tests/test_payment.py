import json
import unittest
from unittest.mock import patch
from decimal import Decimal

from yappa.api import Pay
from yappa.models import Receiver, ReceiverList


class PaymentTestCase(unittest.TestCase):
    def setUp(self):
        self.credentials = {
            'PAYPAL_USER_ID': 'fakeuserid',
            'PAYPAL_PASSWORD': 'fakepassword',
            'PAYPAL_SIGNATURE': '123456789',
            'PAYPAL_APP_ID': 'APP-123456'
        }

        self.currency = 'USD'
        self.return_url = 'http://return.url'
        self.cancel_url = 'http://cancel.url'
        self.preapproval_key = 'PA-11111111111111111'
        self.fees_payer = 'EACHRECEIVER'
        self.sender_email = 'fakesender@gmail.com'
        self.memo = 'Example memo'

        receivers = [Receiver(email='receiver{}@gmail.com'.format(i + 1),
                              amount=Decimal(10+i*5)) for i in range(3)]
        self.receiver_list = ReceiverList(receivers)

        self.pay_key = 'AP-2125055755555555'

    def tearDown(self):
        pass

    @patch('yappa.api.requests')
    def test_request_capturing_preapproved_payment(self, mock_request):
        expected_endpoint = 'https://svcs.sandbox.paypal.com/AdaptivePayments/Pay'
        expected_headers = {
            'X-PAYPAL-SECURITY-USERID': 'fakeuserid',
            'X-PAYPAL-SECURITY-PASSWORD': 'fakepassword',
            'X-PAYPAL-SECURITY-SIGNATURE': '123456789',
            'X-PAYPAL-APPLICATION-ID': 'APP-123456',
            'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
            'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON',
        }
        expected_payload = {
            'actionType': 'PAY',
            'returnUrl': self.return_url,
            'cancelUrl': self.cancel_url,
            'currencyCode': self.currency,
            'feesPayer': self.fees_payer,
            'senderEmail': self.sender_email,
            'memo': self.memo,
            'receiverList': {
                'receiver': [
                    {'email': 'receiver1@gmail.com', 'amount': '10'},
                    {'email': 'receiver2@gmail.com', 'amount': '15'},
                    {'email': 'receiver3@gmail.com', 'amount': '20'},
                ]
            },
            'requestEnvelope': {
                'errorLanguage': 'en_US',
            }
        }

        pay = Pay(self.credentials, debug=True)

        pay.request(
            currencyCode='USD',
            returnUrl=self.return_url,
            cancelUrl=self.cancel_url,
            senderEmail=self.sender_email,
            memo=self.memo,
            receiverList=self.receiver_list
        )

        args, kwargs = mock_request.post.call_args

        self.assertEquals(args, (expected_endpoint,))
        self.assertEquals(kwargs['headers'], expected_headers)
        self.assertEquals(json.loads(kwargs['data']), expected_payload)

    @patch('yappa.api.requests.post')
    def test_capture_preapproved_payment_successfully(self, mock_post):
        expected_payment_info_list = [
            {
                'pendingRefund': 'false',
                'receiver': {
                    'accountId': 'RUCGXXXXXXXX',
                    'amount': '6.00',
                    'email': 'receiver1@gmail.com',
                    'primary': 'false'
                },
                'senderTransactionId': '07V41747777777777',
                'senderTransactionStatus': 'COMPLETED',
                'transactionId': '111111111111',
                'transactionStatus': 'COMPLETED'
            },
            {
                'pendingRefund': 'false',
                'receiver': {
                    'accountId': 'WRFQXXXXXXXX',
                    'amount': '12.00',
                    'email': 'receiver2@gmail.com',
                    'primary': 'false'
                },
                'senderTransactionId': '98692817999999999',
                'senderTransactionStatus': 'COMPLETED',
                'transactionId': '2222222222222',
                'transactionStatus': 'COMPLETED'
            }
        ]
        mock_response = {
            'payKey': self.pay_key,
            'paymentExecStatus': 'COMPLETED',
            'paymentInfoList': {
                'paymentInfo': expected_payment_info_list
            },
            'responseEnvelope': {
                'ack': 'Success',
                'build': '20420247',
                'correlationId': 'a92e1583464e5',
                'timestamp': '2016-05-30T08:39:34.156-07:00'
            },
            'sender': {'accountId': 'SD97PL53N4N2Y'}
        }

        mock_post.return_value.json.return_value = mock_response
        receiver_list = ReceiverList([])    # No need to be true receiver list

        pay = Pay(self.credentials, debug=True)
        resp = pay.request(receiverList=receiver_list)

        self.assertEquals(resp.ack, 'Success')
        self.assertEquals(resp.payKey, self.pay_key)
        self.assertEquals(resp.paymentExecStatus, 'COMPLETED')
        self.assertEquals(resp.sender, {'accountId': 'SD97PL53N4N2Y'})
        self.assertEquals(resp.paymentInfoList, expected_payment_info_list)

    @patch('yappa.api.requests.post')
    def test_capture_preapproved_payment_with_invalid_preapproval_key(self, mock_post):
        mock_response = {
            'error': [{
                'category': 'Application',
                'domain': 'PLATFORM',
                'errorId': '580022',
                'message': 'Invalid request parameter: preapprovalKey with value NON_EXISTENT_KEY',
                'parameter': ['preapprovalKey', 'NON_EXISTENT_KEY'],
                'severity': 'Error',
                'subdomain': 'Application'
            }],
            'responseEnvelope': {
                'ack': 'Failure',
                'build': '20420247',
                'correlationId': 'e0c1fa3692d17',
                'timestamp': '2016-05-30T10:21:25.631-07:00'
            }
        }

        mock_post.return_value.json.return_value = mock_response
        receiver_list = ReceiverList([])

        pay = Pay(self.credentials, debug=True)
        resp = pay.request(receiverList=receiver_list)

        self.assertEquals(resp.ack, 'Failure')
        self.assertEquals(resp.errorId, '580022')
        self.assertEquals(resp.message, 'Invalid request parameter: preapprovalKey with value NON_EXISTENT_KEY')
        self.assertEquals(resp.timestamp, '2016-05-30T10:21:25.631-07:00')

    @patch('yappa.api.requests.post')
    def test_capture_preapproved_payment_with_duplicate_receiver(self, mock_post):
        mock_response = {
            'error': [{
                'category': 'Application',
                'domain': 'PLATFORM',
                'errorId': '579040',
                'message': 'Receiver PayPal accounts must be unique.',
                'parameter': ['receiver'],
                'severity': 'Error',
                'subdomain': 'Application'
            }],
            'responseEnvelope': {
                'ack': 'Failure',
                'build': '20420247',
                'correlationId': '93b6326927fc8',
                'timestamp': '2016-05-30T10:27:03.931-07:00'
            }
        }

        mock_post.return_value.json.return_value = mock_response
        receiver_list = ReceiverList([])

        pay = Pay(self.credentials, debug=True)
        resp = pay.request(receiverList=receiver_list)

        self.assertEquals(resp.ack, 'Failure')
        self.assertEquals(resp.errorId, '579040')
        self.assertEquals(resp.message, 'Receiver PayPal accounts must be unique.')
        self.assertEquals(resp.timestamp, '2016-05-30T10:27:03.931-07:00')
