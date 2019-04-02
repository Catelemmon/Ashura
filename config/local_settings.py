# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: local_settings.py
@time: 19-3-28 上午11:44 
"""
from pathlib import PurePosixPath, Path

from config.config import BASE_DIR


LOG_SYS = "logging"

watch_dir = "templates"

PVPYTHON_PATH = "/data/ParaView-5.6.0-osmesa-MPI-Linux-64bit/bin/pvpython"

LOG_DIR = PurePosixPath.joinpath(BASE_DIR, "logs")

HOMES_PATH = "/home"

SUDO_PW = "09170725"

DEFAULT_PW = "123456"

if not Path(LOG_DIR).exists():
    Path(LOG_DIR).mkdir()
