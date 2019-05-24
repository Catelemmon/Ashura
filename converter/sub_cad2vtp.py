# -*- coding: UTF-8 -*-

from paraview.simple import *
import os
import sys
import salome
#salome.salome_init()
import salome_notebook
import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS
import re
import itertools
import shutil
import collections
import json


class res_dic(object):

    def __init__(self, Indic):
        self.Indic = Indic

    def res_mes(self):
        (filepath, tempfilename) = os.path.split(self.Indic)
        (filename, extension) = os.path.splitext(tempfilename)
        return filepath,tempfilename,filename,extension

class ConversionCad(res_dic):

    def __init__(self, inputfilePath, outputfilePath1, outputfilePath2, SystemSlash ="/"):
        self.inputfilePath = inputfilePath
        self.outputfilePath1 = outputfilePath1
        self.outputfilePath2 = outputfilePath2
        self.SystemSlash = SystemSlash
    def MakeFile(self,creatpath):
        if os.path.exists(creatpath):
            shutil.rmtree(creatpath)
        os.makedirs(creatpath)

    def find_system(self):
        WindowsSlash = "\\"
        LinuxSlash = "/"
        if "/" in self.inputfilePath:
            self.SystemSlash = LinuxSlash
        else:
            self.SystemSlash = WindowsSlash
        return self.SystemSlash

    def make_file_def(self, filepath):
        if os.path.exists(filepath):
            shutil.rmtree(filepath)
        os.makedirs(filepath)

    def _creat_dic(self):
        SystemSlash = self.find_system()
        Creat_in_dic = res_dic(self.inputfilePath)
        Tup_input = Creat_in_dic.res_mes()  # 分别是文件所在目录，文件全称，文件名，文件后缀
        Creat_outVtm_dic = res_dic(self.outputfilePath1)
        Tup_outputVTM = Creat_outVtm_dic.res_mes()
        Creat_out_dic = res_dic(self.outputfilePath2)
        Tup_output = Creat_out_dic.res_mes()

        Load_File_File = Tup_outputVTM[0] + SystemSlash + Tup_outputVTM[2] + "_VTK"
        self.MakeFile(Load_File_File)
        Load_Con_File = Tup_outputVTM[0] + SystemSlash + Tup_outputVTM[2]
        # self.MakeFile(Load_Con_File)
        Load_Vtk_face = Load_File_File + SystemSlash + "Face"
        self.MakeFile(Load_Vtk_face)
        Load_Vtk_wire = Load_File_File + SystemSlash + "Wire"
        self.MakeFile(Load_Vtk_wire)
        Load_Vtk_Rface = Load_File_File + SystemSlash + "RFace"
        self.MakeFile(Load_Vtk_Rface)
        Load_Vtp_face = Tup_outputVTM[0] + SystemSlash + "face"
        self.MakeFile(Load_Vtp_face)
        Load_Vtp_wire = Tup_outputVTM[0] + SystemSlash + "wire"
        self.MakeFile(Load_Vtp_wire)

        return Load_File_File,Load_Con_File,Load_Vtk_face,\
               Load_Vtk_wire,Load_Vtk_Rface,Load_Vtp_face,\
               Load_Vtp_wire,\
               Tup_input,Tup_outputVTM,Tup_output

    def start_convtk(self, Flag_json = 0):
        SystemSlash = self.SystemSlash
        list_load_path = self._creat_dic() # 存储目录列表

        # 利用 salome 打开 stp 文件，并进行拆分，另存为 vtk 文件
        salome.salome_init()
        notebook = salome_notebook.NoteBook()
        sys.path.insert(0, list_load_path[7][0])
        geompy = geomBuilder.New()
        O = geompy.MakeVertex(0, 0, 0)
        OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
        OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
        OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
        try:
            if ".stp" == list_load_path[7][3]:
                Input = geompy.ImportSTEP(self.inputfilePath, False, True)
            elif ".brep" == list_load_path[7][3]:
                Input = geompy.ImportBREP(self.inputfilePath)
            elif ".iges" == list_load_path[7][3]:
                Input = geompy.ImportIGES(self.inputfilePath)

            print("Identification file type successful")
        except Exception:
            print("IOError: file type must be .stp .brep .iges")
            return None

        faces = geompy.ExtractShapes(Input, geompy.ShapeType["FACE"], True)
        face_time = 0
        for index, face in enumerate(faces):
            face_time = face_time + 1
            LoadVTKFPath = list_load_path[2] + self.SystemSlash + "Face_%d" % face_time + ".vtk"
            geompy.ExportVTK(face, LoadVTKFPath, 0.00001)

        # 遍历文件夹，查询拆分个数
        Face_file_NM = os.listdir(list_load_path[2])
        NM_files = len(Face_file_NM)
        print(NM_files)

        # 创建stl文件
        Face_stl_path = self.outputfilePath2
        Face_File_stl = open(Face_stl_path, 'a')

        # 创建vtm文件，并写入开头
        Face_VTM = self.outputfilePath1
        file_vtm = open(Face_VTM, 'a')
        file_vtm.write(
            '<VTKFile type="vtkMultiBlockDataSet" version="1.0" byte_order="LittleEndian" header_type="UInt64">' + '\n')
        file_vtm.write('  <vtkMultiBlockDataSet>' + '\n')
        file_vtm.write('    <Block index="0" name="face">' + '\n')

        try:
            # 删除vtk文件中的lines信息，将删除后的文件写进RFace文件夹中
            for i in range(NM_files):
                Flag_json = Flag_json + 1
                Read_Face_Path = list_load_path[2] + SystemSlash + "Face_" + str(i + 1) + ".vtk"
                Read_RFace_Path = list_load_path[4] + SystemSlash + "Face_" + str(i + 1) + ".vtk"
                Read_Wire_Path = list_load_path[3] + SystemSlash + "Wire_" + str(i + 1) + ".vtk"

                print("rewrite face：{}".format(Read_Face_Path))
                Read_file = open(Read_Face_Path, "r")
                data_Face = Read_file.read()
                Read_file.close()
                with open(Read_RFace_Path, "w") as R_Face_file:
                    data_Face = re.sub("LINES[  \d\n]+", "", data_Face)
                    R_Face_file.write(data_Face)
                    R_Face_file.close()
                # 重写lines信息，并提出所有的cell的pointid构成lines
                RFace_write_path = open(Read_RFace_Path, 'a')
                Read_File_Path = Read_RFace_Path
                face_vtk = LegacyVTKReader(FileNames=Read_File_Path)
                Dict_keys = GetSources().keys()
                # 这里 solame 的GetSources不能直接取到key，需要转换一下key
                Dict_keys = str(Dict_keys)
                p1 = re.compile(r'[[](.*?)[]]', re.S)
                Dict_keys = re.findall(p1, Dict_keys)
                Dict_keys = Dict_keys[0]
                Dict_keys = eval(Dict_keys.replace(')(', '),('))
                facefirest = GetSources()[Dict_keys]
                UpdatePipeline()
                obj = facefirest.SMProxy.GetClientSideObject()
                block = obj.GetOutputDataObject(0)
                NM_Cells = block.GetNumberOfCells()
                list_afterPoint = []
                list_pointIdAll = []  # 所有单元构成的线
                for L in range(NM_Cells):
                    Cell_Point_NM = block.GetCellType(L)
                    while Cell_Point_NM == 5:
                        This_Cell = block.GetCell(L)
                        list_PointId = []
                        for T in range(Cell_Point_NM - 2):
                            pointID = This_Cell.GetPointId(T)
                            list_PointId.append(pointID)
                        list_PointId.sort()
                        list_PointId = list(itertools.combinations(list_PointId, 2))
                        for R in range(3):
                            list_pointIdAll.append(list_PointId[R])
                        break
                # 将没有重复的点加入到list_afterPoint中
                list_afterPoint = [item for item, count in collections.Counter(list_pointIdAll).items() if count == 1]
                RFace_write_path.write(
                    "LINES" + " " + str(len(list_afterPoint)) + " " + str(len(list_afterPoint) * 3) + "\n")
                for Q in range(len(list_afterPoint)):
                    Write_line = str(list_afterPoint[Q])
                    Write_line = Write_line.replace("L", '').replace("(", "").replace(")", "").replace(",", "")
                    RFace_write_path.write("2 " + Write_line + "\n")
                Delete()
                RFace_write_path.close()
                Read_file = open(Read_RFace_Path, "r")
                data_Wire = Read_file.read()
                Read_file.close()
                with open(list_load_path[3] + SystemSlash + "Wire_" + str(i + 1) + ".vtk", "w") as R_Wire_file:
                    data_Wire = re.sub("POLYGONS[  \d\n]+", "", data_Wire)
                    R_Wire_file.write(data_Wire)
                    R_Face_file.close()

                face_vtk = LegacyVTKReader(FileNames=Read_RFace_Path)
                # 使其表面光滑
                generateSurfaceNormals1 = GenerateSurfaceNormals(Input=face_vtk)
                # 同时转换.stl文件
                Dict_keys = GetSources().keys()
                # 这里solame的GetSources不能直接取到key，需要转换一下key
                Dict_keys = str(Dict_keys)
                p1 = re.compile(r'[[](.*?)[]]', re.S)
                Dict_keys = re.findall(p1, Dict_keys)
                Dict_keys = Dict_keys[0]
                Dict_keys = eval(Dict_keys.replace(')(', '),('))
                facefirest = GetSources()[Dict_keys[0]]
                UpdatePipeline()
                obj = facefirest.SMProxy.GetClientSideObject()
                block = obj.GetOutputDataObject(0)
                NM_Cells = block.GetNumberOfCells()
                Face_File_stl.write('solid ' + 'Face_' + str(i + 1) + '\n')
                # 遍历vtk中所有的cell，并取每个cell的3个点
                for L in range(NM_Cells):
                    Cell_Point_NM = block.GetCellType(L)
                    while Cell_Point_NM == 5:
                        Face_File_stl.write(' facet normal 0 0 0' + '\n')
                        Face_File_stl.write('  outer loop' + '\n')
                        This_Cell = block.GetCell(L)
                        for T in range(Cell_Point_NM - 2):
                            pointID = This_Cell.GetPointId(T)
                            pointCon = block.GetPoint(pointID)
                            W_Line = str(pointCon)
                            W_Line = W_Line.replace("(", " ").replace(")", " ").replace(",", " ")  # 去除列表中的小括号和逗号
                            Face_File_stl.write('   vertex ' + W_Line + '\n')
                        Face_File_stl.write('  endloop' + '\n')
                        Face_File_stl.write(' endfacet' + '\n')
                        break
                Face_File_stl.write('endsolid' + '\n')
                # 转换.vtm
                Load_File_Path = list_load_path[5] + SystemSlash + "Face_" + str(i + 1) + ".vtp"
                # 将相关信息写入.vtm中
                Write_file = 'face' + SystemSlash + 'Face_' + str(i + 1) + '.vtp'
                file_vtm.write('      <DataSet index="' + str(i) + '"' + ' name="' + 'Face_' + str(
                    i + 1) + '" file="' + Write_file + '">' + '\n')
                file_vtm.write('      </DataSet>' + '\n')
                SaveData(Load_File_Path, proxy=generateSurfaceNormals1)
                Delete()
                Delete(face_vtk)
            file_vtm.write('    </Block>' + '\n')
            file_vtm.write('    <Block index="1" name="Wires">' + '\n')
            for i in range(NM_files):
                wire_vtk = LegacyVTKReader(FileNames=Read_Wire_Path)
                # 转换.vtm
                Load_File_Path = list_load_path[6] + SystemSlash + "Wire_" + str(i + 1) + ".vtp"
                Write_file = 'wire' + SystemSlash + 'Wire_' + str(i + 1) + '.vtp'
                file_vtm.write('      <DataSet index="' + str(i) + '"' + ' name="' + 'Wire_' + str(
                    i + 1) + '" file="' + Write_file + '">' + '\n')
                file_vtm.write('      </DataSet>' + '\n')
                SaveData(Load_File_Path, proxy=wire_vtk)
                Delete()

            file_vtm.write('    </Block>' + '\n')
            file_vtm.write('  </vtkMultiBlockDataSet>' + '\n')
            file_vtm.write('</VTKFile>' + '\n')
            print("rewrite face successful")
            print("rewrite wire successful")

            res_json = {"faceNumber": NM_files}
            print("result json|{}".format(json.dumps(res_json)))
            Face_File_stl.close()
        except Exception:
            print("Error:conversion died")
            return None
        del SystemSlash, list_load_path
        return Flag_json


if __name__ == '__main__':
    Input_path = sys.argv[1]
    Output_pathfile = sys.argv[2]
    Output_STLpathfile = sys.argv[3]

    start_con = ConversionCad(Input_path, Output_pathfile, Output_STLpathfile)
    Number_block = start_con.start_convtk()
    print("all conversion successful")
    print(Number_block)