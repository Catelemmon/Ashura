# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: Scheduler.py
@time: 19-3-28 下午1:50 
"""
from abc import abstractmethod


class Scheduler:

    # TODO 有待重构

    def __new__(cls, *args, **kwargs):
        return object.__new__(cls)

    @classmethod
    def create_job(self):
        """
        创建job
        :return:
        """
        pass

    @abstractmethod
    def data_parse(self):
        """
        参数处理
        :return:
        """
        pass

    def send_job(self, work_dir, **kwargs):
        """
        发送作业
        :return:
        """
        pass

    @abstractmethod
    def job_info(self):
        """
        获取job的信息
        :return:
        """
        pass

    @abstractmethod
    def kill_job(self, **kwargs):
        """
        杀作业
        :return:
        """
