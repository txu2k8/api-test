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
from pkgs.xlog import LogWriter

# 项目root目录
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
# 创建配置对象为全局变量
cf = ConfigIni(os.path.join(root_dir, 'config', 'globals.ini'))
# 创建日志对象为全局变量
logger = LogWriter(
    file_level=cf.get_str("LOGGER", "file_level"),
    console_level=cf.get_str("LOGGER", "console_level")
)
# 用例地址
case_xmind_path = os.path.join(root_dir, 'data')
# 待处理api地址
api_xmind_path = os.path.join(root_dir, 'todo')
# 报告目录
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
        return default_value


def get_global_dict():
    return _global_dict


__all__ = [
    "root_dir", "logger", "read_yaml", "cf", "case_xmind_path", "api_xmind_path",
    "report_path", "html_report_path", "xml_report_path",
    "set_global_value", "get_global_value", "get_global_dict",
    "HOST_TAG_CHOICE", "PRIORITY_TAG_CHOICE"
]


if __name__ == '__main__':
    pass
