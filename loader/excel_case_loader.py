#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:excel_case_loader.py
@time:2021/09/26
@email:tao.xu2008@outlook.com
@description:xmind文件格式测试用例读取
"""


class ExcelCaseLoader(object):
    """
    读取 excel 内容，返回用例数据：
    字典列表（list[dict1,dict2]）
    """

    def __init__(self, file_path, book=""):
        self.file_path = file_path
        self.book = book

    def get_excel_data(self):
        return []


if __name__ == '__main__':
    pass
