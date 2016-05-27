import unittest
from unittest.mock import patch
from datetime import datetime, timezone
from pytz.exceptions import UnknownTimeZoneError

from yappa.utils import current_local_time


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
