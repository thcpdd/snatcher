from datetime import datetime, timedelta


def delay_time(
    days=0,
    seconds=0,
    microseconds=0,
    milliseconds=0,
    minutes=0,
    hours=0,
    weeks=0
):
    now = datetime.now()
    utc_ctime = datetime.utcfromtimestamp(now.timestamp())  # use utc time
    time_delay = timedelta(days=days, seconds=seconds, microseconds=microseconds,
                           milliseconds=milliseconds, minutes=minutes,
                           hours=hours, weeks=weeks)
    return utc_ctime + time_delay
