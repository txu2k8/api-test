#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:department.py
@time:2021/09/29
@email:tao.xu2008@outlook.com
@description:
"""
import os
from collections import defaultdict
from config import root_dir, read_yaml
from core.spiders.auth import Auth


class DepartmentSpider(Auth):
    """爬取并解析 部门信息"""
    _departments = None
    _sorted_departments = None

    def __init__(self, session_id=None):
        super(DepartmentSpider, self).__init__(session_id)
        pass

    def get_departments(self):
        kwargs = read_yaml(os.path.join(root_dir, "core/spiders/spiders.yaml"))["department"]
        rq = self.assignment(kwargs["request"])
        url = self.url + rq["path"]
        response = self.api.request(rq['method'], url, headers=rq["headers"]).json()
        res = response.get('data').get('list')
        res_data = []
        for d in res:
            department_info = defaultdict()
            # if d.get('name') in self.department_mapping:
            department_info['department_id'] = d.get('id')
            department_info['name'] = d.get('name')
            res_data.append(dict(department_info))
        return res_data

    @property
    def departments(self):
        if self._departments is None:
            self._departments = self.get_departments()
        return self._departments

    @property
    def sorted_departments(self):
        if self._sorted_departments is None:
            self._sorted_departments = sorted(self.departments, key=lambda x: x['department_id'])
        return self._sorted_departments

    @property
    def departments_names(self):
        return [dept['name'] for dept in self.sorted_departments]

    @property
    def departments_ids(self):
        return [dept['department_id'] for dept in self.sorted_departments]


if __name__ == '__main__':
    depts = DepartmentSpider()
    print(depts.departments)
    print(depts.sorted_departments)
    print(depts.departments_names)
    print(depts.departments_ids)
