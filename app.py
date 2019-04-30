# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: app.py
@time: 19-3-28 上午11:33 
"""


import os
import sys
from pathlib import Path

from watchdog.events import FileSystemEventHandler

from monitor import fm
from monitor.Handlers import SU2ResultHandler
from servers import AshuraServer


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.abspath(__file__))
    packages = [d for d in Path(base_dir).iterdir() if d.is_dir() and d is not "templates"]
    for p in packages:
        pp = str(Path(base_dir).joinpath(p))
        if pp not in sys.path:
            sys.path.append(pp)
    sys.path = set(sys.path)
    server = AshuraServer(host="0.0.0.0", port=5000, is_debug=True)
    server.run_server()

