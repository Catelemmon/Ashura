# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: MeshOpt.py
@time: 19-3-28 上午11:06 
"""
import codecs
from pathlib import Path


from configs.config import CAE_APPLICATION_TYPE
from utils.log_utils import get_logger


logger = get_logger(logger_name="core")


class MeshOpt:

    def __new__(cls, workpath, is_upload=False, upload_mtype="OpenFoam", **kwargs):
        """
        创建一个Mesh
        :param workpath: meshs文件夹的路径
        :param is_upload: 是否为上传网格
        :param mesh_type 如果是
        :param kwargs: 可以额外添加和定制的参数, 可以集成到框架内
        :return:
        """
        if cls._args_check(workpath, upload_mtype):
            return cls._init(workpath, is_upload, upload_mtype, **kwargs)
        else:
            return None

    @classmethod
    def _args_check(cls, workpath, upload_mtype):
        try:
            if not Path(workpath).is_absolute():
                raise ValueError("mesh path must be a absolute path!")
            if upload_mtype not in CAE_APPLICATION_TYPE:
                raise ValueError("the type must be in CAE_APPLICATION_TYPE from configs!")
            return True
        except ValueError:
            logger.exception()
            return False

    def _parse_args(self, kwargs):
        # TODO 暂时实现到这里
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def del_mesh(cls, workpath):
        pass

    @classmethod
    def _init(cls, workpath, is_upload=False, upload_mtype="OpenFoam", **kwargs):
        self = object.__new__(cls)
        self.workpath = workpath
        self.is_upload = is_upload
        self.upload_mtype = upload_mtype
        self._parse_args(kwargs)
        return self

    def create_mdir(self, mdir_name):
        """
        :param mdir_name: 相对工作目录建立mesh的文件夹
        :return:
        """
        self.mdir_path = Path(self.workpath).joinpath(mdir_name)
        Path(self.mdir_path).mkdir()

    def create_sysd(self):
        """
        创建system这个文件夹
        :return:
        """
        self.sys_dir = Path(self.mdir_path).joinpath("system")
        Path(self.sys_dir).mkdir()

    def write_json_mconfig(self, jname, mdata):

        """
        写入前端传入的json版本的mesh配置文件
        :param mdata: 需要写入json的数据
        :param jname: json的文件名称
        :return:
        """
        j_mconfig = Path(self.mdir_path).joinpath(jname)
        with codecs.open(j_mconfig, encoding="utf-8", mode="w") as j_mconfig_obj:
            j_mconfig_obj.write(mdata)

    def write_mconfig(self, *mdicts,):
        # TODO 写mesh的配置的文件
        """

        :return:
        """
        pass

    def create_mdicts(self):
        # TODO
        """
        创建mesh的配置文件
        :return:
        """
        pass

    def copy_mdircts(self, ori_dir):
        """
        拷贝mesh的dicts到当前的目录下
        :param ori_dir:
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

    def get_space(self):
        # TODO
        """
        占用多大的空间最后这个mesh
        :return:
        """

    def to_vtm(self):
        # TODO:
        """
        将网格后的文件转换为用户可视的vtm
        :return:
        """