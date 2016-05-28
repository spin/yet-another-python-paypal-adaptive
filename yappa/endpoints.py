import requests

from yappa.settings import Settings


class AdaptiveEndpointBase(object):
    def __init__(self, credentials, debug=False):
        settings = Settings(debug=debug)

        self.endpoint = settings.PAYPAL_ENDPOINT
        self.credentials = credentials

    def _build_headers(self):
        pass

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
