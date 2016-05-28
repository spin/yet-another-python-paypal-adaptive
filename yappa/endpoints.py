import requests

from yappa.settings import Settings


class AdaptiveEndpointBase(object):
    headers = {}

    def __init__(self, credentials, debug=False):
        settings = Settings(debug=debug)

        self.endpoint = settings.PAYPAL_ENDPOINT
        self.credentials = credentials

        self._build_headers()

    def _build_headers(self):
        headers = {
            'X-PAYPAL-SECURITY-USERID': self.credentials.PAYPAL_USER_ID,
            'X-PAYPAL-SECURITY-PASSWORD': self.credentials.PASSWORD,
            'X-PAYPAL-SECURITY-SIGNATURE': self.credentials.PAYPAL_SIGNATURE,
            'X-PAYPAL-APPLICATION-ID': self.credentials.PAYPAL_APP_ID,
            'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
            'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON',
        }

        self.headers.update(headers)

    def _build_payload(self):
        pass

    def request(self):
        pass


class PreApproval(AdaptiveEndpointBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = '{}/{}'.format(self.endpoint, 'Preapproval')


class PreApprovalDetails(AdaptiveEndpointBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = '{}/{}'.format(self.endpoint, 'PreapprovalDetails')


class Pay(AdaptiveEndpointBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = '{}/{}'.format(self.endpoint, 'Pay')
