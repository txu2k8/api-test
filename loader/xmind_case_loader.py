#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:xmind_case_loader.py
@time:2021/09/26
@email:tao.xu2008@outlook.com
@description:xmind文件格式测试用例读取
"""

import re
import json
from xmindparser import xmind_to_dict

from config import HOST_TAG_CHOICE, SEVERITY_TAG_CHOICE
from pkgs.utils import is_contains_chinese


def to_safe_name(s):
    return str(re.sub("[^a-zA-Z0-9_]+", "_", s))


class XmindCaseLoader(object):
    """
    读取xmind内容，返回用例数据：
    字典列表（list[dict1,dict2]）
    """
    def __init__(self, file_path, canvas=""):
        self.file_path = file_path
        self.canvas = canvas
        self.xmind_dict_list = xmind_to_dict(file_path)

    def get_canvas_name_list(self):
        return [self.canvas] if self.canvas else [cv.get('title') for cv in self.xmind_dict_list]

    def get_canvas_topic(self, canvas="画布 1"):
        """
        根据初始指定的画布名称（对应于excel的sheel表），返回该画布的数据
        :return: {'title': '', 'topics': []}
        """
        for cv in self.xmind_dict_list:
            if cv.get('title') == canvas:
                return cv.get('topic')
        else:
            raise Exception("Xmind中画布<{}>不存在!".format(canvas))

    def get_canvas_data(self, canvas):
        """
        获取画布内所有API-CASE信息
        :return: {
            "suite": "SuiteName",
            "desc": "Suite Description",
            "api_list": [
                {
                    "api_name": ""
                    "test_case_list": [
                        {
                            "case_name": ""
                            "data": "{}"
                            "expect": "{}"
                            "set_values": "{}"
                        }
                    ]
                }
            ]
        }
        """
        canvas_data = {}
        canvas_topic = self.get_canvas_topic(canvas)
        suite_name = canvas_topic.get('title')
        api_list = canvas_topic.get('topics', [])

        canvas_data['desc'] = canvas
        canvas_data['suite'] = suite_name
        canvas_data['api_list'] = []
        # 读取api信息
        for api in api_list:
            api_dict = {}
            api_dict['priority'] = 0
            api_title = api.get('title', '')
            api_note = api.get('note', '')
            # title、note：把有中文符号的当作描述
            if is_contains_chinese(api_title):
                api_name, api_desc = to_safe_name(api_note), api_title
            else:
                api_name, api_desc = to_safe_name(api_title), api_note
            api_dict['api_name'] = api_name
            api_dict['api_desc'] = api_desc

            api_topics = api.get('topics')
            if not api_topics:
                continue  # steup/teardown 没有下级子主题
            # api 标记处理 -- makers
            api_makers = api.get('makers', [])
            for amk in api_makers:
                priority = amk.split('priority-')  # priority 优先级处理
                if len(priority) == 2:
                    api_dict['priority'] = int(priority[-1])
            # api 标签处理 -- labels
            api_labels = api.get('labels', [])
            api_dict['depends'] = []  # depends 依赖标签
            api_dict['sleep'] = 0  # sleep 标签
            api_dict['skipif'] = ""  # skipif 标签
            host_tag = HOST_TAG_CHOICE[0]  # host 标签
            for alb in api_labels:
                lb_dps = alb.split("depends=")
                lb_dps2 = alb.split("name=")
                lb_sleep = alb.split("sleep=")
                lb_skipif = alb.split("skipif=")
                lb_host = alb.split("host=")
                if len(lb_dps) == 2:
                    api_dict['depends'].append(lb_dps[-1])
                if len(lb_dps2) == 2:
                    api_dict['depends'].append(lb_dps2[-1])
                if len(lb_sleep) == 2:
                    api_dict['sleep'] = int(lb_sleep[-1])
                if len(lb_skipif) == 2:
                    api_dict['skipif'] = lb_skipif[-1]
                if len(lb_host) == 2 and lb_host[-1] in HOST_TAG_CHOICE:
                    host_tag = lb_host[-1]
            api_dict['host_tag'] = "host_" + host_tag

            # 读取api详情
            api_detail = api_topics[0]
            path = api_detail.get('title', '')
            api_req = api_detail.get('topics')
            if not api_req:
                continue  # steup/teardown 没有下级子主题
            rq = api_req[0]
            method = rq.get('title', '')
            api_dict['path'] = path
            api_dict['method'] = method

            # 读取case配置
            case_cf_list = rq.get('topics')
            api_dict['test_case_list'] = []
            if api_name.startswith('#'):  # 被注释掉的接口，不解析用例参数
                continue
            for idx, case in enumerate(case_cf_list):
                if case.get('title', '').startswith('#'):  # 被注释掉的用例
                    continue
                case_dict = {}
                # 继承API配置属性
                case_dict['suite'] = suite_name  # 模块名
                case_dict['api_name'] = api_dict['api_name']  # api名
                case_dict['api_desc'] = api_dict['api_desc']  # api描述
                case_dict['priority'] = api_dict['priority']  # 优先级
                case_dict['host_tag'] = api_dict['host_tag']  # host_qw / host_mk
                case_dict['depends'] = api_dict['depends']  # api依赖
                case_dict['sleep'] = api_dict['sleep']  # api sleep
                case_dict['skipif'] = api_dict['skipif']  # api skipif
                case_dict['method'] = api_dict['method']  # method: get/post/...
                case_dict['path'] = api_dict['path']  # api path
                # case 配置
                case_dict['name'] = "{}_{}".format(api_name, str(idx+1).zfill(3))  # case名
                case_dict['desc'] = case.get('title', '')  # 描述
                case_dict['severity'] = ""  # 严重度
                # case 标签处理
                case_labels = case.get('labels', [])
                for clb in case_labels:
                    lb_severity = clb.split("severity=")
                    if len(lb_severity) == 2:
                        severity = lb_severity[-1]
                        if severity in SEVERITY_TAG_CHOICE:
                            case_dict['severity'] = severity
                            break  # 只取一个

                # case 输入、输出、设置变量 处理
                case_data = case.get('topics')
                req_data = case_data[0].get('title', '{}')  # 输入参数
                res_expect = case_data[1].get('title', '{}')  # 期望输出
                # 需要设置为全局的变量，key-value， key为保存变量名，value为字段查询名或jsonpath
                res_set_cache = case_data[2].get('title', '{}') if len(case_data) > 2 else '{}'
                case_dict['req_data'] = req_data
                case_dict['res_expect'] = res_expect
                case_dict['res_set_cache'] = res_set_cache
                api_dict['test_case_list'].append(dict(case_dict))
            canvas_data['api_list'].append(api_dict)

        return canvas_data

    def get_xmind_data(self):
        return [self.get_canvas_data(cv) for cv in self.get_canvas_name_list()]


if __name__ == '__main__':
    xcl = XmindCaseLoader("../doc/用例设计规范.xmind", "用例设计-示例")
    res = xcl.get_xmind_data()
    # print(res)
    print(json.dumps(res, ensure_ascii=False))
