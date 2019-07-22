# -*- coding: utf-8 -*-

from bs_lib.service import app_constant, warning
from datetime import datetime, date, time
import time as TIME
from dateutil.relativedelta import relativedelta
import logging
import pytz

logger = logging.getLogger(__name__)
date_time_object_map = {
    app_constant.DATE_FORMAT: date,
    app_constant.TIME_FORMAT: time,
    app_constant.DATE_TIME_FORMAT: datetime,
    app_constant.DATE_TIME_ZONE_FORMAT: datetime
}

# Backward compatibility for existing calls
ThrowException = warning.ThrowException
ThrowWarning = warning.ThrowWarning

#####################################################################################


def split_time_date(date_time=None):
    """Split a datetime to date & time
    @:return dict
    """
    parsed_date_time = get_date_time(date_time)
    return {
        "date": parsed_date_time.strftime(app_constant.DATE_FORMAT),
        "time": parsed_date_time.strftime(app_constant.TIME_FORMAT)
    }


def get_date_time(date_time=None, only_date=False, datetime_format=app_constant.DATE_TIME_FORMAT):
    if _check_datetime_format(date_time, datetime_format):
        if only_date and datetime_format == app_constant.DATE_TIME_FORMAT:
            date_time = date_time[:app_constant.DATE_LENGTH]
            if len(date_time) == app_constant.DATE_LENGTH:
                date_time += " 00:00:00"
        return datetime.strptime(date_time, datetime_format)


def _get_date_time(date_time, datetime_format=app_constant.DATE_TIME_FORMAT):
    if not isinstance(date_time, date_time_object_map.get(datetime_format)):
        date_time = get_date_time(date_time=date_time, datetime_format=datetime_format)
    return date_time


def _check_datetime_format(date_time=None, datetime_format=app_constant.DATE_TIME_FORMAT):
    if date_time is None:
        raise ThrowException(msg="Have not found any Date or Time", title="Date Time Error")
    else:
        try:
            datetime.strptime(date_time, datetime_format)
            return True
        except ValueError:
            raise ThrowException(msg="DateTime format error, use %s" % datetime_format, title="Date Time Error")


def get_date_difference(start_date, end_date, date_format=app_constant.DATE_FORMAT):
    """Relative difference between two date (e.g: month, year, day etc) **not actual**
    @:return relativedelta
    """
    start_date = _get_date_time(date_time=start_date, datetime_format=date_format)
    end_date = _get_date_time(date_time=end_date, datetime_format=date_format)
    return relativedelta(end_date, start_date)


def month_difference(start_date, end_date):
    """Month difference between two date
    @:return int
    """
    diff = get_date_difference(start_date, end_date, date_format=app_constant.DATE_FORMAT)
    return (diff.years * 12) + diff.months


def day_difference(start_date, end_date, date_format=app_constant.DATE_FORMAT):
    """Actual difference between two date (e.g: days, sec etc)
    @:return timedelta
    """
    start_date = _get_date_time(date_time=start_date, datetime_format=date_format)
    end_date = _get_date_time(date_time=end_date, datetime_format=date_format)
    return end_date - start_date


def get_future_date(start_date, days=0, months=0, years=0, date_format=app_constant.DATE_FORMAT):
    """Construct a new date (future or past)
    @:return relativedelta
    """
    start_date = _get_date_time(date_time=start_date, datetime_format=date_format)
    return start_date + relativedelta(days=days, months=months, years=years)


def get_timestamp(date_time, datetime_format=app_constant.DATE_TIME_FORMAT):
    """Convert a given time to UNIX timestamp
    @:return float
    """
    date_time = _get_date_time(date_time=date_time, datetime_format=datetime_format)
    return TIME.mktime(date_time.timetuple())


def convert_timezone(date_time, tz=pytz.timezone('UTC'), datetime_format=app_constant.DATE_TIME_ZONE_FORMAT):
    """Convert a given time to a specified Timezone
    @:return datetime
    """
    date_time = _get_date_time(date_time=date_time, datetime_format=datetime_format)
    return date_time.astimezone(tz)
