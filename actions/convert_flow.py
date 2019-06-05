# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: convert_flow.py
@time: 2019/4/25 上午10:24 
"""
from importlib import import_module
from multiprocessing import Process, ProcessError
from pathlib import Path

from constants.maps import CONVERT_CLASSES
from converter.snipthumb import SnipThumb
from dbs import DB
from utils.log_utils import get_logger

core_logger = get_logger("core")


class ConvertControler(object):

    def __init__(self, ori_file, des_file, vf_file, convert_type, thumb_path=None):
        self.ori_file = ori_file
        self.des_file = des_file
        self.vf_file = vf_file
        self.thumb_path = thumb_path
        self._path_adapt()
        self.convert_type = convert_type
        mdl_name, cls_name = CONVERT_CLASSES[convert_type]
        convert_class = getattr(import_module(mdl_name), cls_name)
        try:
            self.converter = convert_class(self.ori_file, self.des_file, self.vf_file)
        except ValueError:
            core_logger.exception("创建转换类失败")
            core_logger.info("ConvertControler 类创建成功")
            raise

    def _path_adapt(self):
        if self.des_file is not None:
            if not Path(self.des_file).parent.exists():
                Path(self.des_file).parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if not Path(self.vf_file).parent.exists():
            Path(self.vf_file).parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        if self.thumb_path is not None:
            if not Path(self.thumb_path).parent.exists():
                Path(self.thumb_path).parent.mkdir(mode=0o700, parents=True, exist_ok=True)

    def start_actions(self):
        core_logger.info(f"convert信息写入数据库! | {CONVERT_CLASSES[self.convert_type]}"
                         f" |{self.ori_file} | {self.des_file} | {self.vf_file }")
        convert_id = DB.write_convert(self.ori_file, self.des_file, self.vf_file, self.convert_type,
                                      thumb_nail=self.thumb_path)
        if convert_id == -1:
            return -1, "数据库写入失败"
        core_logger.info(f"创建进程进行转换 | convert_id: {convert_id}")
        try:
            convert_pro = Process(target=self._asyc_convert, args=(convert_id,))
            convert_pro.start()
            core_logger.info(f"异步转换进程开始 | pid: {convert_pro.pid} | convert_id: {convert_id}")
            return convert_id, "success!"
        except ProcessError:
            DB.update_convert(convert_id, 1, {})
            core_logger.exception("开启转换进程失败")
            return 1, "开启转换进程失败"

    def _asyc_convert(self, convert_id):
        core_logger.info(f"异步进行转换 | {convert_id}")
        try:
            status, conver_info, msg = self.converter.start()
        except TypeError:
            DB.update_convert(convert_id, 2, {})
            core_logger.exception(f"转换失败 | {convert_id}")
            return
        except ValueError:
            DB.update_convert(convert_id, 2, {})
            core_logger.exception(f"转换失败 | {convert_id}")
            return
        DB.update_convert(convert_id, status, conver_info)
        core_logger.info(f"异步转换结束 | {convert_id} | {msg}")
        if self.thumb_path is not None:
            if Path(self.vf_file).exists():
                res = SnipThumb(vf_file=self.vf_file, img_file=self.thumb_path).start()
                if res == 1:
                    core_logger.info(f"图片转换失败 | 图片转换脚本出错")
            core_logger.info(f"转换图片失败 | 没有对应的vtm文件 | {self.vf_file}")
        return
