# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: HttpServer.py
@time: 2019/4/19 下午2:55 
"""
import copy
import json
from typing import Dict
from gevent.pywsgi import WSGIServer
from actions import solve_flow
from flask import Flask
from flask_restplus import Resource, Api, Namespace
from actions.mesh_flow import MeshControler
from actions.convert_flow import ConvertControler
from actions.solve_flow import stop_solve
from actions.su2mesh_flow import SU2MeshControler
from dbs import DB, SlurmDB
from servers import AshuraServer
from utils.log_utils import get_logger

http_server_logger = get_logger("http_server")

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
solve_chart.add_argument("iterationStep", type=int, help="the begin of iteration step", location='form')
solve_chart.add_argument("accesstoken", type=str, help="the token to attach middleware", location='form')

convert_parser = ns.parser()
convert_parser.add_argument("origin-file", type=str, help="the path of the origin file", location='form')
convert_parser.add_argument("des-file", type=str,
                            help="the absolute path of destination file", location='form')
convert_parser.add_argument("vf-file", type=str,
                            help="the absolute path of visual file")
convert_parser.add_argument("convert-type", type=int, help="the type of converter, "
                                                           "example: 0 means origin cad converts to stl and vtk, "
                                                           "1 means openfoam mesh converts to su2mesh and vtm",
                            location='form')
convert_parser.add_argument("thumb-path", type=str, help="thumbnail image path", location='form')
convert_parser.add_argument("accesstoken", type=str, help="the token to attach middleware", location='form')

convert_status = ns.parser()
convert_status.add_argument("convertId", type=int, help="the id of convert operation", location='form')
convert_status.add_argument("accesstoken", type=str, help="the token to attach middleware", location='form')

mesh_parser = ns.parser()
mesh_parser.add_argument("work-path", type=str, help="workspace of mesh", location='form')
mesh_parser.add_argument("cad-file-path", type=str, help="the path of cad", location='form')
mesh_parser.add_argument("username", type=str, help="who sends the mesh", location='form')
mesh_parser.add_argument("mesh-name", type=str, help="the name of mesh", location='form')
mesh_parser.add_argument("mesh-app", type=int, help="mesh application", location='form')
mesh_parser.add_argument("mesh-config", type=str, help="the config of mesh application", location='form')
mesh_parser.add_argument("accesstoken", type=str, help="the token to attach middleware", location='form')

mesh_status_parser = ns.parser()
mesh_status_parser.add_argument("meshId", type=int, help="the id of mesh", location='form')
mesh_status_parser.add_argument("accesstoken", type=str, help="the token to attach middleware", location='form')

su2_mesh_parser = ns.parser()
su2_mesh_parser.add_argument("work-path", type=str, help="workspace of mesh", location='form')
su2_mesh_parser.add_argument("cad-file-path", type=str, help="the path of cad", location='form')
su2_mesh_parser.add_argument("vf-path", type=str, help="the path of visual file", location='form')
su2_mesh_parser.add_argument("thumb-path", type=str, help="image path of visual file", location='form')
su2_mesh_parser.add_argument("username", type=str, help="who sends the mesh", location='form')
su2_mesh_parser.add_argument("mesh-name", type=str, help="the name of mesh", location='form')
su2_mesh_parser.add_argument("mesh-app", type=int, help="mesh application", location='form')
su2_mesh_parser.add_argument("mesh-config", type=str, help="the config of mesh application", location='form')
su2_mesh_parser.add_argument("accesstoken", type=str, help="the token to attach middleware", location='form')

su2mesh_status_parser = ns.parser()
su2mesh_status_parser.add_argument("meshId", type=int, help="the id of mesh", location='form')

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
class JobStatus(Resource):
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
        if result is None:
            return create_resp(1, msg="没有该仿真作业的状态", result=None)
        slurm_id = result["slurmId"]
        status = SlurmDB().query_job_status(slurm_id)
        if status == -2:
            return create_resp(1, msg="slurm中没有对应的作业", result=None)
        result["currentStep"] = result["currentStep"] + 1 if result["currentStep"] > 0 else 0
        result["slurmStatus"] = status

        return create_resp(0, msg="success", result=result)


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
        begin = arg.get("iterationStep", 0)
        if begin is None:
            begin = 0
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
        args_list = ["origin-file", "vf-file", "convert-type"]
        for arg in args_list:
            if arg not in in_arg:
                return create_resp(1, msg=f"we didn't get arg!", result=None)
        try:

            convert_id, msg = ConvertControler(in_arg["origin-file"],
                                               in_arg.get("des-file", ""), in_arg["vf-file"],
                                               in_arg["convert-type"], in_arg.get("thumb-path", None)).start_actions()
        except Exception:
            return create_resp(1, msg="上传文件错误 | 请上传正确的文件", result={})
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
            return create_resp(1, msg=f"没有接收到convertId", result=None)


@ns.route("/do-mesh")
class DoMesh(Resource):

    @ns.doc(parser=mesh_parser)
    def post(self):
        # args_list = ["work-path", "cad-file-name", "username", "mesh-name", "mesh-app", "mesh-config"]
        args_list = ["work-path", "cad-file-path", "username", "mesh-name", "mesh-config"]
        in_args = mesh_parser.parse_args()
        for arg in args_list:
            if arg not in in_args:
                return create_resp(2, msg=f"未接收到{arg}", result=None)
        mc = MeshControler(work_path=in_args["work-path"],
                           cad_file_name=in_args["cad-file-path"],
                           username=in_args["username"],
                           mesh_name=in_args["mesh-name"],
                           # mesh_app=in_args["mesh-app"],
                           mesh_config=json.loads(in_args["mesh-config"]))
        mesh_id = mc.start_actions()
        return create_resp(0, "success!", {"meshId": mesh_id})


@ns.route("/su2mesh")
class SU2Mesh(Resource):

    @ns.doc(parser=su2_mesh_parser)
    def post(self):
        args_list = ["work-path", "cad-file-path",
                     "vf-path", "thumb-path", "username", "mesh-name",
                     "mesh-app", "mesh-config"]
        in_args = su2_mesh_parser.parse_args()
        for arg in args_list:
            if arg not in in_args:
                return create_resp(2, msg=f"未接收到参数{arg}", result=None)
        su2mc = SU2MeshControler(
            work_path=in_args["work-path"],
            cad_file_path=in_args["cad-file-path"],
            vf_path=in_args["vf-path"],
            thumb_path=in_args["thumb-path"],
            username=in_args["username"],
            mesh_name=in_args["mesh-name"],
            mesh_app=in_args["mesh-app"],
            mesh_config=json.loads(in_args["mesh-config"])
        )
        mesh_id, msg = su2mc.start_actions()
        return create_resp(0, msg, {"meshId": mesh_id})


@ns.route("/su2mesh-status")
class SU2MeshStatus(Resource):

    @ns.doc(parser=su2mesh_status_parser)
    def post(self):
        in_args = su2mesh_status_parser.parse_args()
        mesh_id = in_args.get("meshId", None)
        if mesh_id is None:
            return create_resp(2, msg=f"未接收到参数meshId", result=None)
        result = DB.query_mesh_convert(mesh_id)
        slurm_id = result["slurmId"]
        status = SlurmDB().query_job_status(slurm_id)
        if status == -2:
            return create_resp(1, msg="slurm中没有对应的作业", result=None)
        result["slurmStatus"] = status
        return create_resp(0, msg="success", result=result)


@ns.route("/mesh-status")
class MeshStatus(Resource):

    @ns.doc(parser=mesh_status_parser)
    def post(self):
        in_arg = dict(mesh_status_parser.parse_args())
        mesh_id = in_arg.get("meshId", None)
        if mesh_id is None:
            return create_resp(1, msg="we didn't get meshId", result=None)
        result = DB.query_mesh_status(mesh_id)
        if result is None:
            return create_resp(1, msg="没有该网格作业的状态", result=None)
        slurm_id = result["slurmId"]
        status = SlurmDB().query_job_status(slurm_id)
        if status == -2:
            return create_resp(1, msg="slurm中没有对应的作业", result=None)
        result["slurmStatus"] = status
        result["currentStep"] = result["totalStep"] - 1 if \
            result["currentStep"] > result["totalStep"] else result["currentStep"]
        return create_resp(0, msg="success", result=result)


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
        self.easy_wsgi_server = WSGIServer((self.host, self.port), self._app, log=http_server_logger)
        self.easy_wsgi_server.serve_forever()

    def __getattr__(self, item):

        if item not in ["_from_parts", "_parse", "_init", "server", "run_server"]:
            try:
                return getattr(self._app, item)
            except AttributeError:
                return getattr(self._api, item)
