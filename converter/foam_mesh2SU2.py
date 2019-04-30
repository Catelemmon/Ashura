# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: foam_mesh2SU2.py
@time: 2019/4/11 上午11:50 
"""

import os, re, codecs
from typing import Callable

from paraview.simple import *

MARKER_TYPE_ENUM = {  # SU2里面的Marker就是vtk文件中的ploydata即面网格, openfoam的boundary
    2: 3,  # 两个点是一条线
    3: 5,  # 三个点是三角形
    4: 9,  # 四边形
}

ELEM_TYPE_ENUM = {  # SU2里面的ELEM就是vtk文件中的UNSTRUCTURED_GRID即体网格, openfoam的cell
    4: 10,  # 四个点是四面体
    8: 12,  # 八个点是六面体
    6: 13,  # 六个点是棱镜
    5: 14,  # 五个点是金字塔(五面体)
}

class Foam2SU2Converter:

    __slots__ = ('foam_file', 'su2_file', 'mesh_dim', 'point_map')

    def __init__(self, foam_file, su2_mname, su2_mdir, mesh_dim="3D"):
        self.foam_file = foam_file
        su2_file_path = os.path.join(su2_mdir, su2_mname+".su2")
        self.su2_file = codecs.open(su2_file_path, encoding="utf-8", mode="a")
        self.mesh_dim = mesh_dim[0]
        self.point_map = {}  # 存储点的一个反序列
        if mesh_dim == "3D":
            self.do_convert = self.convert3D
        elif mesh_dim == "2D":
            self.do_convert = self.convert2D
        else:
            raise ValueError("mesh_dim is not a correct value! ")

    def convert3D(self):

        foam = self._read_foam()
        foam = self._capture_meshs(foam)
        vtk_agent = self._vtk_agent(foam)
        inter_mesh, bmeshes = self._meshes(vtk_agent)
        bm_names = self._bm_names(foam, vtk_agent)
        Delete(foam)
        del vtk_agent
        self._write_su2(inter_mesh, bmeshes, bm_names)
        pass

    def convert2D(self):
        # 业务暂时不需要
        pass

    def _read_foam(self):
        foam = OpenFOAMReader(FileName=self.foam_file)
        return foam

    def _capture_meshs(self, foam):
        foam.MeshRegions = foam.MeshRegions.GetAvailable()
        return foam

    def _vtk_agent(self, foam):
        # 获取vtk原生的数据结构-vtkOpenFoamReader
        # 接下来的很多东西都是从这里面读取
        vtk_agent = foam.SMProxy.GetClientSideObject()
        return vtk_agent

    def _meshes(self, vtk_agent):
        # 返回blocks(meshes)
        vtk_info = vtk_agent.GetOutput()
        vtk_agent.Update()
        bmeshes = []
        inter_mesh, bound_mesh = vtk_info.GetBlock(0), vtk_info.GetBlock(1)
        bound_mesh_num = bound_mesh.GetNumberOfBlocks()
        for i in xrange(bound_mesh_num):
            bmeshes.append(bound_mesh.GetBlock(i))
        return inter_mesh, bmeshes

    def _bm_names(self, foam ,vtk_agent):
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
        return bm_names

    def _write_su2(self, inter_mesh, bmeshs, bm_names):
        self.su2_file.write("NDIME= {}\n".format(self.mesh_dim))  # 写入网格维度
        self._write_inter_mesh(inter_mesh)
        self._write_im_points(inter_mesh)  # 写入点文件并建立点文件的映射
        del inter_mesh
        self._write_markers(bmeshs, bm_names)

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

        psp = re.compile("[\(\),]")
        for pc in xrange(imp_num):
            point = inter_mesh.GetPoint(pc)
            self.point_map[point] = pc  # 对点进行反向映射
            ps = re.sub(psp, "", str(point))
            self.su2_file.write(ps+" {}".format(pc)+"\n")
        return imp_num

    def _write_markers(self, bmeshes, bm_names):
        self.su2_file.write("NMARK= {}\n".format(len(bmeshes)))  # 写入NMARK
        lp = re.compile("[\[\],]")  # list pattern

        for bmi, bm in enumerate(bmeshes):
            #  遍历所有的面网格(boundary网格)
            self.su2_file.write("MARKER_TAG= {}\n".format(bm_names[bmi]))  # 输出这个网格的名字
            bm_polynum = bm.GetNumberOfCells()  # boundary网格总共有多少个
            self.su2_file.write("MARKER_ELEMS= {}\n".format(bm_polynum))  # 输出网格总共多少个poly(cell, elems)
            for pc in xrange(bm_polynum):  # 遍历所有的poly
                poly = bm.GetCell(pc)  # 获取一个poly
                poly_type = poly.GetCellType()  # 获取poly的type
                pp_num = poly.GetNumberOfPoints()  # 获取poly的点数
                points = []
                for ppi in xrange(pp_num):  # 遍历poly所有的点
                    pt_id = poly.GetPointId(ppi)

                    # 访问反向映射, 构造新的点
                    point = bm.GetPoint(pt_id)
                    pt_id = self.point_map.get(point, -1)
                    if pt_id is -1:
                        print "没有取到对应的点"
                    points.append(pt_id)
                pl = re.sub(lp, "", str(points))
                poly_str = "{poly_type} {point_list} {poly_count}\n".format(poly_type=poly_type,
                                                                          point_list=pl, poly_count=pc)
                self.su2_file.write(poly_str)

if __name__ == '__main__':
    # case_dir = "/home/cicada/workspace/paraview_workspace/Semi_Trailer_Truck_finemesh/case.foam"
    case_dir = "/home/cicada/workspace/paraview_workspace/rae2822Square_luo/case.foam"
    # case_dir = "/home/cicada/workspace/paraview_workspace/airplot/airplot.foam"
    cwd = os.getcwd()
    of2su2c = Foam2SU2Converter(foam_file=case_dir, su2_mname="rae2822Square_luo", su2_mdir=cwd)
    of2su2c.do_convert()
