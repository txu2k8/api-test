#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:get_environment_data.py
@time:2021/09/28
@email:tao.xu2008@outlook.com
@description:获取、爬取当前环境相关数据
"""
from config import environment, get_global_value
from spiders.employee import EmployeeSpider
from spiders.department import DepartmentSpider


class GetEnvData(object):
    """爬取当前环境相关数据"""

    def __init__(self, session_id=None):
        self.session_id = session_id
        self.emp = EmployeeSpider(session_id)
        self.dept = DepartmentSpider(session_id)
        self.login_session_data = self.dept.get_login_session()

    @classmethod
    def get_props(cls):
        return [x for x in dir(cls) if isinstance(getattr(cls, x), property)]

    @property
    def login_uid(self):
        return self.login_session_data.get("uid")

    @property
    def login_name(self):
        return self.login_session_data.get("name")

    @property
    def login_qw_user_id(self):
        return self.login_session_data.get("qwUserId")  # 如'alex'

    @property
    def login_agent_id(self):
        return self.login_session_data.get("agentId")  # 如'1000002'

    @property
    def login_department_id(self):
        return self.login_session_data.get("qwDepartmentId")[0]

    @property
    def department_ids(self):
        return self.dept.departments_ids

    @property
    def department_names(self):
        return self.dept.departments_names

    @property
    def employee_names(self):
        return self.emp.employees_names

    @property
    def employee_ids(self):
        return self.emp.employees_ids

    @property
    def employees_roles(self):
        return self.emp.employees_roles

    @property
    def employees_department_ids(self):
        return self.emp.employees_department_ids

    # ==================== data for callback ====================
    @property
    def external_contact_access_token(self):
        test_env = get_global_value("test_env")
        corp_secret = environment.get_str(test_env, "external_contact_corp_secret")
        return self.dept.get_access_token(corp_secret)


if __name__ == '__main__':
    pass
