# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: __init__.py.py
@time: 19-3-27 下午5:21 
"""

try:
    from config.local_settings import *
except ImportError:
    from config.online_settings import *

from config.config import *

