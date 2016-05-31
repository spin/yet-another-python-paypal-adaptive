import decimal
from datetime import datetime, timezone

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

