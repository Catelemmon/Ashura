# -*- coding: UTF-8 -*-

from paraview.simple import *
import salome_notebook
import sys
import salome
import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS
import os
import re


class creat_box(object):

    def __init__(self, fpoint, spoint, stl_path, stl_name, vtm_path, vtm_name):
        self.fpoint = fpoint
        self.spoint = spoint
        self.stl_path = stl_path
        self.stl_name = stl_name
        self.vtm_path = vtm_path
        self.vtm_name = vtm_name

    def merge_boxface(self, num, writein):
        with open(self.stl_path + "boxFace_{}.stl".format(num)) as f:
            fi = f.readlines()
            for i in range(len(fi)):
                if i == 0:
                    writein.write("solid boxface{}\n".format(num))
                else:
                    writein.write(fi[i])

    def del_line(self, the_dic_vtk, th_num):
        Read_file = open(the_dic_vtk + "//" + "boxface{}.vtk".format(th_num), "r")
        data_Face = Read_file.read()
        Read_file.close()
        with open(the_dic_vtk + "//" + "boxface{}.vtk".format(th_num), "w") as R_Face_file:
            data_Face = re.sub("LINES[  \d\n]+", "", data_Face)
            R_Face_file.write(data_Face)

    def start_creat(self):
        try:
            stl_path = self.stl_path
            notebook = salome_notebook.NoteBook()
            geompy = geomBuilder.New()
            O = geompy.MakeVertex(0, 0, 0)
            OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
            OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
            OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
            Vertex_1 = geompy.MakeVertex(*self.fpoint)
            Vertex_2 = geompy.MakeVertex(*self.spoint)
            Box_1 = geompy.MakeBoxTwoPnt(Vertex_1, Vertex_2)
            [Face_1, Face_2, Face_3, Face_4, Face_5, Face_6] = geompy.ExtractShapes(Box_1, geompy.ShapeType["FACE"],
                                                                                    True)
            geompy.ExportSTL(Face_1, stl_path + "boxFace_1.stl", True, 0.00001, True)
            geompy.ExportSTL(Face_2, stl_path + "boxFace_2.stl", True, 0.00001, True)
            geompy.ExportSTL(Face_3, stl_path + "boxFace_3.stl", True, 0.00001, True)
            geompy.ExportSTL(Face_4, stl_path + "boxFace_4.stl", True, 0.00001, True)
            geompy.ExportSTL(Face_5, stl_path + "boxFace_5.stl", True, 0.00001, True)
            geompy.ExportSTL(Face_6, stl_path + "boxFace_6.stl", True, 0.00001, True)

            save_vtk_dic = self.vtm_path + "VTK/"
            os.mkdir(save_vtk_dic)
            geompy.ExportVTK(Face_1, save_vtk_dic + "boxface1.vtk", 0.00001)
            geompy.ExportVTK(Face_2, save_vtk_dic + "boxface2.vtk", 0.00001)
            geompy.ExportVTK(Face_3, save_vtk_dic + "boxface3.vtk", 0.00001)
            geompy.ExportVTK(Face_4, save_vtk_dic + "boxface4.vtk", 0.00001)
            geompy.ExportVTK(Face_5, save_vtk_dic + "boxface5.vtk", 0.00001)
            geompy.ExportVTK(Face_6, save_vtk_dic + "boxface6.vtk", 0.00001)
            # 删除vtk中的line信息
            self.del_line(save_vtk_dic, 1)
            self.del_line(save_vtk_dic, 2)
            self.del_line(save_vtk_dic, 3)
            self.del_line(save_vtk_dic, 4)
            self.del_line(save_vtk_dic, 5)
            self.del_line(save_vtk_dic, 6)

            filebox = open(stl_path + "/" + self.stl_name, "a")
            self.merge_boxface(1, filebox)
            self.merge_boxface(2, filebox)
            self.merge_boxface(3, filebox)
            self.merge_boxface(4, filebox)
            self.merge_boxface(5, filebox)
            self.merge_boxface(6, filebox)
            filebox.close()

            add_stl = open(stl_path + self.stl_name, "a")

            with open(stl_path + "/" + self.stl_name) as w:
                wi = w.readlines()
                for i in range(len(wi)):
                    add_stl.write(wi[i])
        except:
            print("stl,vtk生成失败")

        try:
            # 转换vtp,并生成vtm
            Face_VTM = self.vtm_path + "{}.vtm".format(self.vtm_name)
            file_vtm = open(Face_VTM, 'w')
            file_vtm.write(
                '<VTKFile type="vtkMultiBlockDataSet" version="1.0" byte_order="LittleEndian" header_type="UInt64">' + '\n')
            file_vtm.write('  <vtkMultiBlockDataSet>' + '\n')
            file_vtm.write('    <Block index="0" name="box_face">' + '\n')

            # 创建一个boxface用来存放vtp
            os.makedirs(self.vtm_path + "boxface")

            file_num = os.listdir(self.vtm_path + "VTK")
            NM_file = len(file_num)

            for i in range(NM_file):
                # 写入vtm相关信息
                Write_file = 'boxface' + "/" + 'boxface' + str(i + 1) + '.vtp'
                file_vtm.write('      <DataSet index="' + str(i) + '"' + ' name="' + 'boxface' + str(
                    i + 1) + '" file="' + Write_file + '">' + '\n')
                file_vtm.write('      </DataSet>' + '\n')
            file_vtm.write('    </Block>' + '\n')
            file_vtm.write('  </vtkMultiBlockDataSet>' + '\n')
            file_vtm.write('</VTKFile>' + '\n')
            file_vtm.close()

            os.remove(stl_path + "boxFace_1.stl")
            os.remove(stl_path + "boxFace_2.stl")
            os.remove(stl_path + "boxFace_3.stl")
            os.remove(stl_path + "boxFace_4.stl")
            os.remove(stl_path + "boxFace_5.stl")
            os.remove(stl_path + "boxFace_6.stl")
        except:
            print("vtm生成失败")


if __name__ == '__main__':
    first_input = sys.argv[1]  # 为stl原文件
    sec_input = sys.argv[2]  # 为stl目标文件
    thir_input = sys.argv[3]  # 为vtm目标文件
    c1 = sys.argv[4]
    c2 = sys.argv[5]

    new_stl = open(sec_input, 'w')
    with open(first_input) as ori:
        line = ori.readlines()
        for i in range(len(line)):
            new_stl.write(line[i])
    new_stl.close()

    c1_list = re.sub("\(|\)", "", c1).split(",")
    c1_t = tuple([int(i) for i in c1_list])
    c2_list = re.sub("\(|\)", "", c2).split(",")
    c2_t = tuple([int(i) for i in c2_list])
    point1 = c1_t
    point2 = c2_t

    (res_stl_path, give_stl_name) = os.path.split(sec_input)
    give_stl_path = res_stl_path + "/"

    (res_vtm_path, give_vtm_name) = os.path.split(thir_input)
    give_vtm_path = res_vtm_path + "/"

    Creat_boundingbox = creat_box(point1, point2, give_stl_path, give_stl_name, give_vtm_path, give_vtm_name)
    Creat_boundingbox.start_creat()

    try:
        file_num = os.listdir(give_vtm_path + "VTK")
        NM_file = len(file_num)
        for i in range(NM_file):
            Read_File_Path = give_vtm_path + "VTK/" + "boxface{}.vtk".format(i + 1)
            face_vtk = LegacyVTKReader(FileNames=Read_File_Path)
            SaveData(give_vtm_path + "boxface/boxface{}.vtp".format(i + 1), proxy=face_vtk)
            Delete()
    except:
        print("vtk生成失败")
    print("creat_box_successful")
