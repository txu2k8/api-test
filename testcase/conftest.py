#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:conftest.py
@time:2021/09/26
@email:tao.xu2008@outlook.com
@description:
"""
import re
import pytest
from collections import defaultdict
from config import cf, logger, set_global_value, get_global_value
from spiders.get_environment_data import GetEnvData
from spiders.auth import Auth


@pytest.fixture(scope='session', autouse=True)
def a_get_session():  # 方法以a开头确保先执行get_session
    """通过计费获取超管session id"""
    session_id = Auth(session_id=None).Authorization
    logger.info(session_id)
    set_global_value('session_id', session_id)
    # print(session_id)
    return session_id


@pytest.fixture(scope='session', autouse=True)
def get_bill_session():
    """获取计费登录token"""
    ses_id = Auth(session_id=None).get_bill_session()
    logger.info(ses_id)
    set_global_value('sesId', ses_id)
    return ses_id


@pytest.fixture(scope='session', autouse=True)
def get_env_data():
    try:
        env_data = GetEnvData(session_id=get_global_value("session_id"))
    except Exception as e:
        logger.error(e)
        return
    logger.info("爬取并设置测试环境信息到全局变量...")
    for k in env_data.get_props():
        try:
            v = env_data.__getattribute__(k)
            # logger.debug("测试环境信息：{}:{}".format(k, v))
            set_global_value(k, v)
        except Exception as e:
            logger.error(e)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    标记测试结果到 BaseAPI().step_table
    :param item:
    :param call:
    :return:
    """
    # 读取保存到全局的测试结果
    report_summary = get_global_value("report_summary", defaultdict(int))
    case_member_mapping = get_global_value("case_member_mapping", defaultdict(str))
    case_py = str(item.nodeid).split('::')[0].split('/')[1]
    case_members = []
    for p, m in cf.get_kvs('MEMBERS').items():
        if len(re.findall(p, case_py)) > 0:
            if m not in case_members:
                case_members.append(m)
    case_members_str = ','.join(case_members)
    out = yield
    report = out.get_result()
    # print("执行结果：{}".format(report))
    # logger.error("nodeid：{}".format(item.nodeid))

    if report.when == "setup":
        if report.outcome == "skipped":  # skipped
            report_summary[report.outcome] += 1
            item.cls.api.step_table.append(["", "", item.function.__name__, "skipped"])
        elif report.outcome == "failed":
            # 当setup执行失败了，setup的执行结果的failed,后面的call用例和teardown都不会执行了，最终执行结果是error
            report_summary["error"] += 1
            case_member_mapping[case_py] = case_members_str

    if report.when == "call":  # 只获取call用例时的信息
        if len(item.cls.api.step_table) > 0:
            item.cls.api.step_table[-1][-1] = report.outcome
        report_summary[report.outcome] += 1
        if report.outcome in ["failed", "error"]:
            case_member_mapping[case_py] = case_members_str

    if report.when == "teardown":
        if report.outcome == "failed":
            # teardown执行失败了，teardown的执行结果的failed,setup和case都是pass的，最终执行结果是1 passed,1 error
            report_summary[report.outcome] += 1
            case_member_mapping[case_py] = case_members_str

    # 保存测试结果到全局变量
    set_global_value("report_summary", report_summary)
    set_global_value("case_member_mapping", case_member_mapping)


if __name__ == '__main__':
    pass
