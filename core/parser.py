#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:paser.py
@time:2021/09/28
@email:tao.xu2008@outlook.com
@description:参数解析器
"""
import re
import json
from jsonpath import jsonpath
from config import logger
from core.data_factory.data_faker import *


class DataParser(object):
    """数据解析器"""
    # 缓存内容
    _cache = {}

    def __init__(self):
        pass

    @staticmethod
    def json_path(json_data, expr):
        """
        :param json_data: 传入json格式，发现json或者字典都ok
        :param expr: 要获取json内容的表达式，如："$..data.list[0].id"
        :return: 返回想要的字符串
        """
        # return jsonpath(json_data, f"$..{expr}")
        return jsonpath(json_data, expr)

    def set_cache_kv(self, key, value):
        self._cache[key] = value
        logger.debug("Set Cache: {}:{}".format(key, self._cache[key]))
        return True

    # 缓存中写入字段
    def set_cache(self, res: dict, key, expr):
        """
        保存字段至缓存中
        :param res: 传入的数据,如接口返回值
        :param key: 保存在缓存中的字段名
        :param expr: 传入数据中的字段名,即获取来源
        :return:
        """
        values = self.json_path(res, expr)
        # print(values)
        assert values is not False, f'set_cache: {expr}的值不存在\n{res}'
        self._cache[key] = values
        logger.debug("Set Cache:  {}:{}".format(key, self._cache[key]))
        return True

    # 获取缓存中字段
    def get_cache(self, key):
        """
        取缓存key 对应的value
        :param key:
        :return:
        """
        value = self._cache.get(key)
        assert value is not None, f'get_cache: {key}的值不存在'  # 取值失败直接让用例fail
        logger.debug("get_cache {0}:{1}".format(key, value))
        return value

    # 替换内容中的{{变量}}, 返回新字符串
    @staticmethod
    def _replace_var(content, var_name, var_value):
        """
        替换内容中的变量, 返回字符串型，即 $var --> value
        :param content:
        :param var_name: $var
        :param var_value:
        :return:
        """
        if not isinstance(content, str):
            content = json.dumps(content)
        var_name = "{{" + str(var_name) + "}}"
        var_value = json.dumps(var_value) if isinstance(var_value, (list, dict, tuple, set)) else str(var_value)
        content = content.replace(var_name, var_value)
        return content

    # 从内容中提取所有变量名
    @staticmethod
    def _extract_variables(content: str):
        """
        从内容中提取所有变量名, 变量格式为{{variable}}
        :param content:
        :return: 返回变量名list
        """
        variable_regexp = r"{{([^\n}]+)}}"
        if not isinstance(content, str):
            content = str(content)
        try:
            return re.findall(variable_regexp, content)
        except TypeError:
            return []

    # 提取变量->读取cache中对应变量值->替换变量名
    def replace_variables(self, content: str):
        """
        从字符传 content 中提取变量 -> 读取cache中对应变量值 -> 替换content中变量名
        :param content:
        :return:
        """
        var_list = self._extract_variables(content)
        for var_name in var_list:
            vaild_var_name = var_name.strip()  # 处理变量名前后空白符
            if vaild_var_name.endswith("]"):
                # 列表取元素
                regexp = r"([\w_]+)\[(\d+)\]"
                vns = re.findall(regexp, vaild_var_name)
                if vns:
                    k, idx = vns[0]
                    var_value = self.get_cache(k)[int(idx)]
                else:
                    var_value = self.get_cache(vaild_var_name)
            elif vaild_var_name.endswith(")"):
                # 调用方法取返回值
                var_value = eval(var_name)
            else:
                var_value = self.get_cache(vaild_var_name)
            content = self._replace_var(content, var_name, var_value)
        return content

    # content字符串变量的解析、处理， 返回字典
    def content_to_dict(self, content: str):
        """
        content字符串变量的解析、处理， 返回字典
        :param content:
        :return:
        """
        content = self.replace_variables(content)  # 替换字符串中变量
        try:
            return json.loads(content, strict=False)
        except Exception as e:
            logger.error("JSONDecodeError: JSON Content: {}".format(content))
            raise e


if __name__ == '__main__':
    js = '{"data":[{"group_id":12, "id": "aad", "tags":["111a"]}, {"group_id":345, "id": "ssa", "tags":["222a"]}]}'
    print(jsonpath(json.loads(js), "$..data[?(@.length>1)]"))
