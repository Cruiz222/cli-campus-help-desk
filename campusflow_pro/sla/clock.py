from datetime import datetime, timezone

def utc_now():
    current_time = datetime.now(timezone.utc)

    return current_time