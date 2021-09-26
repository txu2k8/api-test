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
import time
import json
import requests
from prettytable import PrettyTable
from jsonpath import jsonpath
from collections import defaultdict
from config import logger, get_global_value,  set_global_value
from data_factory import data_faker  # 不要删除，有eval操作


class BaseApi(object):
    """API key requests"""
    # 缓存内容
    _cache = {}
    # 验证数据方式
    _validate_type = [
        "eq",  # 验证元素值等于
        "neq",  # 验证元素值不等于
        "ne",  # 验证元素值不等于
        "contain",  # 验证元素的字符串值中包含字符串"xxx"
        "contain_if_exist",  # 如果获取到元素不为空，则验证元素的字符串值中包含字符串"xxx"
        "in_list",  # 验证列表元素包含字符串"xxx"
        "not_in_list",  # 验证列表元素不包含字符串"xxx"
        "has_key",  # 验证字典元素包含的key或key列表
    ]

    def __init__(self):
        # API请求列表
        self.step_table = []  # [('描述', 'Method', 'URL', 'Result')]

    def request(self, method, url, **kwargs):
        logger.info("{0} {1}\n参数：{2}".format(method, url, kwargs))
        response = requests.request(method, url, **kwargs)
        logger.debug("响应：{}".format(response.text))
        rc = response.status_code
        report_summary = get_global_value("report_summary", defaultdict(int))
        if str(rc).startswith('5'):
            report_summary['5xx'] += 1
        elif rc == 404:
            report_summary['404'] += 1

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
    def json_path(json_data, expr):
        """
        :param json_data: 传入json格式，发现json或者字典都ok
        :param expr: 要获取json内容的表达式，如："$..data.list[0].id"
        :return: 返回想要的字符串
        """
        # return jsonpath(json_data, f"$..{expr}")
        return jsonpath(json_data, expr)

    @staticmethod
    def to_safe_name(s):
        return str(re.sub("[^a-zA-Z0-9_]+", "_", s))

    def set_cache_kv(self, key, value):
        if isinstance(value, str) and "$" in value:
            value = self.replace_variables(value)
        self._cache[key] = {
            'value': value,
            'time': int(time.time())
        }
        logger.debug("Set Cache: {}:{}".format(key, self._cache[key]))
        return True

    # 缓存中写入字段
    def set_cache(self, res: dict, expr, key):
        """
        保存字段至缓存中
        :param res: 传入的数据,如接口返回值
        :param expr: 传入数据中的字段名,即获取来源
        :param key: 保存在缓存中的字段名
        :return:
        """
        if isinstance(expr, str) and "$" in expr:
            expr = self.replace_variables(expr)
        values = self.json_path(res, expr)
        # print(values)
        assert values is not False, f'set_cache: {expr}的值不存在\n{res}'
        self._cache[key] = {
            'value': values[0] if isinstance(values, list) else values,
            'time': int(time.time())
        }
        logger.debug("Set Cache:  {}:{}".format(key, self._cache[key]))
        return True

    # 获取缓存中字段
    def get_cache(self, key):
        """
        取缓存key 对应的value
        :param key:
        :return:
        """
        values = self.json_path(self._cache, key)
        assert values is not False, f'get_cache: {key}的值不存在'  # 取值失败直接让用例fail
        if values is not False:
            value = values[0].get('value')
            logger.debug("get_cache {0}:{1}".format(key, value))
            return value
        logger.error(f'get_cache: {key}的值不存在')
        return ''

    @staticmethod
    def get_text(res_text, expr, get_all=False):
        """
        if key not exist, return bool False
        :param res_text:
        :param expr: jsonpath 表达式，如 $..data.list[0].id
        :param get_all: True 返回列表，False-返回列表中第一个值
        :return:
        """
        if res_text is None:
            return None
        if not expr.startswith("$.."):
            expr = "$.." + expr

        try:
            txt = json.loads(res_text)
            value = jsonpath(txt, expr)
            if get_all:
                return value
            elif value and len(value) >= 1:
                return value[0]
            else:
                return value
        except Exception as e:
            logger.error(e)
            raise Exception(e)

    def validate_status_code(self, response, expect_value, compare_method='eq'):
        """
        验证状返回态码
        :param response:
        :param expect_value:
        :param compare_method:
        :return:
        """
        expr = "status_code"
        actual_value = response.status_code
        if compare_method == "eq":
            assert actual_value == expect_value, (actual_value, expect_value)
        elif compare_method in ["neq", "ne"]:
            assert actual_value != expect_value, (actual_value, expect_value)
        else:
            raise Exception(f"错误的关键字'{compare_method}'，仅支持比较： eq-相等，neq/ne-不相等")
        logger.info("期望({}){}:{}, 实际{}:{} PASS...".format(compare_method, expr, expect_value, expr, actual_value))
        return True

    def validate_response_data(self, response, expr, expect_value, compare_method='eq'):
        if isinstance(expect_value, str) and "$" in expect_value:
            expect_value = self.replace_variables(expect_value)
        if isinstance(expr, str) and "$" in expr:
            expr = self.replace_variables(expr)

        get_all = True if compare_method in ["in_list", "not_in_list"] else False
        actual_value = self.get_text(response.text, expr, get_all=get_all)
        assert_err_msg = "期望({})：{}, 实际：{}\n响应：{}".format(compare_method, expect_value, actual_value, response.text)
        # if not actual_value:
        #     logger.warning("未取到返回数据")
        #     logger.warning((expr, response.text))
        #     return True
        if compare_method == "eq":
            assert actual_value == expect_value, assert_err_msg
        elif compare_method in ["neq", "ne"]:
            assert actual_value != expect_value, assert_err_msg
        elif compare_method in ["contain"]:
            assert expect_value in actual_value, assert_err_msg
        elif compare_method in ["contain_if_exist"]:
            if actual_value:
                assert expect_value in actual_value, assert_err_msg
            else:
                logger.warning("响应json中没找到对应的值：{}".format(expr))
        elif compare_method in ["in_list"]:
            assert expect_value in actual_value, assert_err_msg
        elif compare_method in ["not_in_list"]:
            assert expect_value not in actual_value, assert_err_msg
        elif compare_method in ["has_key"]:
            assert isinstance(actual_value, dict)
            if isinstance(expect_value, list):
                for ev in expect_value:
                    assert ev in actual_value, "期望({})：{}, 实际：{}\n响应：{}".format(compare_method, ev, actual_value, response.text)
            else:
                assert expect_value in actual_value, assert_err_msg
        else:
            raise Exception(f"错误的关键字'{compare_method}'，仅支持比较： eq-相等，neq/ne-不相等，contain-包含")
        logger.info("期望({}){}:{}, 实际{}:{} PASS...".format(compare_method, expr, expect_value, expr, actual_value))
        return True

    def validate(self, response, validate_kv):
        """
        验证数据正确性
        :param response:
        :param validate_kv: {"eq": {"code": 401, "msg": "unauthorized"}, "contain":{"$..data.name":"beijing"}}
        :return:
        """
        logger.debug(validate_kv)
        for compare, expect in validate_kv.items():
            for expr, expect_value in expect.items():
                if expect_value in ['', [], {}]:
                    logger.info("期望({}){}:{}, 跳过检查...".format(compare, expr, expect_value))
                    continue
                # self.validate_status_code(response, expr, expect_value, compare)
                self.validate_response_data(response, expr, expect_value, compare)
        return True

    # 替换内容中的变量, 返回字符串型
    @staticmethod
    def replace_var(content, var_name, var_value):
        """
        替换内容中的变量, 返回字符串型，即 $var --> value
        :param content:
        :param var_name: $var
        :param var_value:
        :return:
        """
        if not isinstance(content, str):
            content = json.dumps(content)
        var_name = "$" + var_name
        var_value = json.dumps(var_value) if isinstance(var_value, (list, dict, tuple, set)) else str(var_value)
        content = content.replace(str(var_name), var_value)
        return content

    # 从内容中提取所有变量名, 变量格式为$variable,返回变量名list
    @staticmethod
    def extract_variables(content: str):
        variable_regexp = r"\$([\w\[\d+\]_(=)]+)"  # \$([\w_]+)
        if not isinstance(content, str):
            content = str(content)
        try:
            return re.findall(variable_regexp, content)
        except TypeError:
            return []

    def replace_variables(self, content: str):
        """
        从字符传 content 中提取变量 -> 读取cache中对应变量值 -> 替换content中变量名
        :param content:
        :return:
        """
        # 检查是否存在变量
        var_list = self.extract_variables(content)
        for var_name in var_list:
            if var_name.endswith("]"):
                # 列表取元素
                regexp = r"([\w_]+)\[(\d+)\]"
                vns = re.findall(regexp, var_name)
                if vns:
                    k, idx = vns[0]
                    var_value = self.get_cache(k)[int(idx)]
                else:
                    var_value = self.get_cache(var_name)
            elif var_name.endswith(")"):
                # 调用方法取返回值
                var_value = eval("data_faker."+var_name)
            else:
                var_value = self.get_cache(var_name)
            content = self.replace_var(content, var_name, var_value)
        return content

    def do_url(self, url: str):
        return self.replace_variables(url)

    def do_params(self, params: str):
        """
        输入参数变量的解析、处理， 返回字典
        :param params:
        :return:
        """
        content = self.replace_variables(params)
        try:
            return json.loads(content, strict=False)
        except Exception as e:
            logger.error("JSONDecodeError: JSON Content: {}".format(content))
            raise e

    def do_expect(self, expect: dict):
        """
        期望输出的处理， 返回字典  -- 添加
        :param expect:
        :return:
        """
        ep_keys = expect.keys()
        if set(ep_keys).issubset(set(self._validate_type)):
            return expect
        return {"eq": expect}


if __name__ == "__main__":
    # BaseApi().getApiTime()
    api = BaseApi()
    # dept_ids = [1, 2, 3]
    # json_content = '{"id":"$dept_ids[2]"}'
    # api.set_cache_kv("dept_ids", dept_ids)
    # print(api.do_params(json_content))
    # print(api.get_text('{"success":true,"code":500200,"msg":"ok","data":{}}', "success"))
    js = '{"data":[{"group_id":12, "id": "aad", "tags":["111a"]}, {"group_id":345, "id": "ssa", "tags":["222a"]}]}'
    # api.set_cache(json.loads(js), "$..data[?(@.group_id>=10)].id", "kk")
    print(jsonpath(json.loads(js), "$..data[?(@.length>1)]"))
    # api.set_cache(json.loads(js), "$..data.length", "kk")
