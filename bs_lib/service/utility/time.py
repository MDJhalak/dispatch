# -*- coding: utf-8 -*-
from bs_lib.service import app_constant, common, warning
import pytz
import math


def server_to_user_datetime(date_time, server_tz='UTC', user_tz=app_constant.UTC6, format=app_constant.DATE_TIME_FORMAT):
    """process and convert given server date_time to user date_time
    :param date_time: string
    :param server_tz: string
    :param user_tz: string
    :param format: string
    :return: string
    """
    server_tz = pytz.timezone(server_tz)
    user_tz = pytz.timezone(user_tz)
    actual_datetime = common._get_date_time(date_time=date_time, datetime_format=format)
    converted_datetime = common.convert_timezone(date_time=actual_datetime.replace(tzinfo=server_tz), tz=user_tz)
    return converted_datetime.strftime(format)


def convert_float_time(time):
    """process and convert float time value to integer hour & minute
    :param time: float
    :return: int, int
    """
    factor = time < 0 and -1 or 1
    abs_time = abs(time)
    hour = factor * int(math.floor(abs_time))
    minute = int(round((abs_time % 1) * 60))
    if minute > 59 or hour > 23:
        raise warning.ThrowException(message="Wrong value in time.", title="Data Error")
    return hour, minute