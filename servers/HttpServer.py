# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: HttpServer.py
@time: 2019/4/19 下午2:55 
"""
from typing import Dict

from servers.AshuraServer import AshuraServer
from flask import Flask
from flask_restplus import Resource, Api, Namespace, fields

RESPONSE_TEMPLATE = {
    "code": None,
    "msg": None,
    "results": None
}

ns = Namespace("/", description="test operation!")

test_parser = ns.parser()
test_parser.add_argument("solveapp", type=int, help="the id of solve app", location='form')


resource_fields = ns.model('Resource', {
    'job_id': fields.String,
    'mesh_app': fields.Integer
})


class DoSolve(Resource):

    def post(self):



class JobResults(Resource):
    def post(self):
        pass


class JobChart(Resource):
    def post(self):
        pass


class CadConvert(Resource):
    pass


@ns.route("/test")
class Test(Resource):
    @ns.doc(parser=test_parser)
    def post(self):
        args = test_parser.parse_args()
        print(args)
        solve_app = args['solveapp']
        res = RESPONSE_TEMPLATE
        res["results"] = "{'app_id': %s }" % solve_app
        return RESPONSE_TEMPLATE


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
