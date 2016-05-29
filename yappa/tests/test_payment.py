import unittest
from unittest.mock import patch
from decimal import Decimal


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

    def tearDown(self):
        pass

    def test_capture_future_payment(self):
        pass
