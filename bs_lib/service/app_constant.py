# -*- coding: utf-8 -*-

from datetime import datetime, date

DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_TIME_ZONE_FORMAT = "%Y-%m-%d %H:%M:%S%z"
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"
HM_FORMAT = "%H:%M"
HM_12_HOUR_FORMAT = "%I:%M %p"
UTC6 = 'Etc/GMT-6'
OL_REPORT_DATE_FORMAT = "%d-%m-%Y"
DATE_LENGTH = len(date.today().strftime(DATE_FORMAT))
DATETIME_LENGTH = len(datetime.now().strftime(DATE_TIME_FORMAT))
HM_LENGTH = len(datetime.now().strftime(HM_FORMAT))

# SELECTION DATA #
year_selection = [(year, str(year)) for year in range(1990, datetime.now().year + 3)]
month_selection = [
    ('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'),
    ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')
]
week_days_selection = [
    ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'),
    ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')
]
# ENDS HERE #