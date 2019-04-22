# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: HttpServer.py
@time: 2019/4/19 下午2:55 
"""
from typing import Dict

from service.AshuraServer import AshuraServer
from flask import Flask
from flask_restful import Resource, Api, request


class DoSolve(Resource):
    def post(self):
        pass


class JobResults(Resource):
    def post(self):
        pass


class JobChart(Resource):
    def post(self):
        pass


class CadConvert(Resource):
    pass


class HttpServer(AshuraServer):

    def _init(self):
        self._app = Flask("AshuraServer")
        self._api = Api(app=self._app)
        self._api.add_resource(DoSolve, "/do_solve")

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
            return getattr(self._app, item)
