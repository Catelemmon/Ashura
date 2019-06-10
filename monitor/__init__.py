# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: __init__.py.py
@time: 19-3-28 上午11:33 
"""

from monitor.WorkDirMonitor import WorkDirMonitor
from monitor.Handlers import *

global DIR_MONITOR

DIR_MONITOR = WorkDirMonitor()
