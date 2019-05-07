# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: configs.py
@time: 19-3-28 上午11:44 
"""
import os
from pathlib import Path

LOG_SYS_ENUM = ("logging", "sentry")

BASE_DIR = Path(os.path.abspath(__file__)).parent.parent

LAUNCH_BEHOLDER = True

PLOYMESH_FILES = (
    "boundary",
    "faces",
    "neighbour",
    "owner",
    "points"
)
