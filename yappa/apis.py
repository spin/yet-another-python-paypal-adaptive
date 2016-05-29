import json
from abc import ABCMeta, abstractproperty, abstractmethod
from collections import namedtuple

import requests

from yappa.settings import Settings
from yappa.utils import decimal_default


class AdaptiveApiBase(metaclass=ABCMeta):
    headers = {}
    payload = {
        'requestEnvelope': {
            'errorLanguage': 'en_US',
        }
    }

    def __init__(self, credentials, debug=False):
        settings = Settings(debug=debug)

        self.endpoint = settings.PAYPAL_ENDPOINT
        self.auth_url = settings.PAYPAL_AUTH_URL
        self.credentials = credentials

        self._build_headers()

    def _build_headers(self):
        headers = {
            'X-PAYPAL-SECURITY-USERID': self.credentials['PAYPAL_USER_ID'],
            'X-PAYPAL-SECURITY-PASSWORD': self.credentials['PAYPAL_PASSWORD'],
            'X-PAYPAL-SECURITY-SIGNATURE': self.credentials['PAYPAL_SIGNATURE'],
            'X-PAYPAL-APPLICATION-ID': self.credentials['PAYPAL_APP_ID'],
            'X-PAYPAL-REQUEST-DATA-FORMAT': 'JSON',
            'X-PAYPAL-RESPONSE-DATA-FORMAT': 'JSON',
        }

        self.headers.update(headers)

    def request(self, *args, **kwargs):
        self.payload.update(self.build_payload(*args, **kwargs))

        response = requests.post(self.endpoint,
                                 data=json.dumps(self.payload, default=decimal_default),
                                 headers=self.headers)

        return self.build_response(response.json())

    @abstractmethod
    def build_payload(self, *args, **kwargs):
        pass

    @abstractmethod
    def build_response(self, response):
        pass


class PreApproval(AdaptiveApiBase):
    preapproval_key = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = '{}/{}'.format(self.endpoint, 'Preapproval')

    def build_payload(self, *args, **kwargs):
        return {
            'startingDate': kwargs.get('starting_date'),
            'endingDate': kwargs.get('ending_date'),
            'returnUrl': kwargs.get('return_url'),
            'cancelUrl': kwargs.get('cancel_url'),
            'currencyCode': kwargs.get('currency'),
            'maxAmountPerPayment': kwargs.get('max_amount_per_payment'),
            'maxNumberOfPayments': kwargs.get('max_number_of_payments'),
            'maxTotalAmountOfAllPayments': kwargs.get('max_total_amount_of_all_payments')
        }

    def build_response(self, response):
        ApiResponse = namedtuple('ApiResponse', ['ack', 'preapprovalKey', 'nextUrl'])
        ack = response['responseEnvelope']['ack']
        key = response['preapprovalKey']
        next_url = ''

        if self.auth_url and key:
            next_url = '{}?cmd=_ap-preapproval&preapprovalkey={}'.format(self.auth_url, key)

        return ApiResponse(ack=ack, preapprovalKey=key, nextUrl=next_url)


class PreApprovalDetails(AdaptiveApiBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = '{}/{}'.format(self.endpoint, 'PreapprovalDetails')


class Pay(AdaptiveApiBase):
    pay_key = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = '{}/{}'.format(self.endpoint, 'Pay')

    @property
    def next_url(self):
        next_url = ''

        if self.auth_url and self.pay_key:
            next_url = '{}?cmd=_ap-payment&paykey={}'.format(
                self.auth_url,
                self.pay_key)

        return next_url
