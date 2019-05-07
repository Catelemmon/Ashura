# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: Handlers.py
@time: 2019/4/30 下午1:52 
"""
from watchdog.events import RegexMatchingEventHandler

from dbs import DB
from parsers.SU2Parser import SU2Parser


class SU2ResultHandler(RegexMatchingEventHandler):

    def __init__(self, solve_job_id, rf_regs=(r'.*history\..+', ), **kwargs):
        # TODO: 待重构
        super(SU2ResultHandler, self).__init__(regexes=rf_regs, **kwargs)
        self.rf_regs = rf_regs
        self.offset = 0
        self.res_dict_tmp = None
        self.su2p = None
        self.keys = None
        self.solve_job_id = solve_job_id

    def on_modified(self, event):
        res_file = event.src_path
        if self.offset is 0:
            self.su2p = SU2Parser(res_file)
            self.res_dict_tmp, self.keys, self.offset = self.su2p.parse_first_line()
        results, self.offset = self.su2p.res_parse(self.res_dict_tmp, self.keys, self.offset)
        curent_step = int(results[-1]["Iteration"]) if len(results) is not 0 else 0
        DB.update_solve_current_step(self.solve_job_id, curent_step)
