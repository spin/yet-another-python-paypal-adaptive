import json
import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from pytz.exceptions import UnknownTimeZoneError
from decimal import Decimal

from yappa.utils import current_local_time
from yappa.utils import decimal_default
from yappa.utils import build_failure_response


class UtilsTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('yappa.utils.datetime')
    def test_current_local_time_taipei(self, mock_datetime):
        mock_now = datetime(2016, 5, 27, 16, 33, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        local_now = current_local_time('Asia/Taipei')

        self.assertEqual(local_now.isoformat(), '2016-05-28T00:33:00+08:00')

    @patch('yappa.utils.datetime')
    def test_current_local_time_canada(self, mock_datetime):
        mock_now = datetime(2016, 5, 27, 16, 33, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        local_now = current_local_time('Canada/Central')

        self.assertEqual(local_now.isoformat(), '2016-05-27T11:33:00-05:00')

    @patch('yappa.utils.datetime')
    def test_current_local_time_with_invalid_zone(self, mock_datetime):
        mock_now = datetime(2016, 5, 27, 16, 33, 0, 0, tzinfo=timezone.utc)
        mock_datetime.now.return_value = mock_now

        with self.assertRaises(UnknownTimeZoneError) as e:
            current_local_time('invalid/timezone')

    def test_decimal_default(self):
        product = {
            'price': Decimal('55.12')
        }

        result = json.dumps(product, default=decimal_default)
        self.assertEqual(result, '{"price": 55.12}')

    def test_decimal_default_with_non_decimal(self):
        product = {
            'name': 'Product 1'
        }

        result = json.dumps(product, default=decimal_default)
        self.assertEqual(result, '{"name": "Product 1"}')

    def test_build_failure_response(self):
        raw_response = {
            'error': [{
                'category': 'Application',
                'domain': 'PLATFORM',
                'errorId': '580022',
                'message': 'Invalid request parameter: preapprovalKey with value ABCD',
                'parameter': ['preapprovalKey', 'ABCD'],
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

        resp = build_failure_response(raw_response)

        self.assertEquals(resp.ack, 'Failure')
        self.assertEquals(resp.errorId, '580022'),
        self.assertEquals(resp.timestamp, '2016-05-29T09:13:32.007-07:00')
        self.assertEquals(resp.message, 'Invalid request parameter: preapprovalKey with value ABCD')
