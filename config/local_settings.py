# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: local_settings.py
@time: 19-3-28 上午11:44 
"""

from pathlib import PurePosixPath, Path

from config.config import BASE_DIR

# 需要监控的目录
watch_dir = "templates"

# paraview的默认python的路径
PVPYTHON_PATH = "/data/ParaView-5.6.0-osmesa-MPI-Linux-64bit/bin/pvpython"

# 家目录 创建其他用户的家目录
HOMES_PATH = "/home"

# sudo密码
SUDO_PW = "09170725"

# Linux用户的默认密码
DEFAULT_USER_PW = "lmtuser666"

# 日志模块的配置
LOG_DIR = PurePosixPath.joinpath(BASE_DIR, "logs")

# 日志记录的方式
# 可选方式 logging和sentry
LOG_SYS = "logging"

# 如果日志目录不存在则创建
if not Path(LOG_DIR).exists():
    Path(LOG_DIR).mkdir()

# 一些模板文件的目录
TEMPLATES_DIR = PurePosixPath.joinpath(BASE_DIR, "templates")

# 脚本的目录
SCRIPTS_PATH = PurePosixPath.joinpath(TEMPLATES_DIR, "scripts")

# 创建用户的脚本
USER_ADD_SCRIPT = PurePosixPath.joinpath(TEMPLATES_DIR, "add-user.sh")

# 修改用户的脚本
PASSWD_USER_SCRIPT = PurePosixPath.joinpath(TEMPLATES_DIR, "passwd-user.sh")


