from datetime import datetime, timezone

import pytz


def current_local_time(zone='Asia/Taipei'):
    now = datetime.now(timezone.utc)
    local_now = now.astimezone(pytz.timezone(zone))

    return local_now
