##
## This file is generated automatically by SALOME v9.2.2 with dump python functionality
##
# -*- coding: UTF-8 -*-

'''''
脚本的流程为：使用salome打开.stp文件后，提取出里面的face，并保存至指定的文件夹
删除文件夹中face的lines数据，并保存至RFace文件夹中
重写RFace中每一个face的lines
将重写后face中的POLYGONS删除，保存为wire
将重写后的face进行转换为vtp，并生成一个vtm文件
将重写后的face的POLYGANG的数据删除，并保存为到wire文件夹中
同时生成一个stl文件
'''


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

def MakeFile(filepath):
    if os.path.exists(filepath):
        shutil.rmtree(filepath)
    os.makedirs(filepath)

WindowsSlash  = "\\"
LinuxSlash = "/"

Input_path = sys.argv[1]
Output_path = sys.argv[2]

if "/" in Input_path:
    SyetemSlash = LinuxSlash
else:
    SyetemSlash = WindowsSlash

try:
    (filepath, tempfilename) = os.path.split(Input_path)
    (filename, extension) = os.path.splitext(tempfilename)

    Load_File_File = Output_path + SyetemSlash + filename + "_VTK"
    MakeFile(Load_File_File)

    Load_Con_File = Output_path + SyetemSlash + filename
    MakeFile(Load_Con_File)

    Load_Vtk_face = Load_File_File + SyetemSlash + "Face"
    MakeFile(Load_Vtk_face)

    Load_Vtk_wire = Load_File_File + SyetemSlash + "Wire"
    MakeFile(Load_Vtk_wire)

    Load_Vtk_Rface = Load_File_File + SyetemSlash + "RFace"
    MakeFile(Load_Vtk_Rface)

    Load_Vtp_face = Load_Con_File + SyetemSlash + "face"
    MakeFile(Load_Vtp_face)

    Load_Vtp_wire = Load_Con_File + SyetemSlash + "wire"
    MakeFile(Load_Vtp_wire)

    print("creat storage directory successful")
except Exception:
    print("Error:creat storage directory failed")

salome.salome_init()
notebook = salome_notebook.NoteBook()
sys.path.insert(0, filepath)
###
### GEOM component
###
geompy = geomBuilder.New()
O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)

try:
    if ".stp" == extension:
        Input = geompy.ImportSTEP(Input_path, False, True)
    elif ".brep" == extension:
        Input = geompy.ImportBREP(Input_path)
    elif ".iges" == extension:
        Input = geompy.ImportIGES(Input_path)

    print("Identification file type successful")
except Exception:
    print("IOError: file type must be .stp .brep .iges")
    raise

faces = geompy.ExtractShapes(Input, geompy.ShapeType["FACE"], True)
face_time = 0
for index, face in enumerate(faces):
    face_time = face_time + 1
    LoadVTKFPath = Load_Vtk_face + SyetemSlash + "Face_%d" %face_time + ".vtk"
    geompy.ExportVTK(face, LoadVTKFPath, 0.0001)

print("conversion vtk successful")

Face_Path_file = Load_Vtk_face
Face_file_NM = os.listdir(Face_Path_file)
NM_files = len(Face_file_NM)
Other_file_path = Load_Vtk_Rface
try:
    # 删除vtk文件中的lines信息，将删除后的文件写进RFace文件夹中
    for i in range(NM_files):
        Read_Face_Path = Face_Path_file + SyetemSlash + "Face_" + str(i + 1) + ".vtk"
        print("rewrite face：{}".format(Read_Face_Path))
        Read_file = open(Read_Face_Path, "r")
        data_Face = Read_file.read()
        Read_file.close()
        with open(Other_file_path + SyetemSlash +"Face_" + str(i + 1) + ".vtk", "w") as R_Face_file:
            data_Face = re.sub("LINES[  \d\n]+", "", data_Face)
            R_Face_file.write(data_Face)
            R_Face_file.close()
        # 重写lines信息，并提出所有的cell的pointid构成lines
        RFace_write_path = open(Other_file_path + SyetemSlash + "Face_" + str(i + 1) + ".vtk", 'a')
        Read_File_Path = Other_file_path + SyetemSlash +"Face_" + str(i + 1) + ".vtk"
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
        list_pointIdAll = [] #所有单元构成的线
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
        RFace_write_path.write("LINES" + " " + str(len(list_afterPoint)) + " " + str(len(list_afterPoint) * 3) + "\n")
        for Q in range(len(list_afterPoint)):
            Write_line = str(list_afterPoint[Q])
            Write_line = Write_line.replace("L", '').replace("(", "").replace(")","").replace(",", "")
            RFace_write_path.write("2 " + Write_line + "\n")
        Delete()
        RFace_write_path.close()
    print("rewrite face successful")
except Exception:
    print("Error:rewrite face failed")
    raise

try:
    for i in range(NM_files):
        Read_RFace_Path = Other_file_path + SyetemSlash +"Face_" + str(i + 1) + ".vtk"
        Read_file = open(Read_RFace_Path, "r")
        data_Wire = Read_file.read()
        Read_file.close()
        with open(Load_Vtk_wire + SyetemSlash +"Wire_" + str(i + 1) + ".vtk", "w") as R_Wire_file:
            data_Wire = re.sub("POLYGONS[  \d\n]+", "", data_Wire)
            R_Wire_file.write(data_Wire)
            R_Face_file.close()
    print("write wire successful")
except Exception:
    print("Error:failed to write wire")
    raise

# 创建一个文件用于在转换成vtp格式的同时，存储一个.stl格式的文件
Face_stl_path = Load_Con_File + SyetemSlash + filename + ".stl"
Face_File_stl = open(Face_stl_path, 'a')

# 给出VTK格式文件路径
Face_Path_file = Load_Vtk_Rface
Face_File = os.listdir(Face_Path_file)
Num_files = len(Face_File)

# 创建一个文件，作为vtm
Face_VTM = Load_Con_File + SyetemSlash + "cad.vtm"
facefile_VTM = open(Face_VTM, 'a')
facefile_VTM.write('<VTKFile type="vtkMultiBlockDataSet" version="1.0" byte_order="LittleEndian" header_type="UInt64">' + '\n')
facefile_VTM.write('  <vtkMultiBlockDataSet>' + '\n')
facefile_VTM.write('    <Block index="0" name="face">' + '\n')

try:
    # 循环文件，将每一个vtk文件转为vtp，循环次数为文件个数
    for i in range(Num_files):
        Read_File_Path = Face_Path_file + SyetemSlash +"Face_" + str(i+1) + ".vtk"
        print("conviersion vtk:{}".format(Read_File_Path))
        face_vtk = LegacyVTKReader(FileNames=Read_File_Path)
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
                    W_Line = W_Line.replace("(", " " ).replace(")"," ").replace(",", " " )  # 去除列表中的小括号和逗号
                    Face_File_stl.write('   vertex ' + W_Line + '\n')
                Face_File_stl.write('  endloop' + '\n')
                Face_File_stl.write(' endfacet' + '\n')
                break
        Face_File_stl.write('endsolid' +'\n')
        # 转换.vtm
        Load_File_Path = Load_Vtp_face + SyetemSlash + "Face_" + str(i + 1) + ".vtp"
        # 将相关信息写入.vtm中
        Write_file = 'face' + SyetemSlash + 'Face_' + str(i+1) + '.vtp'
        facefile_VTM.write('      <DataSet index="' + str(i) + '"' +' name="' + 'Face_' + str(i+1) + '" file="' + Write_file +'">' + '\n')
        facefile_VTM.write('      </DataSet>' + '\n')
        SaveData(Load_File_Path, proxy=generateSurfaceNormals1)
        Delete()
        Delete(face_vtk)
    print("vtk face conversion vtp successful")
except Exception:
    print("Error:vtk face conversion vtp failed")
    raise

facefile_VTM.write('    </Block>' + '\n')
Face_File_stl.close()
print ("wirte stl successful")
facefile_VTM.close()

# 以下重复，将不同形式的vtk转为vtp

# 给出wire文件的VTK格式文件路径
Wire_Path_file = Load_Vtk_wire
Wire_File = os.listdir(Load_Vtk_wire)
Num_files = len(Wire_File)
res_json = {"faceNumber": 0}
#打开之间的vtm文件，并续写内容
wireVTM_file = Load_Con_File + SyetemSlash + "cad.vtm"
wirefile_VTM = open(wireVTM_file, 'a')
wirefile_VTM.write('    <Block index="1" name="Wires">' + '\n')
try:
    # 循环，将每一个vtk转为vtp
    for i in range(Num_files):
        # Wire_Path_file = Load_Vtk_wire
        Read_File_Path = Load_Vtk_wire + SyetemSlash + "Wire_" + str(i + 1) + ".vtk"
        wire_vtk = LegacyVTKReader(FileNames=Read_File_Path)
        # 转换.vtm
        Load_File_Path = Load_Vtp_wire + SyetemSlash + "Wire_" + str(i + 1) + ".vtp"
        Write_file = 'wire' + SyetemSlash + 'Wire_' + str(i + 1) + '.vtp'
        wirefile_VTM.write('      <DataSet index="' + str(i) + '"' + ' name="' + 'Wire_' + str(i+1) + '" file="' + Write_file +'">' + '\n')
        wirefile_VTM.write('      </DataSet>' + '\n')
        SaveData(Load_File_Path, proxy=wire_vtk)
        Delete()
        res_json["faceNumber"] = res_json["faceNumber"] + 1
    print("vtk wire conversion vtp successful")
except Exception:
    print("Error:vtk wire conversion vtp failed")
    raise

wirefile_VTM.write('    </Block>' + '\n')
wirefile_VTM.write('  </vtkMultiBlockDataSet>' + '\n')
wirefile_VTM.write('</VTKFile>' + '\n')
print("write vtm successful")
wirefile_VTM.close()
# RFace_write_path.close()
print("all conversion successful")
print("result json|{}".format(json.dumps(res_json)))
