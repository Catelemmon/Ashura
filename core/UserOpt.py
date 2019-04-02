# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: UserOpt.py
@time: 2019/4/1 上午9:25 
"""
import os
from pathlib import Path

from config.local_settings import HOMES_PATH, SUDO_PW, DEFAULT_PW

out_log = "out_log.log"


class UserOpt:

    """
    sudo su - luoyuhang --session-command "sbatch /data/home/luoyuhang/pump_3.0/solver_cp.sh"
    执行solver操作

    """

    @classmethod
    def _mkdir_ashome(cls, user_name, homes_path=HOMES_PATH):
        """
        创建user的家目录
        :param user_name: 用户名
        :param homes_path: 创建家目录的路径
        :return:
        """
        uh = Path(homes_path).joinpath(user_name)
        os.system(f"echo {SUDO_PW} | sudo -S mkdir {str(uh)} >> {out_log}")
        return str(uh)

    @classmethod
    def add_user(cls, user_name, password=DEFAULT_PW, home_dir=None):
        """
        添加用户并初始化初始密码
        :param user_name: 用户名
        :param password: 密码
        :param home_dir: 家目录
        :return:
        """
        if home_dir is None:
            uh = cls._mkdir_ashome(user_name)
        os.system(f"echo {SUDO_PW} | sudo -S useradd {user_name} -d {uh} >> {out_log}")
        cls.passwd_user(user_name, password)

    @classmethod
    def add_group(cls):
        # TODO 实现添加组　目前不需要
        pass

    @classmethod
    def del_user(cls, user_name):
        """
        根据用户名删除用户
        :param user_name:
        :return:
        """
        os.system(f"echo {SUDO_PW} | sudo -S userdel -r {user_name} >> {out_log}")

    @classmethod
    def del_group(cls):
        # TODO 实现删除组　目前暂时不需要　
        pass

    @classmethod
    def passwd_user(cls, user_name, passwd):
        os.system(f'echo -e "{passwd}\n{passwd}" | echo {SUDO_PW} | sudo -S passwd {user_name} >> {out_log}')
