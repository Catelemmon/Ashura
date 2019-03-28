# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: Mesh.py
@time: 19-3-28 上午11:06 
"""

from pathlib import Path


from config.config import CAE_APPLICATION_TYPE
from utils.log_utils import get_logger


logger = get_logger(logger_name="core")


class Mesh:

    def __new__(cls, workpath, project_id, is_upload=False, upload_mtype="OpenFoam", **kwargs):
        """
        创建一个Mesh
        :param workpath: meshs文件夹的路径
        :param project_id:  mesh对应的工程id
        :param is_upload: 是否为上传网格
        :param mesh_type 如果是
        :param kwargs: 可以额外添加和定制的参数, 可以集成到框架内
        :return:
        """
        if cls._args_check(project_id, upload_mtype):
            return cls._init(workpath, project_id, is_upload, upload_mtype, **kwargs)
        else:
            return None

    @classmethod
    def _args_check(cls, workpath, upload_mtype):
        try:
            if not Path(workpath).is_absolute():
                raise ValueError("mesh path must be a absolute path!")
            if upload_mtype not in CAE_APPLICATION_TYPE:
                raise ValueError("the type must be in CAE_APPLICATION_TYPE from config!")
            return True
        except ValueError:
            logger.exception()
            return False

    def _parse_args(self, kwargs):
        # TODO 暂时实现到这里
        for key, value in kwargs.items():
            setattr(self, key, value)
        pass

    @classmethod
    def _init(cls, workpath, project_id, is_upload=False, upload_mtype="OpenFoam", **kwargs):
        self = object.__new__(cls)
        self.path = workpath
        self.project_id = project_id
        self.is_upload = is_upload
        self.upload_mtype = upload_mtype
        self._parse_args(kwargs)
        return self

    def create_mesh(self, mdir_name):
        """

        :param mdir_name: 相对工作目录建立mesh的文件夹
        :return:
        """
        pass


    def write_config(self):
        pass

    def add_fdict(self):
        # TODO
        """
        添加mesh的配置文件
        :return:
        """
        pass

    def mesh_adapt(self):
        # TODO
        """
        实现mesh文件的转换和适配
        :return:
        """
        pass

    def do_mesh(self):
        # TODO
        """
        执行mesh操作
        :return:
        """
        pass