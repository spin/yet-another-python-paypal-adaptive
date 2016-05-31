import unittest

from yappa.api import AdaptiveApiBase


class AdaptiveBaseTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

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

        resp = AdaptiveApiBase.build_failure_response(raw_response)

        self.assertEquals(resp.ack, 'Failure')
        self.assertEquals(resp.errorId, '580022'),
        self.assertEquals(resp.timestamp, '2016-05-29T09:13:32.007-07:00')
        self.assertEquals(resp.message, 'Invalid request parameter: preapprovalKey with value ABCD')