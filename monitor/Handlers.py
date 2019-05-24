# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: Handlers.py
@time: 2019/4/30 下午1:52 
"""
import json
import re

from watchdog.events import RegexMatchingEventHandler

from dbs import DB
from parsers.SU2Parser import SU2Parser
from utils.log_utils import get_logger
from utils.offset_file import offset_file

convert_logger = get_logger("convert")


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
        if self.offset == 0:
            self.su2p = SU2Parser(res_file)
            self.res_dict_tmp, self.keys, self.offset = self.su2p.parse_first_line()
        results, self.offset = self.su2p.res_parse(self.res_dict_tmp, self.keys, self.offset)
        curent_step = int(results[-1]["Iteration"]) if len(results) is not 0 else 0
        if len(results) is not 0:
            DB.update_solve_current_step(self.solve_job_id, curent_step)  # 更新数据库中仿真当前步数
            for l_res in results:
                iter_step = l_res["Iteration"]
                DB.write_solve_chart(self.solve_job_id, iter_step, l_res)


class CFMeshResultHandler(RegexMatchingEventHandler):

    def __init__(self, mesh_id, rf_regs=(r'.*\d+\.out', ), **kwargs):
        super(CFMeshResultHandler, self).__init__(regexes=rf_regs, **kwargs)
        self.rf_regs = rf_regs
        self.offset = 0
        self.mesh_id = mesh_id
        self.current_step = 0

    def on_modified(self, event):
        res_file = event.src_path
        save_offset = 0
        line_matches = 0
        convert_logger.\
            info(f"读取带offset的文件 | file: {event.src_path} | offset: {self.offset} | mesh_id: {self.mesh_id}")
        for line, offset in offset_file(res_file, offset=self.offset):
            if re.search("Finished", line):
                print(line)
                line_matches += 1
            if re.search("End", line):
                DB.compete_mesh_step(mesh_id=self.mesh_id)
                return
            save_offset = offset
        self.current_step += line_matches
        self.offset = save_offset if save_offset > 0 else self.offset
        res = DB.query_mesh_status(self.mesh_id)
        if res == {}:
            convert_logger.critical(f"mesh_status中没有对应的mesh | {self.mesh_id}")
            return
        else:
            DB.update_mesh_status(self.mesh_id, current_step=self.current_step)
