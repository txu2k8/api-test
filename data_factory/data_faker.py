#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:options.py
@time:2021/09/26
@email:tao.xu2008@outlook.com
@description:
"""

import time
import datetime
import arrow
import calendar
from faker import Faker


class DataFaker(object):
    """data faker"""
    def __init__(self):
        self.faker = Faker(['zh_CN'])

    @classmethod
    def get_props(cls):
        return [x for x in dir(cls) if isinstance(getattr(cls, x), property)]

    @property
    def uuid4(self):
        """0d1072bf-5d0f-4216-bea6-4df9deb8dae9"""
        return self.faker.uuid4()

    def uuid4_list(self, n=1):
        """['1727b3fa-1fc4-4849-aeb3-60790624fcbe']"""
        return [self.faker.uuid4() for _ in range(n)]

    @property
    def name(self):
        return "auto_" + self.faker.name()

    @property
    def phone_number(self):
        """生成手机号"""
        return self.faker.phone_number()

    @property
    def city(self):
        return self.faker.city()

    @property
    def address(self):
        return self.faker.address()

    @property
    def time_stamp(self):
        return int(time.time())

    @property
    def date_now_str(self):
        return datetime.datetime.now().strftime("%Y-%m-%d")

    @property
    def datetime_now_str(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def date_yesterday_str(self):
        return arrow.now().shift(days=-1).format("YYYY-MM-DD")

    @property
    def date_month_ago_str(self):
        return arrow.now().shift(months=-1).format("YYYY-MM-DD")

    @property
    def last_week_date(self):
        weekday = arrow.now().shift(weeks=-1).isoweekday()  # 获取当天的一周前是星期几
        mon = arrow.now().shift(weeks=-1, days=-(weekday - 1))
        sun = mon.shift(days=6)
        return mon.format("YYYY-MM-DD"), sun.format("YYYY-MM-DD")

    @property
    def last_week_monday(self):
        weekday = arrow.now().shift(weeks=-1).isoweekday()  # 获取当天的一周前是星期几
        mon = arrow.now().shift(weeks=-1, days=-(weekday - 1))
        return mon.format("YYYY-MM-DD")

    @property
    def last_week_sunday(self):
        weekday = arrow.now().shift(weeks=-1).isoweekday()  # 获取当天的一周前是星期几
        mon = arrow.now().shift(weeks=-1, days=-(weekday - 1))
        sun = mon.shift(days=6)
        return sun.format("YYYY-MM-DD")

    @property
    def last_month_date(self):
        last_month_date = arrow.now().shift(months=-1).date()
        year, month = last_month_date.year, last_month_date.month
        end = calendar.monthrange(int(year), int(month))[1]
        start_date = '%s-%s-01' % (year, month)
        end_date = '%s-%s-%s' % (year, month, end)
        return start_date, end_date

    @property
    def last_month_start_date(self):
        last_month_date = arrow.now().shift(months=-1).date()
        year, month = last_month_date.year, last_month_date.month
        start_date = '%s-%s-01' % (year, month)
        return start_date

    @property
    def last_month_end_date(self):
        last_month_date = arrow.now().shift(months=-1).date()
        year, month = last_month_date.year, last_month_date.month
        end = calendar.monthrange(int(year), int(month))[1]
        end_date = '%s-%s-%s' % (year, month, end)
        return end_date


if __name__ == '__main__':
    df = DataFaker()
    print(df.uuid4())
    print(df.uuid4_list(2))
