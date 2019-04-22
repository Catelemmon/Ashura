# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: test.py
@time: 2019/4/22 下午5:23 
"""

from service.AshuraServer import AshuraServer

server = AshuraServer(host="0.0.0.0", port=5000, is_debug=True)


server.run_server()