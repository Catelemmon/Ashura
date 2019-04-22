# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: test_sql.py
@time: 2019/4/23 下午5:37 
"""

from model.models import DBsession, Job

session = DBsession()

job = Job(path="gucci",
          mesh_path="dior",
          user_name="Obama",
          solve_app=0,
          solve_config="dior",
          launch_script="launch"
          )

session.add(job)
session.commit()
session.close()