#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:validator.py
@time:2021/09/28
@email:tao.xu2008@outlook.com
@description:数据校验器
"""
import json
from jsonpath import jsonpath
from config import logger

# 数据验证方式
VALIDATE_TYPE = [
    "eq",  # 验证元素值等于
    "neq",  # 验证元素值不等于
    "ne",  # 验证元素值不等于
    "contain",  # 验证元素的字符串值中包含字符串"xxx"
    "contain_if_exist",  # 如果获取到元素不为空，则验证元素的字符串值中包含字符串"xxx"
    "in_list",  # 验证列表元素包含字符串"xxx"
    "not_in_list",  # 验证列表元素不包含字符串"xxx"
    "has_key",  # 验证字典元素包含的key或key列表
]


class ResponseValidator(object):
    """请求响应校验器"""
    def __init__(self):
        pass

    def format_res_expect(self, expect: dict):
        """
        期望输出的格式化处理：设置默认校验规则：eq
        :param expect:
        :return:返回字典
        """
        ep_keys = expect.keys()
        if set(ep_keys).issubset(set(VALIDATE_TYPE)):
            return expect
        return {"eq": expect}

    def get_text(self, res_text, expr, get_all=False):
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

    def validate_response_data(self, response, expr, expect_value, compare_method='eq'):
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
                    assert ev in actual_value, "期望({})：{}, 实际：{}\n响应：{}".format(compare_method, ev, actual_value,
                                                                                response.text)
            else:
                assert expect_value in actual_value, assert_err_msg
        else:
            raise Exception(f"错误的关键字'{compare_method}'，仅支持比较： eq-相等，neq/ne-不相等，contain-包含")
        logger.info("期望({}){}:{}, 实际{}:{} PASS...".format(compare_method, expr, expect_value, expr, actual_value))
        return True

    def validate(self, response, validate_kv: dict):
        """
        验证数据正确性
        :param response: requests.request()响应体
        :param validate_kv: {"eq": {"code": 401, "msg": "unauthorized"}, "contain":{"$..data.name":"beijing"}}
        :return:
        """
        logger.debug(validate_kv)
        validate_kv = self.format_res_expect(validate_kv)
        for compare, expect in validate_kv.items():
            for expr, expect_value in expect.items():
                if expect_value in ['', [], {}]:
                    logger.info("期望({}){}:{}, 跳过检查...".format(compare, expr, expect_value))
                    continue
                self.validate_response_data(response, expr, expect_value, compare)
        return True


if __name__ == '__main__':
    pass
