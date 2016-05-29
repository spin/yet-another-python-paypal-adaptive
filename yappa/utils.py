import decimal
from datetime import datetime, timezone
from collections import namedtuple

import pytz


def current_local_time(zone='Asia/Taipei'):
    """
    Get current time with specified time zone

    @param zone: zone name
    @return:
    """
    now = datetime.now(timezone.utc)
    local_now = now.astimezone(pytz.timezone(zone))

    return local_now


def decimal_default(obj):
    """
    Used for json.dumps()

    @param obj:
    @return:
    """
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError


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
