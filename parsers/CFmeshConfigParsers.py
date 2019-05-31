# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: CFmeshConfigParsers.py
@time: 2019/5/31 下午5:10 
"""
import copy
import json
from typing import Dict

from parsers.OFDictParser import OFDictParse

"mesh_scale"

CELL_TYPE_MAPS = {
    "Cube": "box"
}


def _box_parse(box_dict: Dict):
    box_res = {"type": "box"}
    value = box_dict["value"]
    centre_str = str(tuple(value["center"])).replace(",", "")
    box_res["centre"] = centre_str
    box_res["lengthX"] = value["xLength"]
    box_res["lengthY"] = value["yLength"]
    box_res["lengthZ"] = value["zLength"]
    box_res["additionalRefinementLevels"] = value["additionalRefinementLevels"]
    if "refinementThickness" in value:
        box_res["refinementThickness"] = value["refinementThickness"]
    return {box_dict["name"]: box_res}


def _sphere_parse(sphere_dict: Dict):
    sphere_res = {"type": "sphere"}
    value = sphere_dict["value"]
    centre_str = str(tuple(value["center"])).replace(",", "")
    sphere_res["centre"] = centre_str
    sphere_res["radius"] = value["radius"]
    sphere_res["additionalRefinementLevels"] = value["additionalRefinementLevels"]
    if "refinementThickness" in value:
        sphere_res["refinementThickness"] = value["refinementThickness"]
    return {sphere_dict["name"]: sphere_res}


CELL_FUNCS = {
    "Cube": _box_parse,
    "Sphere": _sphere_parse,
}


def mesh_scale_parser(mesh_scale_args: Dict):
    return mesh_scale_args


def object_refinements_parser(object_refinements_args: Dict):
    res = {}
    object_refinement = object_refinements_args["objectRefinements"]
    res["objectRefinements"] = {}
    refinement = res["objectRefinements"]
    for cell_refine in object_refinement:
        cell_parse_func = CELL_FUNCS.get(cell_refine["type"], None)
        if cell_parse_func:
            refinement.update(cell_parse_func(cell_refine))
    return res


def local_refinements_parser(local_refinements_args: Dict):
    res = {}
    local_refinment = local_refinements_args["localRefinement"]
    res["localRefinement"] = {}
    refinement = res["localRefinement"]
    for face_refine in local_refinment:
        level = {"additionalRefinementLevels": face_refine["additionalRefinementLevels"]}
        faces = face_refine["items"]
        for face in faces:
            if face["type"] == "topo":
                for sub_face in face["items"]:
                    single_face = {sub_face["name"]: copy.deepcopy(level)}
                    refinement.update(single_face)
                continue
            single_face = {face["name"]: copy.deepcopy(level)}
            refinement.update(single_face)
    return res


def boudary_layer_parse(boundary_layer_dict: Dict):
    res = {}
    boudary_layer = boundary_layer_dict["boundaryLayers"]
    res["boundaryLayers"] = {}
    boundaries = res["boundaryLayers"]
    for layer in boudary_layer:
        if layer != "patchBoundaryLayers":
            boundaries[layer] = boudary_layer[layer]
        else:
            patch_boundary_layer_dict = {"patchBoundaryLayers": {}}
            inner_layer = patch_boundary_layer_dict["patchBoundaryLayers"]
            for iiter_layer in boudary_layer[layer]:
                level = {"additionalRefinementLevels": iiter_layer["additionalRefinementLevels"]}
                faces = iiter_layer["items"]
                for face in faces:
                    if face["type"] == "topo":
                        for sub_face in face["items"]:
                            single_face = {sub_face["name"]: copy.deepcopy(level)}
                            inner_layer.update(single_face)
                        continue
                    single_face = {face["name"]: copy.deepcopy(level)}
                    inner_layer.update(single_face)
            res["boundaryLayers"].update(patch_boundary_layer_dict)
    return res


FIELDS_FUNCS = {
    "mesh_scale": mesh_scale_parser,
    "objectRefinements": object_refinements_parser,
    "localRefinement": local_refinements_parser,
    "boundary_layer": boudary_layer_parse
}


def merge_parse(cfmesh_dict: Dict):
    args = cfmesh_dict["meshParams"]["args"]
    total_res = {}
    for arg in args:
        field_arg = arg["formSchema"]["value"]
        field_func = FIELDS_FUNCS.get(arg["name"], None)
        if field_func:
            field_res = field_func(field_arg)
            total_res.update(field_res)
    return total_res


if __name__ == '__main__':
    s = """{
    "curProperty": "INDEX",
    "meshParams": {
        "args": [
            {
                "formName": "计算域",
                "name": "comp_domain",
                "formSchema": {
                    "value": {
                        "type": "Cube",
                        "args": {
                            "point1": [
                                0,
                                0,
                                0
                            ],
                            "point2": [
                                500,
                                500,
                                500
                            ]
                        }
                    }
                }
            },
            {
                "formName": "网格尺度",
                "name": "mesh_scale",
                "formSchema": {
                    "value": {
                        "boundaryCellSize": 10,
                        "minCellSize": 30,
                        "boundaryCellSizeRefinementThickness": 1,
                        "keepCellsIntersectingBoundary": 1,
                        "checkForGluedMesh": 0,
                        "enforceGeometryConstraints": 1,
                        "maxCellSize": 1
                    }
                }
            },
            {
                "formName": "局部细化",
                "name": "objectRefinements",
                "formSchema": {
                    "value": {
                        "objectRefinements": [
                            {
                                "type": "Cube",
                                "name": "Cube1",
                                "value": {
                                    "xLength": 3,
                                    "yLength": 4,
                                    "zLength": 5,
                                    "center": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "additionalRefinementLevels": 7
                                }
                            },
                            {
                                "type": "Sphere",
                                "name": "Sphere1",
                                "value": {
                                    "radius": 5,
                                    "center": [
                                        0,
                                        0,
                                        0
                                    ],
                                    "additionalRefinementLevels": 7,
                                    "refinementThickness": 0.3
                                }
                            }
                        ]
                    }
                }
            },
            {
                "formName": "面",
                "name": "localRefinement",
                "formSchema": {
                    "value": {
                        "localRefinement": [
                            {
                                "additionalRefinementLevels": 4,
                                "items": [
                                    {
                                        "type": "face",
                                        "name": "face1"
                                    },
                                    {
                                        "type": "face",
                                        "name": "face2"
                                    },
                                    {
                                        "type": "face",
                                        "name": "face3"
                                    },
                                    {
                                        "type": "topo",
                                        "name": "topo1",
                                        "items": [
                                            {
                                                "type": "face",
                                                "name": "face1"
                                            },
                                            {
                                                "type": "face",
                                                "name": "face2"
                                            },
                                            {
                                                "type": "face",
                                                "name": "face3"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            },
            {
                "formName": "边界层",
                "name": "boundary_layer",
                "formSchema": {
                    "value": {
                        "boundaryLayers": {
                            "optimiseLayer": 1,
                            "optimisationParameters": {
                                "nSmoothNormals": 10,
                                "maxNumIterations": 30,
                                "reCalculateNormals": 1,
                                "relThicknessTol": 0.3
                            },
                            "symmetryPlaneLayerTopology": 1,
                            "untangleLayers": 1,
                            "patchBoundaryLayers": [
                                {
                                    "additionalRefinementLevels": 4,
                                    "items": [
                                        {
                                            "type": "face",
                                            "name": "face1"
                                        },
                                        {
                                            "type": "face",
                                            "name": "face2"
                                        },
                                        {
                                            "type": "face",
                                            "name": "face3"
                                        },
                                        {
                                            "type": "topo",
                                            "name": "topo1",
                                            "items": [
                                                {
                                                    "type": "face",
                                                    "name": "face1"
                                                },
                                                {
                                                    "type": "face",
                                                    "name": "face2"
                                                },
                                                {
                                                    "type": "face",
                                                    "name": "face3"
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        ]
    },
    "toposetInfo": [
        {
            "name": "topo1",
            "children": [
                {
                    "name": "face1",
                    "selected": true,
                    "visibility": true
                }
            ]
        }
    ]
}"""
    d = json.loads(s)
    res_dict = merge_parse(d)
    ofdp = OFDictParse("meshDict")
    print(ofdp.hard_render(res_dict))
    # print(json.dumps(res_dict, indent="    "))
