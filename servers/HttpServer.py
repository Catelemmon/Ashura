# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: HttpServer.py
@time: 2019/4/19 下午2:55 
"""
import copy
from typing import Dict

from actions import solve_flow
import json
from flask import Flask
from flask_restplus import Resource, Api, Namespace

from dbs import DB
from servers import AshuraServer

ns = Namespace("/", description="中间件接口文档!")

solve_parser = ns.parser()
solve_parser.add_argument("work-path", type=str, help="workspace of job", location='form')
solve_parser.add_argument("mesh-file-path", type=str, help="the path of mesh", location='form')
solve_parser.add_argument("username", type=str, help="who sends the solve", location='form')
solve_parser.add_argument("solve-app", type=int, help="the id of solve app", location='form')
solve_parser.add_argument("solve-config", type=str, help="the config of solve-config", location='form')
solve_parser.add_argument("accesstoken", type=str, help="the token to attach middleware", location='form')

results_parser = ns.parser()
results_parser.add_argument("jobId", type=int, help="the id of job", location='form')
results_parser.add_argument("accesstoken", type=str, help="the token to attach middleware", location='form')

RESPONSE_TEMPLATE = {
    "code": None,
    "msg": None,
    "result": None
}


def create_resp(code, msg, result):
    resp = copy.deepcopy(RESPONSE_TEMPLATE)
    resp["code"] = code
    resp["msg"] = msg
    resp["result"] = result
    return resp


@ns.route("/do-solve")
class DoSolve(Resource):
    """
    :description 提交仿真作业
    """
    @ns.doc(parser=solve_parser)
    def post(self):

        # 校验参数
        solve_args = ["work-path", "mesh-file-path", "username", "solve-app", "solve-config", "accesstoken"]
        kwargs = dict(solve_parser.parse_args())
        for args in solve_args:
            if args not in kwargs:
                code, msg, results = 1, f"缺少参数{args}!", None
                return create_resp(code, msg, results)

        # 执行solve

        job_id, msg = solve_flow.start_solve_actions(**kwargs)
        return create_resp(0, msg, {"jobId": job_id})


@ns.route("/solve-status")
class JobResults(Resource):
    """
    :description 获取仿真的结果
    """
    @ns.doc(parser=results_parser)
    def post(self):
        arg = dict(results_parser.parse_args())
        job_id = arg.get("jobId", None)
        if job_id is None:
            return create_resp(1, msg="没有传入job id", result="{}")

        result = DB.query_solve_status(job_id=job_id)
        return create_resp(1, msg="", result=result)


class JobChart(Resource):
    def post(self):
        pass


class CadConvert(Resource):
    pass


class HttpServer(AshuraServer):

    def _init(self):
        self._app = Flask("AshuraServer")
        self._api = Api(app=self._app, title="中间件接口文档", version="v0.1", description="无描述")
        self._api.add_namespace(ns)
        pass

    @classmethod
    def _from_parts(cls, kwargs, init=True):
        self = object.__new__(cls)
        pars: Dict = cls._parse(kwargs)
        self.options = kwargs
        para_l = ["host", "port", "is_debug"]
        self.host = pars.get("host", "0.0.0.0")
        self.port = pars.get("port", 5000)
        self.is_debug = pars.get("is_debug", True)
        for para in para_l:
            self.options.pop(para)
        if init:
            self._init()
        return self

    def server(self, options):
        self._app.run(host=self.host, port=self.port, debug=self.is_debug, **options)

    def __getattr__(self, item):

        if item not in ["_from_parts", "_parse", "_init", "server", "run_server"]:
            try:
                return getattr(self._app, item)
            except AttributeError:
                return getattr(self._api, item)
