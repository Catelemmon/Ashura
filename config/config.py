# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: config.py
@time: 19-3-28 上午11:44 
"""


from pathlib import Path

CAE_APPLICATION_TYPE = (
    "OpenFoam",
    "SU2",
    "MOOSE"
)

LOG_SYS_ENUM = ("logging", "sentry")

BASE_DIR = Path.cwd().parent

LAUNCH_BEHOLDER = True

PLOYMESH_FILES = (
    "boundary",
    "faces",
    "neighbour",
    "owner",
    "points"
)

# TODO: pkguil
DEFAULT_SERVER = "HttpServer."