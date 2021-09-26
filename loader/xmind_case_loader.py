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
        'api-1':[
            {'suite':'', 'name': 'case1', 'desc': '描述', 'method': 'get', 'path': '/api/xxx/s', 'data': {}, 'res': ''},
            {case2},
            ],
        'api-2': [],
        }
        """
        canvas_data = {}
        api_case_dict_list = []
        canvas_topic = self.get_canvas_topic(canvas)
        module_name = canvas_topic.get('title')
        canvas_data['desc'] = canvas
        canvas_data['module'] = module_name
        api_list = canvas_topic.get('topics') or []
        for api in api_list:
            api_dict = {}
            api_name = api.get('title') if api.get('title') else ""
            api_desc = api.get('note') if api.get('note') else ""
            api_labels = api.get('labels')  # depends、host、sleep
            api_dict['api_name'] = api_name
            api_dict['api_desc'] = api_desc
            api_dict['api_desc'] = api_desc
            api_dict['depends'] = []  # depends 依赖标签
            api_dict['sleep'] = 0  # sleep 标签
            api_dict['skipif'] = ""  # skipif 标签
            host_tag = "host_" + HOST_TAG_CHOICE[0]  # host 标签
            if api_labels:
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
                        host_tag = "host_" + lb_host[-1]
            api_dict['host_tag'] = host_tag
            api_dict['test_case_list'] = []
            api_detail = api.get('topics')[0]
            path = api_detail.get('title') or ""
            rq = api_detail.get('topics')[0]
            method = rq.get('title') or ""
            api_dict['path'] = path
            api_dict['method'] = method
            case_cf_list = rq.get('topics')
            if api_name.startswith('#'):  # 被注释掉的接口，不解析用例参数
                continue
            for idx, case in enumerate(case_cf_list):
                if case.get('title').startswith('#'):  # 被注释掉的用例
                    continue
                case_dict = {}
                case_labels = case.get('labels')  # priority
                case_dict['module'] = module_name  # 模块名
                case_dict['api_name'] = api_name  # api名
                case_dict['host_tag'] = host_tag  # host_qw / host_mk
                case_dict['api_desc'] = api_desc  # api描述
                case_dict['depends'] = api_dict['depends']  # api依赖
                case_dict['sleep'] = api_dict['sleep']  # api sleep
                case_dict['skipif'] = api_dict['skipif']  # api skipif
                case_dict['name'] = f"{api_name}_" + str(idx+1).zfill(3)  # case名
                case_dict['desc'] = case.get('title')  # 描述
                case_dict['priority'] = ""  # 优先级
                if case_labels:
                    for clb in case_labels:
                        if clb in PRIORITY_TAG_CHOICE:
                            case_dict['priority'] = clb
                            break
                case_dict['method'] = method  # method: get/post/...
                case_dict['path'] = path  # api path
                case_input_output = case.get('topics')[0]
                case_dict['data'] = case_input_output.get('title')  # 输入
                output_set_vars = case_input_output.get('topics')
                str_expect = output_set_vars[0].get('title')
                try:
                    case_dict['expect'] = json.loads(str_expect, strict=False)  # 输出
                except Exception as e:
                    print("API:{0}->{1}\nJSON Content:{2}".format(module_name, api_name, str_expect))
                    raise e
                case_dict['set_vars'] = {}
                if len(output_set_vars) > 1:
                    str_set_vars = output_set_vars[1].get('title')
                    try:
                        case_dict['set_vars'] = json.loads(str_set_vars, strict=False)  # 需要设置为全局的变量，key-value， key为保存变量名，value为字段查询名或jsonpath
                    except Exception as e:
                        print("API:{0}->{1}\nJSON Content:{2}".format(module_name, api_name, str_set_vars))
                        raise e
                api_dict['test_case_list'].append(dict(case_dict))
            api_case_dict_list.append(api_dict)

        canvas_data['api_case_list'] = api_case_dict_list
        return canvas_data

    def get_xmind_data(self):
        return [self.get_canvas_data(cv) for cv in self.get_canvas_name_list()]


if __name__ == '__main__':
    pass
