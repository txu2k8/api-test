#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:pytest_creator.py
@time:2021/09/28
@email:tao.xu2008@outlook.com
@description:创建符合pytest规范的py文件，包含测试用例
"""

import re
import builtins
import os
import types
import pytest
import allure
from config import logger, testcase_path
from core.pkgs.utils import is_contains_chinese, sleep_progressbar
from operator import methodcaller


def to_safe_name(s):
    return str(re.sub("[^a-zA-Z0-9_]+", "_", s))


# 自动构造用例文件和内容
def create_testcase(module_name: str, module_data: list):
    """
    为模块创建py文件，并更加模块测试数据生成用例代码
    :param module_name: 模块名
    :param module_data: suite测试数据列表
    :return:
    """
    # 文件头内容模板
    import_content = '''#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""本文件是根据测试用例自动生成，pytest调用执行"""

import pytest
import allure
from core.creator.pre_request import PreRequest
from core.creator.py_creator import CaseMetaClass

'''

    # 类模板
    class_content = '''
@allure.feature('{suite_desc}')
class Test{suite_name}(PreRequest, metaclass=CaseMetaClass):
    test_py = "{test_py}"
    api_data_list = {api_data_list}

    def teardown_class(self):
        print("\\n")
        self.api.print_step_table(ps='{suite_name}')

'''

    test_py = 'test_{}.py'.format(to_safe_name(module_name))
    test_case_file = os.path.join(testcase_path, test_py)
    with open(test_case_file, 'w', encoding='utf8') as f:
        f.write(import_content)  # 写入文件头部导入信息
        for idx, suite_data in enumerate(module_data):
            suite_desc = suite_data['desc'].strip()
            suite_name = to_safe_name(suite_data['suite'])
            api_data_list = suite_data['api_list']
            f.write(class_content.format(
                suite_desc=suite_desc, suite_name=suite_name,  # +str(idx+1).zfill(4),
                test_py=test_py,
                api_data_list=api_data_list)
            )
    return True


func_template = '''
def {func_name}(self, case_data):
    # 不满足条件，跳过用例
    api_skipif = self.api.replace_variables(case_data['skipif'])
    if api_skipif and eval(api_skipif):
        logger.warning("不满足条件%s: %s" % (case_data['skipif'], api_skipif))
        pytest.skip("不满足条件%s" % api_skipif)

    # self.{func_name}.__func__.__doc__ = case_data["desc"]
    class_name = self.__class__.__name__
    func_name = self.{func_name}.__name__
    logger.info(self.test_py+"::"+class_name+"::"+func_name)
    # logger.info(self.{func_name}.__name__)
    # logger.info(self.{func_name}.__doc__)
    logger.info(case_data["desc"])
    story_name = case_data["api_desc"] or case_data["desc"]
    if story_name:
        allure.dynamic.story(story_name)
    allure.dynamic.description(case_data["desc"])
    allure.dynamic.severity(case_data["priority"])
    
    # 参数解析
    req_data = self.request_data_parse(case_data)
    res_expect = self.api.content_to_dict(case_data["res_expect"])
    res_set_cache = self.api.content_to_dict(case_data["res_set_cache"])
    
    self.api.step_table.append([case_data["desc"], req_data["method"], case_data["path"], "call"])
    # self.api.print_step_table()
    # logger.info(req_data)
    if case_data["sleep"] > 0:
        logger.info("API请求前Sleep %ds ..." % case_data["sleep"])
        sleep_progressbar(case_data["sleep"])

    if not req_data.get("method"):  # API方法配置为 空，则只设置全局变量
        for k, v in res_set_cache.items():
            self.api.set_cache_kv(k, v)
        return True
    elif req_data.get("method").upper() == "SETUP":  # API方法配置为 SETUP
        c, f = case_data.get("path").split("().")
        # 通过反射进行取类
        class_obj = getattr(setup, c)
        f_obj = getattr(class_obj, f)
        logger.info("%s::%s" %(class_obj.__name__, f_obj.__name__))
        logger.info(f_obj.__doc__)
        res = methodcaller(f, **req_data["json"])(class_obj())
        assert res
        return True
    elif req_data.get("method").upper() == "CALLBACK":  # API方法配置为 CALLBACK
        c, f = case_data.get("path").split("().")
        # 通过反射进行取类
        class_obj = getattr(callback, c)
        f_obj = getattr(class_obj, f)
        logger.info("%s::%s" %(class_obj.__name__, f_obj.__name__))
        logger.info(f_obj.__doc__)
        res = methodcaller(f, **req_data["json"])(class_obj())
    else:
        res = self.api.request(**req_data)
    # logger.info(res.text)
    validate_kv = self.api.format_res_expect(res_expect)
    assert self.api.validate(res, validate_kv), "Faild: response validate"
    for k, expr in res_set_cache.items():
        assert self.api.set_cache(res.json(), k, expr)

    allure.dynamic.title(case_data["api_name"]+"-"+case_data["desc"])
'''


class CaseMetaClass(type):
    """根据接口生成定制测试用例代码"""

    def __new__(cls, name, bases, attrs):
        api_data_list = attrs.pop('api_data_list')
        for idx, api_data in enumerate(api_data_list):
            api_name = api_data['api_name']
            api_desc = api_data['api_desc']
            case_list = api_data['test_case_list']
            func_name = 'test_{0}_{1}'.format(str(idx + 1).zfill(3), to_safe_name(api_name.replace("#", "")))
            # 动态创建API用例
            function = create_function(func_template.format(func_name=func_name),
                                       namespace={
                                           'pytest': pytest,
                                           'allure': allure,
                                           'logger': logger,
                                           'is_contains_chinese': is_contains_chinese,
                                           'sleep_progressbar': sleep_progressbar,
                                           'methodcaller': methodcaller
                                       })

            # 测试用例参数化
            ids = [str(c).zfill(3) for c in range(1, len(case_list) + 1)]
            attrs[func_name] = pytest.mark.parametrize('case_data', case_list, ids=ids)(function)
            # 添加被依赖和依赖标志
            dp_name, depends = None, []
            for dp in api_data['depends']:
                if dp == api_name:
                    dp_name = api_name
                    continue
                else:
                    depends.append(dp)
            if dp_name or len(depends) > 0:
                # logger.info("dependency: {} : name={},depends={}".format(func_name, dp_name, depends))
                attrs[func_name] = pytest.mark.dependency(name=dp_name, depends=depends, scope='class')(
                    attrs[func_name])
            # skip以#开头的测试用例
            if api_name.startswith("#") or api_desc.startswith("#"):
                attrs[func_name] = pytest.mark.skip(reason='测试用例被注释#')(attrs[func_name])
        return super().__new__(cls, name, bases, attrs)


def create_function(function_express, namespace=None):
    """动态生成函数对象"""
    if namespace is not None:
        builtins.__dict__.update(namespace)
    module_code = compile(function_express, '', 'exec')  # 根据模板生成可执行的代码
    function_code = [x for x in module_code.co_consts if isinstance(x, types.CodeType)][0]
    return types.FunctionType(function_code, builtins.__dict__)


if __name__ == '__main__':
    from config import root_dir
    from core.loader.xmind_case_loader import XmindCaseLoader

    tc_file = os.path.join(root_dir, 'doc', '用例设计规范.xmind')
    m_name = os.path.split(tc_file)[-1].split('.')[0]
    m_data = XmindCaseLoader(tc_file, canvas="用例设计-示例").get_xmind_data()
    create_testcase(m_name, m_data)
