#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:__init__.py.py
@time:2021/09/26
@email:tao.xu2008@outlook.com
@description:
"""

import os
from config.cf_rw import *
from config.options import *
from core.pkgs.xlog import LogWriter

# 项目root目录
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
# 创建配置对象为全局变量
cf = ConfigIni(os.path.join(root_dir, 'config', 'globals.ini'))
environment = ConfigIni(os.path.join(root_dir, 'config', 'environment.ini'))
# 创建日志对象为全局变量
logger = LogWriter(
    file_level=cf.get_str("LOGGER", "file_level"),
    console_level=cf.get_str("LOGGER", "console_level")
)
# 用例data地址: xmind/excel/csv文件地址
case_data_path = os.path.join(root_dir, 'data')
# 待处理api地址
api_xmind_path = os.path.join(root_dir, 'todo')
# pytest testcase 目录地址
testcase_path = os.path.join(root_dir, 'testcase')
# 报告目录地址
report_path = os.path.join(root_dir, 'report')
html_report_path = os.path.join(report_path, 'html')
xml_report_path = os.path.join(report_path, 'xml')

# 设置全局 key/value
_global_dict = {}


def set_global_value(key, value):
    global _global_dict
    # print(key, value)
    _global_dict[key] = value


def get_global_value(key, default_value=None):

    try:
        global _global_dict
        return _global_dict[key]
    except KeyError:
        if default_value is None:
            logger.error("No data for key:{}".format(key))
        return default_value


def get_global_dict():
    return _global_dict


__all__ = [
    "root_dir", "logger", "read_yaml", "cf", "environment",
    "case_data_path", "api_xmind_path", "testcase_path",
    "report_path", "html_report_path", "xml_report_path",
    "set_global_value", "get_global_value", "get_global_dict",
    "HOST_TAG_CHOICE", "SEVERITY_TAG_CHOICE", "PRIORITY_TAG_CHOICE"
]


if __name__ == '__main__':
    pass
