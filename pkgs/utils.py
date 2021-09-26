#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:utils.py
@time:2021/09/26
@email:tao.xu2008@outlook.com
@description:
"""
import os
import socket
import glob
import time
from progressbar import ProgressBar, Percentage, Bar, RotatingMarker, ETA
from config import logger


def get_local_ip():
    """
    Get the local ip address --linux/windows
    :return:(char) local_ip
    """
    return socket.gethostbyname(socket.gethostname())


def is_contains_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    if string is None:
        string = ""
    if not isinstance(string, str):
        string = str(string)
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def remove_files(base_dir, ext='test_*.py'):
    """
    使用通配符，获取文件并删除
    :return:
    """
    for f in glob.glob(os.path.join(base_dir, ext)):
        logger.info("remove {}".format(f))
        os.remove(f)


def sleep_progressbar(seconds):
    """
    Print a progress bar, total value: seconds
    :param seconds:
    :return:
    """

    # widgets = ['Progress: ', Percentage(), ' ', Bar(marker=RotatingMarker('-=>')), ' ', Timer(), ' | ', ETA()]
    widgets = ['Progress: ', Percentage(), ' ', Bar(marker=RotatingMarker('-=>')), ' ', ETA()]
    pbar = ProgressBar(widgets=widgets, maxval=seconds).start()
    for i in range(seconds):
        pbar.update(1 * i + 1)
        time.sleep(1)
    pbar.finish()


def get_list_intersection(list_a, list_b):
    """
    Get the intersection between list_a and list_b
    :param list_a:
    :param list_b:
    :return:(list) list_intersection
    """

    assert isinstance(list_a, list)
    assert isinstance(list_b, list)
    return list((set(list_a).union(set(list_b))) ^ (set(list_a) ^ set(list_b)))


if __name__ == '__main__':
    # print(get_local_ip())
    # sleep_progressbar(3)
    print(get_list_intersection([1, 2], [2, 3]))
