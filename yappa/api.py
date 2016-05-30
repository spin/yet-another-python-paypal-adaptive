import json
from abc import ABCMeta, abstractmethod
from collections import namedtuple

import requests

from yappa.settings import Settings
from yappa.utils import decimal_default, build_failure_response


class AdaptiveApiBase(metaclass=ABCMeta):

    def __init__(self, credentials, debug=False):
        settings = Settings(debug=debug)

        self.endpoint = settings.PAYPAL_ENDPOINT
        self.auth_url = settings.PAYPAL_AUTH_URL
        self.credentials = credentials

        self.headers = {}
        self.payload = {
            'requestEnvelope': {
                'errorLanguage': 'en_US',
            }
        }

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = '{}/{}'.format(self.endpoint, 'Preapproval')

    def build_payload(self, *args, **kwargs):
        return {
            'startingDate': kwargs.get('startingDate'),
            'endingDate': kwargs.get('endingDate'),
            'returnUrl': kwargs.get('returnUrl'),
            'cancelUrl': kwargs.get('cancelUrl'),
            'currencyCode': kwargs.get('currencyCode'),
            'maxAmountPerPayment': kwargs.get('maxAmountPerPayment'),
            'maxNumberOfPayments': kwargs.get('maxNumberOfPayments'),
            'maxTotalAmountOfAllPayments': kwargs.get('maxTotalAmountOfAllPayments')
        }

    def build_response(self, response):
        ack = response['responseEnvelope']['ack']

        if ack in ('Success', 'SuccessWithWarning'):
            ApiResponse = namedtuple('ApiResponse', ['ack', 'preapprovalKey', 'nextUrl'])
            key = response['preapprovalKey']
            next_url = ''

            if self.auth_url and key:
                next_url = '{}?cmd=_ap-preapproval&preapprovalkey={}'.format(self.auth_url, key)

            api_response = ApiResponse(ack=ack, preapprovalKey=key, nextUrl=next_url)

        else:   # ack in ('Failure', 'FailureWithWarning')
            api_response = build_failure_response(response)

        return api_response


class PreApprovalDetails(AdaptiveApiBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = '{}/{}'.format(self.endpoint, 'PreapprovalDetails')

    def build_payload(self, *args, **kwargs):
        return {
            'preapprovalKey': kwargs.get('preapprovalKey'),
        }

    def build_response(self, response):
        ack = response['responseEnvelope']['ack']
        response_fields = ['ack', 'approved', 'cancelUrl', 'curPayments', 'curPaymentsAmount',
                           'curPeriodAttempts', 'currencyCode', 'dateOfMonth', 'dayOfWeek',
                           'displayMaxTotalAmount', 'endingDate', 'maxTotalAmountOfAllPayments',
                           'paymentPeriod', 'pinType', 'returnUrl', 'startingDate', 'status',
                           'sender', 'senderEmail']

        if ack in ('Success', 'SuccessWithWarning'):
            ApiResponse = namedtuple('ApiResponse', response_fields)
            response_kwargs = {field: ack if field == 'ack' else response.get(field) for field in response_fields}

            api_response = ApiResponse(**response_kwargs)

        else:
            api_response = build_failure_response(response)

        return api_response


class Pay(AdaptiveApiBase):

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
