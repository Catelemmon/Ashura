# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: log_utils.py
@time: 19-3-18 上午10:23 
"""

from pathlib import PurePosixPath
from functools import wraps
from configs.local_settings import LOG_SYS
from configs.local_settings import LOG_DIR

import logging
from logging import DEBUG


def sentry_logger():
    # TODO: 实现sentry的日志记录
    pass


def default_logger(name=None, logger=None, level=None, logfile=None, message=None):
    """
    使用python默认的日志记录的装饰器

    :param logger: 日志记录器
    :param level: 日志的等级
    :param name: 日志名称
    :param logfile: 日志文件
    :param message: 日志消息
    :return: 返回一个装饰器
    """
    if logfile:
        if not PurePosixPath.is_absolute(logfile):
            raise OSError(f"{logfile} is not a absolute path!")

    def decorater(func):
        """构造内部的logger"""
        if logger:
            inner_logger = logger
        else:
            logname = name if name else "common"
            inner_logger = logging.getLogger(logname)
            inner_logger.setLevel("INFO")
            formatter = logging.Formatter('%(asctime)s :%(levelname)s  %(message)s')
            fh = logging.FileHandler(logfile if logfile else PurePosixPath.joinpath(LOG_DIR,  f"{logname}.log"))
            fh.setFormatter(formatter)
            streamh = logging.StreamHandler()
            streamh.setFormatter(formatter)
            logmsg = message if message else func.__name__
            loglevel = level if level else logging.INFO

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                inner_logger.addHandler(fh)
                inner_logger.addHandler(streamh)
                inner_logger.log(loglevel, f"executing function {logmsg}")
                inner_logger.handlers.clear()
                return func(*args, *kwargs)
            except ValueError:
                raise
            except Exception:
                inner_logger.addHandler(fh)
                inner_logger.addHandler(streamh)
                inner_logger.info("#####################################################")
                inner_logger.exception(f"something wrong in function {logmsg}")
                inner_logger.info("#####################################################")
                inner_logger.handlers.clear()
        return wrapper
    return decorater


def get_logger(logger_name="common", level=DEBUG, logfile=None):
    logfile = logfile if logfile else PurePosixPath.joinpath(LOG_DIR,  f"{logger_name}.log")
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s :%(levelname)s  %(message)s')
    fh = logging.FileHandler(logfile if logfile else PurePosixPath.joinpath(LOG_DIR, f"{logger_name}.log"))
    fh.setFormatter(formatter)
    streamh = logging.StreamHandler()
    streamh.setFormatter(formatter)
    return logger


if LOG_SYS == "logging":
    logger_dec = default_logger
elif LOG_SYS == "sentry":
    logger_dec = sentry_logger
