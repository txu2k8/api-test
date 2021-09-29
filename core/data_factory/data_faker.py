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


faker = Faker(['zh_CN'])


def uuid4():
    """0d1072bf-5d0f-4216-bea6-4df9deb8dae9"""
    return faker.uuid4()


def uuid4_list(n=1):
    """['1727b3fa-1fc4-4849-aeb3-60790624fcbe']"""
    return [faker.uuid4() for _ in range(n)]


def name():
    return "auto_" + faker.name()


def phone_number():
    """生成手机号"""
    return faker.phone_number()


def city():
    return faker.city()


def address():
    return faker.address()


def time_stamp():
    return int(time.time())


def date_now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def datetime_now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def date_yesterday_str():
    return arrow.now().shift(days=-1).format("YYYY-MM-DD")


def date_month_ago_str():
    return arrow.now().shift(months=-1).format("YYYY-MM-DD")


def last_week_date():
    weekday = arrow.now().shift(weeks=-1).isoweekday()  # 获取当天的一周前是星期几
    mon = arrow.now().shift(weeks=-1, days=-(weekday - 1))
    sun = mon.shift(days=6)
    return mon.format("YYYY-MM-DD"), sun.format("YYYY-MM-DD")


def last_week_monday():
    weekday = arrow.now().shift(weeks=-1).isoweekday()  # 获取当天的一周前是星期几
    mon = arrow.now().shift(weeks=-1, days=-(weekday - 1))
    return mon.format("YYYY-MM-DD")


def last_week_sunday():
    weekday = arrow.now().shift(weeks=-1).isoweekday()  # 获取当天的一周前是星期几
    mon = arrow.now().shift(weeks=-1, days=-(weekday - 1))
    sun = mon.shift(days=6)
    return sun.format("YYYY-MM-DD")


def last_month_date():
    return arrow.now().shift(months=-1).date().strftime('%Y-%m-%d')


def last_month_start_date():
    last_m_date = arrow.now().shift(months=-1).date()
    year, month = last_m_date.year, last_m_date.month
    start_date = '%s-%s-01' % (year, month)
    return start_date


def last_month_end_date():
    last_m_date = arrow.now().shift(months=-1).date()
    year, month = last_m_date.year, last_m_date.month
    end = calendar.monthrange(int(year), int(month))[1]
    end_date = '%s-%s-%s' % (year, month, end)
    return end_date


if __name__ == '__main__':
    print(uuid4())
    print(uuid4_list(2))
