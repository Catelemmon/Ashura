# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: CFmeshConfigParsers.py
@time: 2019/5/31 下午5:10 
"""
import copy
import json
from typing import Dict, List

from parsers.OFDictParser import OFDictParse

"mesh_scale"

CELL_TYPE_MAPS = {
    "Cube": "box"
}

EXCLUDE_SET = {"guid", }

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


def wtih_item_cell_parser(item_cells: List):
    item_list = None
    res = {}
    share_dict = {}
    for cell in item_cells:
        for key in cell:
            if key in EXCLUDE_SET:
                continue
            if key == "items":
                item_list = copy.deepcopy(cell["items"])
                continue
            share_dict[key] = cell[key]
    for item in item_list:
        res[item] = {}
        item_quote = res[item]
        item_quote.update(copy.deepcopy(share_dict))
    return res


def local_refinements_parser(local_refinements_args: Dict):
    res = {}
    local_refinment = local_refinements_args["localRefinement"]
    res["localRefinement"] = {}
    refinement = res["localRefinement"]
    items_dict_res = wtih_item_cell_parser(local_refinment)
    refinement.update(items_dict_res)
    return res
    # for face_refine in local_refinment:
    #
    #     batch_arg_dict = {}
    #     for inner_arg in face_refine:
    #         if inner_arg != "items" and inner_arg not in EXCLUDE_SET:
    #             batch_arg_dict[inner_arg] = face_refine[inner_arg]
    #
    #     faces = face_refine["items"]
    #
    #
    #
    #
    #     for face in faces:
    #         if face["type"] == "topo":
    #             for sub_face in face["items"]:
    #                 single_face = {sub_face["name"]: copy.deepcopy(batch_arg_dict)}
    #                 refinement.update(single_face)
    #             continue
    #         single_face = {face["name"]: copy.deepcopy(batch_arg_dict)}
    #         refinement.update(single_face)
    # return res


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

            patch_boundary_layer_inner_res = wtih_item_cell_parser(boudary_layer["patchBoundaryLayers"])
            inner_layer.update(patch_boundary_layer_inner_res)

            # for iiter_layer in boudary_layer[layer]:
            #
            #     batch_arg_dict = {}
            #
            #     for inner_arg in iiter_layer:
            #         if inner_arg != "items":
            #             batch_arg_dict[inner_arg] = iiter_layer[inner_arg]
            #
            #     faces = iiter_layer["items"]
            #     for face in faces:
            #         if face["type"] == "topo":
            #             for sub_face in face["items"]:
            #                 single_face = {sub_face["name"]: copy.deepcopy(batch_arg_dict)}
            #                 inner_layer.update(single_face)
            #             continue
            #         single_face = {face["name"]: copy.deepcopy(batch_arg_dict)}
            #         inner_layer.update(single_face)
            res["boundaryLayers"].update(patch_boundary_layer_dict)
    return res


FIELDS_FUNCS = {
    "mesh_scale": mesh_scale_parser,
    "objectRefinements": object_refinements_parser,
    "localRefinement": local_refinements_parser,
    "boundary_layer": boudary_layer_parse
}


def cfmesh_config_parser(cfmesh_dict: Dict, cad_file: Dict):
    args = cfmesh_dict["meshParams"]["args"]
    total_res = cad_file
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
                "point1": [0, 0, 0],
                "point2": [500, 500, 500]
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
                  "guid": "12344",
                  "value": {
                    "xLength": 3,
                    "yLength": 4,
                    "zLength": 5,
                    "center": [0, 0, 0],
                    "additionalRefinementLevels": 7
                  }
                },
                {
                  "type": "Sphere",
                  "name": "Sphere1",
                  "guid": "123448",
                  "value": {
                    "radius": 5,
                    "center": [0, 0, 0],
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
                  "guid": "a34343",
                  "additionalRefinementLevels": 4,
                  "items": ["Face_39", "Face_40"]
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
                  "relThicknessTol": 0.3,
                  "featureSizeFactor": 1
                },
                "symmetryPlaneLayerTopology": 1,
                "untangleLayers": 1,
                "patchBoundaryLayers": [
                  {
                    "guid": "a34343",
                    "additionalRefinementLevels": 4,
                    "items": ["Face_39", "Face_40"]
                  }
                ]   
              }
            }
          }
        },
        {
          "formName": "并行设置",
          "name": "processors_number",
          "formSchema": {
            "value": {
              "processorsNumber": {
                "processorsNumber": 2,
                "min": 1,
                "max": 10
              }
            }
          }
        }
      ]
    }
  }
  """
    d = json.loads(s)
    # print(wtih_item_cell_parser(d))
    res_dict = cfmesh_config_parser(d, {"surfaceFile": "\"solid.stl\""})
    ofdp = OFDictParse("meshDict")
    print(ofdp.hard_render(res_dict))
    # print(json.dumps(res_dict, indent="    "))
