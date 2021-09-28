#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:base_api.py
@time:2021/09/26
@email:tao.xu2008@outlook.com
@description:接口请求处理
"""
import re
import requests
from prettytable import PrettyTable
from collections import defaultdict
from config import logger, get_global_value,  set_global_value
from core.parser import DataParser
from core.validator import ResponseValidator


class BaseApi(DataParser, ResponseValidator):
    """API key requests"""

    def __init__(self):
        super(BaseApi, self).__init__()
        self.step_table = []  # [('描述', 'Method', 'URL', 'Result')]

    def request(self, method, url, **kwargs):
        logger.info("{0} {1}\n参数：{2}".format(method, url, kwargs))
        response = requests.request(method, url, **kwargs)
        logger.debug("响应：{}".format(response.text))
        rc = response.status_code
        report_summary = get_global_value("report_summary", defaultdict(int))
        if str(rc).startswith('5') or rc in [404, ]:
            report_summary[str(rc)] += 1
        elif rc in [200, 400] and response.json().get('code', 0) == 500500:
            report_summary['500500'] += 1
        set_global_value('report_summary', report_summary)
        assert rc in [200, 400], "当前状态：{}".format(rc)  # 断言返回值状态
        return response

    def print_step_table(self, ps=""):
        field_names = ['序号', '描述', 'Method', 'URL', 'Result']
        p_table = PrettyTable(field_names)
        p_table.align['序号'] = 'l'
        p_table.align['描述'] = 'l'
        p_table.align['Method'] = 'l'
        p_table.align['URL'] = 'l'
        for idx, step in enumerate(self.step_table):
            p_table.add_row((idx+1, *step))
        logger.info("{}测试用例列表:\n{}".format(ps, p_table))
        return True

    @staticmethod
    def to_safe_name(s):
        return str(re.sub("[^a-zA-Z0-9_]+", "_", s))


if __name__ == "__main__":
    api = BaseApi()

