#!/usr/bin/python
# -*- coding:utf-8 _*- 
"""
@author:TXU
@file:xlog.py
@time:2021/09/26
@email:tao.xu2008@outlook.com
@description: 日志配置类
"""

import os
import sys
import time
from loguru import logger
from pathlib import Path
logger.remove()


class LogWriter:
    """日志类"""

    def __init__(self, log_path=None, file_level="DEBUG", console_level="INFO"):
        timer = time.time()
        log_path = log_path or os.path.abspath(os.path.join(os.path.dirname(__file__), "../../log"))
        self.log_name = Path(log_path, f'message_{timer}.log')
        logger.add(self.log_name, rotation='100 MB', retention='7 days', enqueue=True, encoding="utf-8", level=file_level)
        logger.add(sys.stdout, level=console_level)

    def info(self, msg):
        """打印 info 级别的日志"""
        logger.info(msg)

    def debug(self, msg):
        """打印 debug 级别的日志"""
        logger.debug(msg)

    def warning(self, msg):
        """打印 warning 级别的日志"""
        logger.warning(msg)

    def error(self, msg):
        """打印 error 级别的日志"""
        logger.error(msg)


if __name__ == '__main__':
    LogWriter().info("abc")
