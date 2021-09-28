#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:case_loader.py
@time:2021/09/28
@email:tao.xu2008@outlook.com
@description:
"""
import os
from config import logger, case_data_path
from loader.xmind_case_loader import XmindCaseLoader
from loader.excel_case_loader import ExcelCaseLoader

supported_f_type = (
    ".xmind",
    ".xlsx",
    ".xls",
    ".csv",
)


class CaseLoader(object):
    """递归遍历用例设计文件目录，读取case数据"""
    def __init__(self, case_path: str = case_data_path, sub_dir=""):
        self.case_path = case_path
        if sub_dir:
            self.case_path = os.path.join(case_path, sub_dir)

    def get_all_case_files(self, f_types=supported_f_type) -> list:
        """
        返回cases 路径下全部case文件列表
        :return:
        """
        files_path = []
        if not os.path.isdir(self.case_path):
            logger.warning("{}路径不存在！！！".format(self.case_path))
            return files_path
        for file_name in os.listdir(self.case_path):
            for f_type in f_types:
                if file_name.lower().endswith(f_type):
                    f_path = os.path.join(self.case_path, file_name)
                    logger.info(f_path)
                    files_path.append(f_path)
        return files_path

    def get_all_case_files_recursion(self, f_types=supported_f_type) -> list:
        """
        返回cases 路径下全部case文件列表
        :return:
        """
        files_path = []
        if not os.path.isdir(self.case_path):
            logger.warning("{}: 路径不存在！！！".format(self.case_path))
            return files_path
        for root, dirs, files in os.walk(self.case_path):
            for file_name in files:
                for f_type in f_types:
                    if file_name.lower().endswith(f_type):
                        f_path = os.path.join(root, file_name)
                        logger.info(f_path)
                        files_path.append(f_path)
        return files_path

    @staticmethod
    def load_file_case_data(file_path: str) -> list:
        """
        读取case配置文件中的case信息 --xmind
        :param file_path: case配置文件路径
        :return:xmind中的case信息
        """
        if file_path.endswith(".xmind"):
            return XmindCaseLoader(file_path).get_xmind_data()
        elif file_path.endswith(".xlsx") or file_path.endswith(".xls") or file_path.endswith(".csv"):
            return ExcelCaseLoader(file_path).get_excel_data()

    def load(self) -> list:
        """
        遍历测试用例配置文件，并为每个文件构造完整的测试用例信息集合
        :return:
        """
        for file in self.get_all_case_files_recursion():
            d, f = os.path.split(file)
            pd, pf = os.path.split(d)
            sf = f.split('.')[0].replace("-", "_")
            if case_data_path == pd:
                module_name = "{0}_{1}".format(pf, sf)
            else:
                module_name = sf
            module_data = {module_name: self.load_file_case_data(file)}
            yield module_data


if __name__ == '__main__':
    pass
