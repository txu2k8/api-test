#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:main.py
@time:2021/09/26
@email:tao.xu2008@outlook.com
@description:pytest执行入口
"""

import os
import argparse
import pytest
from collections import defaultdict
import config
from config import logger, root_dir, get_global_value, xml_report_path, html_report_path
from pkgs.utils import remove_files, get_list_intersection
from loader.case_loader import CaseLoader


def test_parser():
    """test args parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=False, action="store", dest="test_env",
                        default="ali", choices=['ali', 'tx', 'qa', 'dev2'], help="测试环境选择")
    parser.add_argument("--data", action="store", dest="data_subdir_list", nargs='+',
                        default=[], help="测试用例*/data/下子目录")
    pytest_group = parser.add_argument_group("pytest框架参数")
    pytest_group.add_argument("-k", action="store", dest="match_expr",
                              default="test_", help="执行匹配表达式的用例")

    jenkins_group = parser.add_argument_group("jenkins相关参数")
    jenkins_group.add_argument("--job_name", action="store", dest="job_name",
                               default="", help="Jenkins JOB_NAME")

    return parser


def generate_py_testcase(args):
    """
    加载用例数据并生成pytest用例文件
    :param args:
    :return:
    """
    logger.info("删除testcase/test_*.py".center(70, '>'))
    remove_files(os.path.join(root_dir, "testcase"), "test_*.py")
    logger.info('测试开始'.center(70, '>'))
    from creator.pytest_creator import create_testcase
    data_subdir_list = args.data_subdir_list or [None]
    for data_subdir in data_subdir_list:
        for item in CaseLoader(sub_dir=data_subdir).load():
            for suite_name, suite_data in item.items():
                create_testcase(suite_name, suite_data)
    return True


def run_pytest(args):
    # pytest 运行测试
    argv = ['-v', '-s', '--ignore-unknown-dependency', f'--alluredir={xml_report_path}',
            '--clean-alluredir']  # , '-k getTableHead'

    argv.extend(['-k', args.match_expr])
    pytest.main(argv)
    report_summary = get_global_value("report_summary", defaultdict(int))
    case_member_mapping = get_global_value("case_member_mapping", defaultdict(str))
    logger.error(case_member_mapping)

    if args.job_name:
        from tools.report import ReportQWChat, QE_TEST_KEY, QE_CFCD_KEY
        rp_qw = ReportQWChat(args.job_name)

        try:
            # 发送测试群：内容较多，包括故障和py:member
            rp_qw.send_report_detail(report_summary, case_member_mapping, qw_robot_key_list=[QE_TEST_KEY])
        except Exception as e:
            logger.error(e)

        if len(get_list_intersection(['404', '5xx', '500500'], list(report_summary.keys()))) > 0:
            logger.info("发送严重错误报告...")
            try:
                # 发送测试群：仅严重错误内容
                rp_qw.send_report_critical(report_summary, qw_robot_key_list=[QE_CFCD_KEY])
            except Exception as e:
                logger.error(e)


def generate_allure():
    # 生成allure报告
    cmd = f'allure generate {xml_report_path} -o {html_report_path} --clean'
    try:
        os.popen(cmd)
        logger.info(f"  ******  开始生成测试报告  ******  \n {cmd}")
    except Exception as e:
        logger.error(u'生成allure报告失败，请检查环境配置', e)
    logger.info('测试完成,请查看报告!'.center(40, '<'))

    cmd = f'allure serve {xml_report_path}'
    os.popen(cmd)
    logger.info('打开测试报告')


if __name__ == '__main__':
    user_args = test_parser().parse_args()
    config.set_global_value("test_env", user_args.test_env)

    generate_py_testcase(user_args)
    run_pytest(user_args)
    # generate_allure()
