# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: __init__.py.py
@time: 19-3-27 下午5:21 
"""

try:
    from configs.local_settings import *
except ImportError:
    from configs.online_settings import *

from configs.config import *

