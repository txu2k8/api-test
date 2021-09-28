#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:employee.py
@time:2021/09/29
@email:tao.xu2008@outlook.com
@description:
"""
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import logger, root_dir, read_yaml
from core.spiders.auth import Auth


class EmployeeSpider(Auth):
    """爬取并解析 员工信息"""
    _employees = None
    _sorted_employees = None

    def __init__(self, session_id=None):
        super(EmployeeSpider, self).__init__(session_id)
        pass

    def get_role_info(self):
        """
        爬取员工角色信息
        :return:
        """
        kwargs = read_yaml(os.path.join(root_dir, "core/spiders/spiders.yaml"))["employee_role"]
        rq = self.assignment(kwargs["request"])
        url = self.url + rq['path']
        data = {
          "page": 1,
          "pageSize": 1000
        }
        response = self.api.request(rq['method'], url, headers=rq["headers"], json=data).json()
        res = response.get('data').get('list')
        role_info = {}
        for role in res:
            role_info[role.get('id')] = role.get('name')
        return role_info

    def get_dept_employees(self, dept_id, rq, role_info):
        """
        爬取部门员工信息
        :return:
        """
        dept_employee_list = []
        url = self.url + rq['path'] + f"?deptId={dept_id}&page=1&pageSize=10000"
        response = self.api.request(rq['method'], url, headers=rq["headers"]).json()
        res = response.get('data').get('list')
        for e in res:
            employee_info = defaultdict()
            employee_info['name'] = e.get('name')
            employee_info['id'] = e.get('_id')
            employee_info['department_id'] = 1
            department_ids = e.get('department', [])
            for department_id in department_ids:
                employee_info['department_id'] = department_id
                continue
            employee_info['role'] = ""
            role_ids = e.get('role', [])
            for role_id in role_ids:
                role_name = role_info.get(role_id, "")
                employee_info['role'] = role_name
                continue
            dept_employee_list.append(employee_info)
        return dept_employee_list

    def get_employees(self, dept_ids=None):
        """
        爬取员工信息
        :param dept_ids: 获取指定部门ID列表的员工
        :return:
        """
        logger.info("获取员工信息...")
        role_info = self.get_role_info()
        kwargs = read_yaml(os.path.join(root_dir, "core/spiders/spiders.yaml"))["employee"]
        rq = self.assignment(kwargs["request"])
        if dept_ids is None:
            return self.get_dept_employees(1, rq, role_info)

        res_data = []
        futures = set()
        with ThreadPoolExecutor(max_workers=8) as executor:
            for dept_id in dept_ids:
                futures.add(executor.submit(self.get_dept_employees, dept_id, rq, role_info))
        for future in as_completed(futures):
            res_data.extend(future.result())
        return res_data

    @property
    def employees(self):
        if self._employees is None:
            self._employees = self.get_employees()
        return self._employees

    @property
    def sorted_employees(self):
        if self._sorted_employees is None:
            self._sorted_employees = sorted(self.employees, key=lambda x: x["name"])
        return self._sorted_employees

    @property
    def employees_names(self):
        return [emp['name'] for emp in self.sorted_employees]

    @property
    def employees_ids(self):
        return [emp['id'] for emp in self.sorted_employees]

    @property
    def employees_roles(self):
        return [emp['role'] for emp in self.sorted_employees]

    @property
    def employees_department_ids(self):
        return [emp['department_id'] for emp in self.sorted_employees]


if __name__ == '__main__':
    ep = EmployeeSpider()
    print(len(ep.sorted_employees))
    print(ep.sorted_employees)
    logger.info("")
