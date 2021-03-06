# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: maps.py
@time: 2019/5/5 下午2:09 
"""

# 解算软件的类型编号
CAE_APPLICATION_TYPE = (
    "SU2",
    "OpenFoam",
    "MOOSE"
)

SU2_SOLVE_CONFIG_MAP = {
    "InitialCondition": "init_cfg",  # su2的初始条件
    "BoundaryCondition": "bound_cfg",  # 边界条件
    "Run": "parl_cfg"  # 并行配置
}

# JSON映射到SU2配置文件
JSON_2_SU2CONFIG = {
    "R": "R",
    "gamma": "gamma",
    "density": "density",
    "AOA": "AOA",
    "Mach": "Mach",
    "slider": "slider",
    "Reynolds": "Reynolds",
    "temperature": "temperature",
    "Reynolds_length": "Reynolds_length",
    "wall": "WALL_MARKER_HEATFLUX",
    "far_bc": "FAR_BC_MARKER_FAR",
    "symmetric": "SYMMETRIC_MARKER_SYM",
    "scheme": "scheme",
    "CFL": "CFL",
    "EXT_NUMBER": "EXT_NUMBER",
    "SAVE_RESULT": "SAVE_RESULT",
    "SAVE_HISTORY": "SAVE_HISTORY",
}

JSON_2_SLURMCONFIG = {
    "numProc": "total_core"
}

# 数据库映射到JSON
DB_2_JSON = {
    "solve": {
        "solve_id": "jobId",
        "solve_path": "solve_path",
        "mesh_path": "mesh_path",
        "username": "username",
        "solve_app": "solve_app",
        "solve_config": "solve_config",
        "launch_script": "launch_script",
        "create_time": "create_time"
    },
    "solve_status": {
        "solve_id": "jobId",
        "core_num": "coreNum",
        "slurm_id": "slurmId",
        "slurm_status": "slurmStatus",
        "total_step": "totalStep",
        "current_step": "currentStep",
        "log_file": "logFile",
        "error_file": "errorFile",
    },
    "solve_results": {

    },
    "solve_chart": {
        "solve_id": "jobId",
        "iteration_step": "iterationStep",
        "multi_fields": "multiFields",
    },
    "convert": {
        "convert_id": "convertId",
        "origin_file": "originFile",
        "des_file": "desFile",
        "vf_file": "vfFile",
        "thumb_nail": "thumbNail",
        "convert_type": "convertType",
        "convert_status": "convertStatus",
        "convert_infos": "convertInfos",
        "begin_time": "beginTime",
        "end_time": "endTime"
    },
    "mesh_status": {
        "mesh_id": "meshId",
        "core_num": "coreNum",
        "slurm_id": "slurmId",
        "slurm_status": "slurmStatus",
        "total_step": "totalStep",
        "current_step": "currentStep",
        "log_file": "logFile",
        "error_file": "errorFile",
        "create_time": "createTime"
    },
    "compute_domain": {
        "domain_id": "domainId",
        "cad_file_path": "cadFilePath",
        "status": "status",
        "vf_path": "vfPath",
        "create_time": "createTime"
    }
}

MESH_APP = (
    "CFMesh2D",
    "CFMesh",
)

# 参数映射到数据库
ARGS_2_DB = {
}


CONVERT_CLASSES = [
    ("cad2vtm", "Cad2VtmConverter"),
    ("foam2su2_vtm", "Foam2su2Converter")
]

OPENFOAM_CLASSES = {
    "meshDict": "dictionary",
}

MONITOR_HANDLERS_CLASSES_MAP = {
    "SU2": "SU2ResultHandler",
}