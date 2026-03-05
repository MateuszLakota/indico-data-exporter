from datetime import datetime, timezone, timedelta

CET = timezone(timedelta(hours=1))


def timestamp_to_iso(ts_str: str):
    ts_float = float(ts_str)

    dt = datetime.fromtimestamp(ts_float, tz=CET)

    return dt.replace(microsecond=0, tzinfo=None).isoformat()
