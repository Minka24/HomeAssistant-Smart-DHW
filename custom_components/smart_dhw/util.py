from datetime import datetime, timedelta


def now():
    return datetime.now()


def last_hours(hours):
    return now() - timedelta(hours=hours)