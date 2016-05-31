import json
from abc import ABCMeta, abstractmethod
from collections import namedtuple

import requests

from .settings import Settings
from .utils import decimal_default
from .models import ReceiverList
from .exceptions import InvalidReceiverException


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

    @staticmethod
    def build_failure_response(response_json):
        """
        Build PayPal request failure response object

        @param response_json: response dictionary
        @return: custom response object
        """
        ApiResponse = namedtuple('ApiResponse', ['ack', 'message', 'errorId', 'timestamp'])
        ack = response_json['responseEnvelope']['ack']
        timestamp = response_json['responseEnvelope']['timestamp']
        error = response_json['error'][0]

        return ApiResponse(
            ack=ack,
            errorId=error.get('errorId'),
            message=error.get('message'),
            timestamp=timestamp)

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
            key = response.get('preapprovalKey')
            next_url = ''

            if self.auth_url and key:
                next_url = '{}?cmd=_ap-preapproval&preapprovalkey={}'.format(self.auth_url, key)

            api_response = ApiResponse(ack=ack, preapprovalKey=key, nextUrl=next_url)

        else:   # ack in ('Failure', 'FailureWithWarning')
            api_response = self.build_failure_response(response)

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
            api_response = self.build_failure_response(response)

        return api_response


class Pay(AdaptiveApiBase):
    DEFAULT_FEES_PAYER = 'EACHRECEIVER'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = '{}/{}'.format(self.endpoint, 'Pay')

    def build_payload(self, *args, **kwargs):
        receiver_list = kwargs.get('receiverList')
        preapproval_key = kwargs.get('preapprovalKey', None)

        if not isinstance(receiver_list, ReceiverList):
            raise InvalidReceiverException('receiverList needs to be instance of yappa.models.RecieverList')

        payload = {
            'actionType': 'PAY',
            'feesPayer': kwargs.get('feesPayer', self.DEFAULT_FEES_PAYER),
            'currencyCode': kwargs.get('currencyCode'),
            'senderEmail': kwargs.get('senderEmail'),
            'receiverList': receiver_list.to_json(),
            'returnUrl': kwargs.get('returnUrl'),
            'cancelUrl': kwargs.get('cancelUrl'),
            'memo': kwargs.get('memo', '')
        }

        if preapproval_key is not None:
            payload['preapprovalKey'] = preapproval_key

        return payload

    def build_response(self, response):
        ack = response['responseEnvelope']['ack']
        response_fields = ['ack', 'payKey', 'paymentExecStatus', 'paymentInfoList', 'sender']

        if ack in ('Success', 'SuccessWithWarning'):
            ApiResponse = namedtuple('ApiResponse', response_fields)
            info_list = response.get('paymentInfoList', None)
            payment_info_list = info_list['paymentInfo'] if info_list else None

            response_kwargs = {
                'ack': ack,
                'payKey': response.get('payKey'),
                'paymentExecStatus': response.get('paymentExecStatus'),
                'paymentInfoList': payment_info_list,
                'sender': response.get('sender')
            }

            api_response = ApiResponse(**response_kwargs)

        else:
            api_response = self.build_failure_response(response)

        return api_response
