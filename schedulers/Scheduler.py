# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: Scheduler.py
@time: 19-3-28 下午1:50 
"""
from abc import abstractmethod


class Scheduler:

    @abstractmethod
    @classmethod
    def render_script(self, ):
        """
        渲染调度系统执行的脚本
        :return:
        """
        pass

    @classmethod
    def create_job(self):
        """
        创建job
        :return:
        """
        pass

    @abstractmethod
    @classmethod
    def data_parse(self):
        """
        参数处理
        :return:
        """
        pass

    @abstractmethod
    def send_job(self):
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
    def kill_job(self):
        """
        杀作业
        :return:
        """
