# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: compute_domain_flow.py
@time: 2019/5/30 下午3:15 
"""


from multiprocessing import ProcessError, Process

from dbs import DB
from utils.log_utils import get_logger

core_logger = get_logger("core")


class ComputeDomainControler(object):

    def __init__(self, cad_file_path, param_field, visual_file_path):
        self.cad_file_path = cad_file_path
        self.param_field = param_field
        self.visual_file_path = visual_file_path

    def start_actions(self):
        core_logger.info(f"构建计算域数据库信息 | cad_file_path: {self.cad_file_path}"
                         f" | visual_file_path: {self.visual_file_path}")
        domain_id = DB.write_compute_domain(self.cad_file_path, self.visual_file_path)
        core_logger.info(f"异步开始构建计算域 | domain_id: {domain_id}")
        try:
            dom_crt_process = Process(target=self.asyc_domain_create, args=(domain_id, ))
            dom_crt_process.start()
            core_logger.exception(f"异步进行计算域的生成　｜ pid: {dom_crt_process.pid} | domain_id: {domain_id}")
            return domain_id, "success"
        except ProcessError:
            core_logger.exception(f"开启计算域构建进程失败 | domain_id: {domain_id}")
            return -1, f"开启计算域构建进程失败 | domain_id: {domain_id}"

    def asyc_domain_create(self, domain_id):
        pass
