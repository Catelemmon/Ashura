# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: convert_flow.py
@time: 2019/4/25 上午10:24 
"""
from importlib import import_module
from multiprocessing import Process, ProcessError

from constants.maps import CONVERT_CLASSES
from dbs import DB
from utils.log_utils import get_logger

core_logger = get_logger("core")


class ConvertControler(object):

    def __init__(self, ori_file, des_file, vf_file, convert_type, thumb_path=None):
        self.ori_file = ori_file
        self.des_file = des_file
        self.vf_file = vf_file
        self.thumb_path = thumb_path
        self.convert_type = convert_type
        mdl_name, cls_name = CONVERT_CLASSES[convert_type]
        convert_class = getattr(import_module(mdl_name), cls_name)
        self.converter = convert_class(self.ori_file, self.des_file, self.vf_file)

    def start_actions(self):
        core_logger.info(f"convert信息写入数据库! | CONVERT_CLASSES[convert_type]"
                         f" |{self.ori_file} | {self.des_file} | {self.vf_file }")
        convert_id = DB.write_convert(self.ori_file, self.des_file, self.vf_file, self.convert_type)
        if convert_id == -1:
            return -1, "数据库写入失败"
        core_logger.info(f"创建进程进行转换")
        try:
            convert_pro = Process(target=self.asyc_convert, args=(convert_id, ))
            convert_pro.start()
            return convert_id, "success!"
        except ProcessError:
            DB.update_convert(convert_id, 1, {})
            core_logger.exception("开启转换进程失败")
            return -1, "开启转换进程失败"

    def asyc_convert(self, convert_id):
        core_logger.info(f"异步进行转换 | {convert_id}")
        status, conver_info, msg = self.converter.start()
        core_logger.info("异步转换结束 | convert_id")
        DB.update_convert(convert_id, status, conver_info)
        if self.thumb_path is not None:
            pass  # 执行转换缩略图
