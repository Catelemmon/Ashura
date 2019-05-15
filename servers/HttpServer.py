# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: HttpServer.py
@time: 2019/4/19 下午2:55 
"""
import copy
from typing import Dict
from gevent.pywsgi import WSGIServer
from actions import solve_flow
from flask import Flask
from flask_restplus import Resource, Api, Namespace

from actions.convert_flow import ConvertControler
from actions.solve_flow import stop_solve
from dbs import DB, SlurmDB
from servers import AshuraServer

ns = Namespace("/", description="中间件接口文档!")

solve_parser = ns.parser()
solve_parser.add_argument("work-path", type=str, help="workspace of job", location='form')
solve_parser.add_argument("mesh-file-name", type=str, help="the path of mesh", location='form')
solve_parser.add_argument("username", type=str, help="who sends the solve", location='form')
solve_parser.add_argument("job-name", type=str, help="job name", location='form')
solve_parser.add_argument("solve-app", type=int, help="the id of solve app", location='form')
solve_parser.add_argument("solve-config", type=str, help="the config of solve-config", location='form')
solve_parser.add_argument("accesstoken", type=str, help="the token to attach middleware", location='form')

results_parser = ns.parser()
results_parser.add_argument("jobId", type=int, help="the id of job", location='form')
results_parser.add_argument("accesstoken", type=str, help="the token to attach middleware", location='form')

stop_solve_parser = ns.parser()
stop_solve_parser.add_argument("jobId", type=int, help="the id of job", location='form')
stop_solve_parser.add_argument("accesstoken", type=str, help="the token to attach middleware", location='form')

solve_chart = ns.parser()
solve_chart.add_argument("jobId", type=int, help="the id of job", location='form')
solve_chart.add_argument("begin", type=int, help="the begin of iteration step", location='form')
solve_chart.add_argument("accesstoken", type=str, help="the token to attach middleware", location='form')

convert_parser = ns.parser()
convert_parser.add_argument("origin-file", type=str, help="the path of the origin file", location='form')
convert_parser.add_argument("output-dir", type=str,
                            help="the directory that result of converting ouputs", location='form')
convert_parser.add_argument("convert-type", type=int, help="the type of converter, "
                                                           "example: 0 means cad converts to vtm, 1 means openfoam "
                                                           "mesh converts to su2mesh and vtm", location='form')
convert_status = ns.parser()
convert_status.add_argument("convertId", type=int, help="the id of convert operation", location='form')

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
        solve_args = ["work-path", "mesh-file-name", "username",
                      "job-name", "solve-app", "solve-config", "accesstoken"]
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
            return create_resp(1, msg="we didn't get jobId!", result=None)

        result = DB.query_solve_status(solve_id=job_id)

        slurm_id = result["slurmId"]
        status = SlurmDB().query_job_status(slurm_id)
        result["currentStep"] = result["currentStep"] + 1 if result["currentStep"] > 0 else 0
        result["slurmStatus"] = status

        return create_resp(0, msg="", result=result)


@ns.route("/stop-job")
class StopJob(Resource):
    """
    :description 停止作业
    """

    @ns.doc(parser=stop_solve_parser)
    def post(self):
        arg = dict(stop_solve_parser.parse_args())
        job_id = arg.get("jobId", None)
        if job_id is None:
            return create_resp(1, msg="we didn't get jobId!", result=None)

        code, msg = stop_solve(job_id)
        return create_resp(code, msg, result=None)


@ns.route("/solve-chart")
class SolveChart(Resource):
    """
    :description 仿真图表
    """
    @ns.doc(parser=solve_chart)
    def post(self):
        arg = dict(solve_chart.parse_args())
        job_id = arg.get("jobId", None)
        if job_id is None:
            return create_resp(1, msg="we didn't get jobId!", result=None)
        begin = arg.get("begin", 0)
        result = DB.query_solve_chart(solve_job_id=job_id, begin=begin)
        return create_resp(0, msg="success", result=result)


@ns.route("/common-convert")
class CommonConvert(Resource):

    """
    :description 转换接口
    """
    @ns.doc(parser=convert_parser)
    def post(self):
        in_arg = dict(convert_parser.parse_args())
        args_list = ["origin-file", "output-dir", "convert-type"]
        for arg in args_list:
            if arg not in in_arg:
                return create_resp(1, msg=f"we didn't get arg!", result=None)
        convert_id, msg = ConvertControler(in_arg["origin-file"],
                                           in_arg["output-dir"], in_arg["convert-type"]).start_actions()
        if convert_id == -1:
            return create_resp(1, msg, result={})
        else:
            return create_resp(0, msg="success!", result={"convertId": convert_id})


@ns.route("/convert-status")
class ConvertStatus(Resource):
    """
    :description 转换的状态
    """
    @ns.doc(parser=convert_status)
    def post(self):
        in_arg = dict(convert_status.parse_args())
        convert_id = in_arg.get("convertId", None)
        if convert_id is not None:
            res = DB.query_convert(convert_id)
            return create_resp(0, msg="success!", result=res)
        else:
            return create_resp(1, msg=f"没有接收到convertId", result={})


class HttpServer(AshuraServer):

    def _init(self):
        self._app = Flask("AshuraServer")
        self._api = Api(app=self._app, title="中间件接口文档", version="v0.1", description="无描述")
        self.easy_wsgi_server = None
        self._api.add_namespace(ns)

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
        self.easy_wsgi_server = WSGIServer((self.host, self.port), self._app)
        self.easy_wsgi_server.serve_forever()

    def __getattr__(self, item):

        if item not in ["_from_parts", "_parse", "_init", "server", "run_server"]:
            try:
                return getattr(self._app, item)
            except AttributeError:
                return getattr(self._api, item)
