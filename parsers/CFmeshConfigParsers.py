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

EXCLUDE_SET = {"guid", "source", "mapper", "actor"}


def is_float(v):
    try:
        float(v)
        return True
    except Exception:
        return False


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
    mesh_scale_arg_res = copy.deepcopy(mesh_scale_args)
    for key in mesh_scale_args:
        if mesh_scale_args[key] == "0":
            mesh_scale_arg_res.pop(key)
    return mesh_scale_arg_res


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
    s = """{"meshParams": {"args": [{"name": "comp_domain", "formName": "计算域", "formSchema": {"value": {"args": {"point1": [0, 0, 0], "point2": [500, 500, 500]}, "type": "Cube"}}}, {"name": "mesh_scale", "formName": "全局参数", "formSchema": {"value": {"maxCellSize": 1, "minCellSize": 0, "boundaryCellSize": 0, "checkForGluedMesh": 0, "enforceGeometryConstraints": 0, "keepCellsIntersectingBoundary": 0, "boundaryCellSizeRefinementThickness": 0}}}, {"name": "objectRefinements", "formName": "体细化", "formSchema": {"value": {"objectRefinements": [{"guid": "4ff525c1-c443-65b5-02ae-65abf83374ad", "name": "长方体1", "type": "Cube", "actor": {}, "value": {"center": ["4", "2", 0], "xLength": "12", "yLength": "4", "zLength": "5", "refinementThickness": 0, "additionalRefinementLevels": "2"}, "mapper": {}, "source": {}}, {"guid": "f70303c5-5a82-4845-f683-366ac8482a76", "name": "长方体0", "type": "Cube", "actor": {}, "value": {"center": ["0.75", "0.8", 0], "xLength": "2", "yLength": "1.6", "zLength": "0.6", "refinementThickness": 0, "additionalRefinementLevels": "4"}, "mapper": {}, "source": {}}]}}}, {"name": "localRefinement", "formName": "面细化", "formSchema": {"value": {"localRefinement": [{"guid": "a34343", "items": ["Face_39", "Face_40", "Face_2", "Face_3"], "additionalRefinementLevels": "6"}, {"guid": "a3dfa28b-ef7b-7ac2-50ff-b5a43d0c049a", "items": ["Face_4", "Face_5", "Face_6"], "additionalRefinementLevels": "7"}, {"guid": "0bae04ce-e3fa-69e1-fac3-014a192447b8", "items": ["Face_7", "Face_8", "Face_9"], "additionalRefinementLevels": "8"}]}}}, {"name": "boundary_layer", "formName": "边界层", "formSchema": {"value": {"boundaryLayers": {"optimiseLayer": 1, "nSmoothNormals": "10", "untangleLayers": 1, "relThicknessTol": "0.2", "maxNumIterations": "30", "featureSizeFactor": "0.5", "allowDiscontinuity": 0, "reCalculateNormals": 1, "patchBoundaryLayers": [{"items": ["Face_39", "Face_40", "Face_2", "Face_3", "Face_4", "Face_5", "Face_6", "Face_7", "Face_8", "Face_9"], "nLayers": "20", "thicknessRatio": "1.2", "maxFirstLayerThickness": "0.0001"}], "optimisationParameters": {"nSmoothNormals": 5, "relThicknessTol": 0.1, "maxNumIterations": 10, "featureSizeFactor": 0.3, "allowDiscontinuity": 0, "reCalculateNormals": 1}, "symmetryPlaneLayerTopology": 1}}}}, {"name": "processors_number", "formName": "并行设置", "formSchema": {"value": {"processorsNumber": {"max": 10, "min": 1, "processorsNumber": 10}}}}]}, "curProperty": "INDEX"}"""
    d = json.loads(s)
    # print(wtih_item_cell_parser(d))
    res_dict = cfmesh_config_parser(d, {"surfaceFile": "\"solid.stl\""})
    ofdp = OFDictParse("meshDict")
    print(ofdp.hard_render(res_dict))
    # print(json.dumps(res_dict, indent="    "))
