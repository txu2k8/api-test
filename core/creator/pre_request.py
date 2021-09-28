#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:pre_request.py
@time:2021/09/28
@email:tao.xu2008@outlook.com
@description:
"""
from config import cf, environment, get_global_value, get_global_dict, set_global_value
from core.api.base_api import BaseApi


class PreRequest(object):
    """请求前的一些操作，如通过计费获取超管session id"""
    api = BaseApi()
    test_env = get_global_value("test_env", "default")
    # environment.ini文件中<测试环境>下的所有k/v
    for k, v in environment.get_kvs(test_env).items():
        set_global_value(k, v)
    # 把globals.ini文件中<WEIXIN>下的所有k/v存入api类的cache中
    for k, v in cf.get_kvs("WEIXIN").items():
        set_global_value(k, v)

    @staticmethod
    def setup():
        print("\n")

    @classmethod
    def setup_class(cls):
        # 初始化
        cls.api.step_table = []
        cls.api._cache = {}
        cls.User_Agent = cf.get_str("HEADERS", "User-Agent")
        cls.Authorization = get_global_value("session_id")

        # 把全局变量写入api类cache，如全局的mock数据
        for k, v in get_global_dict().items():
            cls.api.set_cache_kv(k, v)

        # 为每个class新生成mock数据并写入api类cache
        # mock = MockData()
        # for k in mock.get_props():
        #     v = mock.__getattribute__(k)
        #     logger.info("生成mock数据并写入缓存：{}:{}".format(k, v))
        #     cls.api.set_cache_kv(k, v)

    def request_data_parse(self, kwargs: dict):
        """
        解析用例配置参数，返回requests.request方法的参数字典
        :param kwargs: case_data
        :return:
        """
        headers = {
            "User-Agent": self.User_Agent,
            "Authorization": self.Authorization,
            "Content-Type": "application/json",
        }
        method = kwargs["method"].upper()
        host = get_global_value(kwargs.get("host_tag", "host_mk"))
        url = self.api.replace_variables(host+kwargs["path"])  # 解析path中变量值
        req_data = self.api.content_to_dict(kwargs["req_data"])  # 解析req_data中变量值
        params_append = []
        if "params_append" in req_data:  # 自定义参数类型 --如： {"params_append":[1,2]}  ==>> /path/1/2
            params_append = req_data.pop("params_append")
        for pa in params_append:
            url += "/{}".format(pa)

        data_keys = req_data.keys()
        if len(data_keys) > 0 and set(data_keys).issubset({"params", "json", "data"}):  # 即传入参数指定了参数类型
            data = req_data
        else:
            data = {"params" if method == "GET" else "json": req_data}

        return dict(**{'method': method, 'url': url, 'headers': headers}, **data)


if __name__ == '__main__':
    pass
