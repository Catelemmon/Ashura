# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: sub_foam2su2_vtm.py
@time: 2019/4/11 上午11:50
"""
import codecs

from paraview.simple import *
import os
import re
import gc
import json
import collections

class Foam2SU2Converter(object):

    __slots__ = ('foam_file', 'su2_file', 'mesh_dim', 'point_map', 'do_convert')

    def __init__(self, foam_file, su2_mname, su2_mdir, mesh_dim="3D"):
        self.foam_file = foam_file
        su2_file_path = su2_mdir + "/" + su2_mname + ".su2"
        self.su2_file = codecs.open(su2_file_path, encoding="utf-8", mode="a")
        self.mesh_dim = mesh_dim[0]
        self.point_map = {}
        if mesh_dim == "3D":
            self.do_convert = self.convert3d
        elif mesh_dim == "2D":
            self.do_convert = self.convert2d
        else:
            raise ValueError("mesh_dim is not a correct value! ")

    def convert3d(self):

        foam = self._read_foam()
        foam.MeshRegions = foam.MeshRegions.GetAvailable()
        surface = self._capture_surface(foam)  # 提取surface
        surface_vtk = self._vtk_agent(surface)  # 提取surface的原生vtk对象
        vtk_agent = self._vtk_agent(foam)
        inter_mesh = self._inter_mesh(vtk_agent)
        bm_names = self._bm_names(foam, vtk_agent)  # 获取所有的boundary的名字
        Delete(foam)
        Delete(surface)
        del vtk_agent, surface, foam

        # 写入inter_mesh
        self.su2_file.write("NDIME= {}\n".format(self.mesh_dim))  # 写入网格维度
        self._write_inter_mesh(inter_mesh)
        self._write_im_points(inter_mesh)
        del inter_mesh  # 回收inter_mesh对象
        gc.collect()

        # cell surface block 体网格拆面
        cs_block, mp_blocks = self._poly_blocks(surface_vtk)
        del surface_vtk
        gc.collect()
        # cell surface block |  poly multiple block
        pp_sets = self._poly_points_sets(mp_blocks)  # 构造所有的boundary的点集列表

        self._write_markers(cs_block, pp_sets, bm_names)
        del cs_block, pp_sets, bm_names
        gc.collect()

        return None

    def convert2d(self):
        # 业务暂时不需要
        pass

    def _read_foam(self):
        foam = OpenFOAMReader(FileName=self.foam_file)
        return foam

    @classmethod
    def _poly_blocks(cls, surface_vtk):
        s_blocks = surface_vtk.GetOutputDataObject(0)  # surface blocks
        cs_block, mp_block = s_blocks.GetBlock(0), s_blocks.GetBlock(1)
        # cell surface block | poly multiple block

        mp_blocks = []
        for mpi in xrange(mp_block.GetNumberOfBlocks()):
            mp_blocks.append(mp_block.GetBlock(mpi))
        del s_blocks
        gc.collect()
        return cs_block, mp_blocks

    @classmethod
    def _capture_surface(cls, foam):
        ExtractSurface(Input=foam)
        UpdatePipeline()
        sour_dict = GetSources()
        for sour_key, obj in sour_dict.items():
            sour_name, rid = sour_key
            if "ExtractSurface" in sour_name:
                return sour_dict[sour_key]
        return None

    @classmethod
    def _vtk_agent(cls, foam_obj):
        # 从foam_obj中获取vtk原生的数据结构-vtkOpenFoamReader
        vtk_agent = foam_obj.SMProxy.GetClientSideObject()
        return vtk_agent

    @classmethod
    def _inter_mesh(cls, vtk_agent):
        # 返回blocks(meshes)
        vtk_info = vtk_agent.GetOutput()
        vtk_agent.Update()
        inter_mesh = vtk_info.GetBlock(0)
        return inter_mesh

    @classmethod
    def _bm_names(cls, foam ,vtk_agent):
        # 返回boundary mesh的名字
        # 可以和block对应上
        bm_names = {}
        try:
            bms = vtk_agent.GetNumberOfPatchArrays()
            for bmi in bms:
                 bm_names[bmi] = vtk_agent.GetPatchArrayName(bmi)
        except Exception:
            bms = foam.MeshRegions.GetAvailable()[1:]
            for bmi, bm in enumerate(bms):
                bm_names[bmi] = bm
        del bms
        gc.collect()
        return bm_names

    def _write_inter_mesh(self, inter_mesh):
        lp = re.compile("[\[\],L]")  # list pattern
        self.su2_file.write("NELEM= {}\n".format(inter_mesh.GetNumberOfCells()))  # 写入体网格数量
        cell_num = inter_mesh.GetNumberOfCells()
        for cc in xrange(cell_num):
            cell = inter_mesh.GetCell(cc)
            cell_type = cell.GetCellType()
            cell_points = []
            for pc in xrange(cell.GetNumberOfPoints()):
                cell_points.append(cell.GetPointId(pc))
            pl = re.sub(lp, "", str(cell_points))
            cell_str = "{cell_type} {p_list} {cindex}\n".format(cell_type=cell_type, p_list=pl, cindex=cc)
            self.su2_file.write(cell_str)  # 写入体网格

    def _write_im_points(self, inter_mesh):
        imp_num = inter_mesh.GetNumberOfPoints()

        self.su2_file.write("NPOIN= {}\n".format(imp_num))  # 写入总的点数

        psp = re.compile(r"[(),]")
        for pc in xrange(imp_num):
            point = inter_mesh.GetPoint(pc)
            self.point_map[point] = pc  # 对点进行反向映射
            ps = re.sub(psp, "", str(point))
            self.su2_file.write(ps+" {}".format(pc)+"\n")
        return imp_num

    @classmethod
    def _poly_points_sets(cls, mp_blocks):
        pp_sets = []
        for mpb in mp_blocks:
            pps = set()
            for pi in xrange(mpb.GetNumberOfPoints()):
                pps.add(mpb.GetPoint(pi))
            pp_sets.append(pps)
        return pp_sets

    @classmethod
    def _in_pointset(cls, points, mpp_sets):
        flag = False
        for mppi, mpps in enumerate(mpp_sets):
            for p in points:
                if p in mpps:
                    flag = True
                    continue
                else:
                    flag = False
                    break
            if flag:
                return mppi
            else:
                continue
        return None

    def _write_markers(self, cs_block, mpp_sets, bm_names):
        bm_number = len(bm_names)
        self.su2_file.write("NMARK= {}\n".format(bm_number))  # 写入NMARK
        lp = re.compile("[\[\],L]")  # list pattern

        boundary_dict = {bm_names[bm_name]: [] for bm_name in bm_names.keys()}

        # classfication 对点所属的boundary进行分类

        for pl_i in xrange(cs_block.GetNumberOfCells()):
            # poly index 遍历所有的poly
            poly = cs_block.GetCell(pl_i)
            poly_type = poly.GetCellType()  # 获取poly的模型
            poly_points_id = []  # 网格point的id列表
            poly_points = []  # 网格的点, 坐标集合
            for ppi in xrange(poly.GetNumberOfPoints()):
                # poly point index
                # 得到一个poly的所有点
                pt_id = poly.GetPointId(ppi)  #
                poly_points_id.append(pt_id)
                poly_points.append(cs_block.GetPoint(pt_id))

            multi_poly_index = self._in_pointset(poly_points, mpp_sets)

            # 访问反向映射, 构建新的点坐标
            poly_points_id = [self.point_map[pp] for pp in poly_points]

            pl = re.sub(lp, "", str(poly_points_id))
            belong_boundary = bm_names[multi_poly_index]
            poly_str = "{poly_type} {point_list} {poly_count}\n".format(poly_type=poly_type, point_list=pl,
                                                                    poly_count=len(boundary_dict[belong_boundary]))
            boundary_dict[belong_boundary].append(poly_str)  # 添加一个cell的str

        for boundary_name in boundary_dict.keys():
            self.su2_file.write("MARKER_TAG= {}\n".format(boundary_name))
            polys = boundary_dict[boundary_name]
            self.su2_file.write("MARKER_ELEMS= {}\n".format(len(polys)))
            for poly in polys:
                self.su2_file.write(poly)
            del boundary_dict[boundary_name]
            gc.collect()


if __name__ == '__main__':
    # case_dir = "/home/cicada/workspace/paraview_workspace/Semi_Trailer_Truck_finemesh/case.foam"
    res_l = []
    def gen_res(Name, Nm_cell, Nm_point):
        res = collections.OrderedDict()
        # key_name =  "{}:".format(Name)
        # value_cells = "     {0}.cells:{1}".format(Name, Nm_cell)
        # value_points = "     {0}.points:{1}".format(Name, Nm_point)
        # value_all = (value_cells, value_points)
        res["label"] = Name
        res["cell"] = Nm_cell
        res["point"] = Nm_point
        res_l.append(res)

    case_dir = sys.argv[1]
    # case_dir = "C:\\Users\\Administrator\\Desktop\\airFoil2D\\case.foam"
    # case_dir = "/home/cicada/workspace/paraview_workspace/airplot/airplot.foam"
    Load_vtm = sys.argv[2]
    Load_su2 = sys.argv[3]
    # Load_su2 = "C:\\Users\\Administrator\\Desktop\\airFoil2D"
    (filepath, tempfilename) = os.path.split(case_dir)
    (loadpath, tempfilename2) = os.path.split(Load_su2)
    (loadname, extension2) = os.path.splitext(tempfilename2)
    (load_vtmpath, tempfilename3) = os.path.split(Load_vtm)
    (load_vtmname, extension3) = os.path.splitext(tempfilename3)

    of2su2c = Foam2SU2Converter(foam_file=case_dir, su2_mname=loadname, su2_mdir=loadpath)
    of2su2c.do_convert()

    casefoam = OpenFOAMReader(FileName=case_dir)
    List_Mesh_Regions = dict.keys(GetSources())
    scr = GetSources()[List_Mesh_Regions[0]]
    listMesh = scr.MeshRegions.GetAvailable()
    scr.MeshRegions = listMesh   # 选取所有的 Mesh
    UpdatePipeline()
    obj = scr.SMProxy.GetClientSideObject()
    block = obj.GetOutputDataObject(0)
    inter_block = block.GetBlock(0)
    boundory = block.GetBlock(1)
    All_points = block.GetNumberOfPoints()
    inter_cells = inter_block.GetNumberOfCells()
    inter_point = inter_block.GetNumberOfPoints()

    listMesh.remove('internalMesh')
    scr.MeshRegions = listMesh
    UpdatePipeline()

    List_Mesh_Regions = dict.keys(GetSources())
    scr = GetSources()[List_Mesh_Regions[0]]
    obj = scr.SMProxy.GetClientSideObject()
    block = obj.GetOutputDataObject(0)
    Number_Point = block.GetNumberOfPoints()

    Son_cells = []
    Son_points = []

    for i in range(boundory.GetNumberOfBlocks()):
        Son_of_mesh = boundory.GetBlock(i)
        Son_cells.append(Son_of_mesh.GetNumberOfCells())
        Son_points.append(Son_of_mesh.GetNumberOfPoints())

    boundory_Cells = sum(Son_cells)
    All_name = block.GetClassName()
    All_cells = boundory_Cells + inter_cells
    gen_res(All_name, All_cells, All_points)
    gen_res("internalMesh", inter_cells, inter_point)
    gen_res("Pathes", boundory_Cells, Number_Point)

    for i in range(boundory.GetNumberOfBlocks()):
        Son_name = listMesh[i]
        gen_res(Son_name, Son_cells[i], Son_points[i])

    Vtm_path = load_vtmpath + "/" +load_vtmname + ".vtm"
    SaveData(Vtm_path, proxy=casefoam)
    Delete()
    print(json.dumps(res_l))
    print("conversion vtm successful")


