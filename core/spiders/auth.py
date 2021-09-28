#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:auth.py
@time:2021/09/29
@email:tao.xu2008@outlook.com
@description:
"""
import os
from config import cf, environment, get_global_value, read_yaml, root_dir, logger
from core.api.base_api import BaseApi


class Auth:
    """通过计费获取超管session id"""
    test_env = get_global_value("test_env", "ali")  # 调试使用默认值ali

    def __init__(self, session_id=None):
        self.User_Agent = cf.get_str("HEADERS", "User-Agent")
        self.url = environment.get_str(self.test_env, 'host_mk')
        self.company_id = environment.get_str(self.test_env, 'company_id')
        self.host_bill = environment.get_str(self.test_env, 'host_bill')

        self.api = BaseApi()
        self.Authorization = session_id or self.get_session()

    def get_session(self):
        """通过计费获取超管session id"""
        kwargs = read_yaml(os.path.join(root_dir, "core/spiders/spiders.yaml"))
        rq = kwargs["auth"]["request"]
        url = self.host_bill + rq['path']
        res = self.api.request(rq['method'], url, headers=rq["headers"], params={"id": self.company_id})
        res_json = res.json()
        if res_json.get('code', 0) != 1:
            logger.error(res_json)
        return res_json.get('data', {}).get('url').split('sessionId=')[1]

    def get_bill_session(self):
        """获取计费系统token"""
        kwargs = read_yaml(os.path.join(root_dir, "core/spiders/spiders.yaml"))
        rq = kwargs["bill"]["request"]
        url = self.host_bill + rq['path']
        res = self.api.request(rq['method'], url, headers=rq["headers"], json=rq['data'])
        res_json = res.json()
        if res_json.get('code', 0) != 1:
            logger.error(res_json)
        return res_json.get('data', {}).get('sid')

    def get_login_session(self):
        """获取当前登录用户信息"""
        kwargs = read_yaml(os.path.join(root_dir, "core/spiders/spiders.yaml"))
        rq = kwargs["auth"]["request"]
        host_qw = environment.get_str(self.test_env, 'host_qw')
        host = host_qw.replace("https://", "https://{}-".format(environment.get_str(self.test_env, 'corp_id')))
        url = host + "/biz/v1/qw_account/session/get_login_session"
        params = {"sessionId": self.Authorization, "type": "pc"}
        res = self.api.request("GET", url, headers=rq["headers"], params=params)
        # print(res.json())
        res_data = res.json().get('data', {})
        login_session = {
            "sid": res_data.get("sid"),  # session id
            "uid": res_data.get("uid"),  # user id
            "name": res_data.get("name"),
            "account": res_data.get("account"),  # company id
            "identity": res_data.get("identity"),  # identity 身份，如：admin
            "qwUserId": res_data.get("qwUserId"),  # qwUserId, 如'alex'
            "corpId": res_data.get("corpId"),  # corpId
            "agentId": res_data.get("agentId"),  # agentId
            "gender": res_data.get("gender"),  # gender性别 1-男
            "email": res_data.get("email"),  # email
            "qwDepartmentId": res_data.get("qwDepartmentId"),  # qwDepartmentId, [7]
        }
        return login_session

    def get_access_token(self, corp_secret):
        """
        获取access_token是调用企业微信API接口的第一步，相当于创建了一个登录凭证，其它的业务API接口，
        都需要依赖于access_token来鉴权调用者身份。因此开发者，在使用业务接口前，要明确access_token的颁发来源，
        使用正确的access_token。
        :param corp_secret: 应用的凭证密钥
        :return: access_token
        """
        url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
        res = self.api.request("GET", url,
                               params={
                                   "corpid": environment.get_str(self.test_env, 'corp_id'),
                                   "corpsecret": corp_secret,  # 应用的凭证密钥
                               })
        return res.json().get('access_token', None)

    def assignment(self, kwargs):
        """
        封装操作： 对配置文件的配置进行赋值。
        如果有默认值，直接使用默认值，否则赋值为类属性对应key的value
        :param kwargs:
        :return:
        """
        for key, value in kwargs.items():
            if isinstance(value, dict):
                self.assignment(value)
            elif value:
                pass  # 配置文件设置又默认值，使用默认值
            else:
                safe_key = self.api.to_safe_name(key)
                if hasattr(self, safe_key):
                    kwargs[key] = getattr(self, safe_key)  # 反射，设置为类/实例属性
        return kwargs


if __name__ == '__main__':
    print(Auth().Authorization)
    # print(Auth().get_access_token("dy4nNXVGOznLaPwzEnX9zOble1VVGm4T3lh-W3N-tP8"))
