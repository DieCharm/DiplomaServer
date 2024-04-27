from datetime import datetime, timedelta

def timestamp_from_datetime_str(datetime_str):
    try:
        dt = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
        dt_utc = dt + timedelta(hours = 2)
        ts = datetime.timestamp(dt_utc)
        return ts
    except:
        return 0