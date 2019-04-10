# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: of2su2_mesh.py
@time: 2019/4/4 上午10:00 
"""
import codecs
import gc
import re
from pathlib import Path
from typing import List, Match

from config.config import PLOYMESH_FILES

"""
Description:
将openfoam的 constant/polyMesh 下的网格文件转换为su2的网格文件

原文档翻译:
输入文件应该包含以下内容:
第一行: openfoam的网格文件的后缀应该是以polymesh结尾, 且应该是一个绝对路径
第二行: 输出文件应该是以 .su2 结尾, 且应该是一个绝对路径
第三行: "2D" or "3D" 填写2D或者3D网格
第四行: 如果选择的是2D, 就必须要移除一个轴, 选填X, Y, Z 大写字母, 3D就空置
"""

import sys


# =================
# Various functions
# =================

def SkipFirstLines(listLines):
    i = 0
    while (i < len(listLines)) and (listLines[i][0:2] != "//"):
        i = i + 1
    i = i + 1
    #    while (i < len(listLines)) and (len(listLines[i]) < 2):
    while (i < len(listLines)) and (listLines[i].replace(" ", "") == ""):
        i = i + 1
    return i


def check_count(sline: str):
    if not re.match("\d{2,}", sline):
        """
        判定是否在首行
        :param sline 文件的每一行
        """
        return True
    return False


def PointIsInList(PointIndex, listPoints):
    PtInsideList = False
    for i in range(len(listPoints)):
        if (PointIndex == listPoints[i]):
            PtInsideList = True
    return PtInsideList


def point_in_list(point, points: list):
    """
    校验某个点点是否在点的列表里面
    :param points:
    :param point: 某个点
    :param
    :return: 判断是否在里面
    """
    return point in points


def HaveCommonPoints(listPoints_1, listPoints_2):
    haveCommonPts = False
    i = 0
    while (i < len(listPoints_1)) and (haveCommonPts == False):
        j = 0
        while (j < len(listPoints_2)) and (haveCommonPts == False):
            if (listPoints_1[i] == listPoints_2[j]):
                haveCommonPts = True
            j = j + 1
        i = i + 1
    return haveCommonPts


def points_is_crossed(points1, points2):
    """
    是否含有共同的点 点集1和点集2
    :return:
    """
    for sp1 in points1:
        for sp2 in points2:
            if sp1 == sp2:
                return True
    return False


def CommonPoints(listPoints1, listPoints2):
    listCommonPoints = []
    for i in range(len(listPoints1)):
        if (PointIsInList(listPoints1[i], listPoints2) == True):
            listCommonPoints.append(listPoints1[i])
    return listCommonPoints


def ask_common_points(points1, points2):
    """
    求两个点集中的公共元素
    :param points1:
    :param points2:
    :return:
    """
    spoints1 = set(points1)
    spoints2 = set(points2)
    return list(spoints1.intersection(spoints2))


def ScalarProduct(Vect_1_point_1, Vect_1_point_2, Vect_2_point_1, Vect_2_point_2):
    # TODO 求两个向量的数量积
    dimVect = len(Vect_1_point_1)
    Vect_1 = []
    for i in range(dimVect):
        Vect_1.append(Vect_1_point_2[i] - Vect_1_point_1[i])
    Vect_2 = []
    for i in range(dimVect):
        Vect_2.append(Vect_2_point_2[i] - Vect_2_point_1[i])
    valScalarProduct = 0.0
    for i in range(dimVect):
        valScalarProduct = valScalarProduct + Vect_1[i] * Vect_2[i]
    return valScalarProduct


class OF2SU2Converter:

    def __init__(self, ployMesh_path, su2mesh_path, su2mesh_name, mesh_dimension):
        # TODO 需要完成另外的逻辑
        self.ployMesh_path = ployMesh_path

    """
    对应关系
    faces:
    第一个数字是代表总共有多少个face, 后面是一个大的元组
    元组内部有多个单独数据结构表示face 类似于"n(p1 p2 p3 p4)", 第一个数字代表n个点构成的一个 face, 跟一对括号,
    括号内部的数字代表的是点的编号, pn 与 points 文件的点的索引相对应
    PS: faces 文件中 "n(p1 p2 p3 p4)" 不一定在同一行, 还有可能会有空行
    
    points:
    本质也是一个元组, 第一个数字是总共有多少个点, 
    元组内部多个单独数据结构表示点, 类似于 "(x y z)", 代表 x, y, z 轴上的坐标  
    point的索引即faces文件中的pn所映射的点
    
    owner:
    owner文件索引是face(key, 面的编号), 对应的参数是cell(value, 单元编号), 表示一个面对应的cell是哪个cell
    即 第key个face对应第value个cell
    PS: owner 包含所有的face假定是m个face, 前面的n个face都是internal face, 剩下的一部分m-n是external face
    
    neighbour:
    neighbour 包含所有的internal face, 假定是n个与owner的前面n个对应
    索引文件是face(key, 面的编号), 参数是cell(value, 单元编号), 表示一个面对应的cell是哪个cell
    即 第key个face对应第value个cell
    
    boundary:
    
    """

    def _read_sfile(self, name):
        """
        读取数据文件并返回字符串
        """
        file_path = Path(self.ployMesh_path, name)
        with codecs.open(file_path, mode="r", encoding="utf-8") as f:
            return f.read()

    @classmethod
    def _match_counts(cls, s_data):
        """
        匹配总的计数
        :param s_data: 字符串数据
        :return:
        """
        count_pt = re.compile("^(\d{1,})[\r\n\s]*\(")
        return re.search(count_pt, s_data).group(1)

    @classmethod
    def _match_faces_points(cls, s_data):
        """
        匹配面和点的每一组匹配的数据
        :param s_data:
        :return:
        """
        pt = re.compile("^\d{1,2}[\s\r\n]*?\([\s\S]+?\)")
        shear = re.compile("\(|\)")

        for piece in re.finditer(pt, s_data):
            piece: str
            res: str = re.sub(shear, ' ', piece)
            yield res.split()

    @classmethod
    def _match_three_type(cls, s_data):
        """
        返回数据的整体
        :param s_data: 文件的字符串
        :return:
        """
        pt = "^\d{1,}[\s\r\n]*\([\s\S]*\)"
        return re.search(pt, s_data).group(0)

    def _faces_parse(self, name="faces"):
        """
        解析faces文件返回一个字典
        :param name:
        :return: dict
        {
            face_count : face的总的数目
            faces: face集合 []
            {
                ploygon: 几边形
                point_mapping: 对应点 tuple
            }
        }
        """
        sfaces = self._read_sfile(name)
        face_count = self._match_counts(sfaces)
        faces = []
        face_d = {
            "face_count": face_count,
            "faces": faces
        }
        for face in self._match_faces_points(sfaces):
            face: list
            faces.append({"polygon": face[0], "point_mapping": tuple([int(p) for p in face[1:]])})
        del sfaces  # 回收字符串
        gc.collect()
        return face_d

    def _points_parse(self, name="points"):
        """解析点文件
        :param name: 网格文件
        :return: dict
        {
            point_count: 点的总数目
            points: point的集合, 列表
            (x, y, z) 坐标
        }
        """
        spoints = self._read_sfile(name)
        point_count = self._match_counts(spoints)
        points = []
        points_d = {
            "point_count": point_count,
            "points": points
        }
        for point in self._match_faces_points(spoints):
            point: list
            points.append(tuple(point))
        del spoints
        gc.collect()
        return points_d

    def _owner_parse(self, name="owner"):
        """
        解析owner文件, 并将cell存储为一个二维矩阵
        :param name: 文件名称
        :return:
        {
            cells_infos: list  包含 "nPoints", "nCells", "nFaces", "nInternalFaces"
            cells_matrix: cell的二维矩阵
        }
        """
        # 匹配cell的信息
        sowner = self._read_sfile(name)
        cells_infos = ["nPoints", "nCells", "nFaces", "nInternalFaces"]
        cell_dinfo = {}
        for face_key in cells_infos:
            cell_dinfo[face_key] = int(re.search(f"{face_key}:\s+?(\d+)[\s\"]", sowner).group(1))

        cells_matrix = []
        for i in cell_dinfo["nCells"]:
            cells_matrix.append([])

        cells_list = re.search("\([\s\r\n]*[\s\S]+?\)", sowner).group(0)[1:-1].split()
        del sowner
        gc.collect()
        for f_index, cell in enumerate(cells_list):
            cells_matrix[cell].append(f_index)

        del cells_list
        gc.collect()
        cells = {"cell_dinfo": cell_dinfo, "cells_matrix": cells_matrix}
        return cells

    def _neighbour_parse(self, name="neighbour"):

        """
        解析neighbour文件
        :param name: 文件名
        :return:
        {
            "if_count": int internal face的数量
            "ncells": list cell的列表
        }
        """

        sneigh = self._read_sfile(name)
        if_count = self._match_counts(sneigh)
        # ic_count internal cell

        ncells = re.search("^\([\s\r\n]*(\d[\s\n\r]*?)+?\)", sneigh).group(0)[1:-1].split()
        cell_d = {"if_count": if_count, "ncells": ncells}
        return cell_d

    def _boundary_parse(self, name="boundary"):
        """
        解析bounary文件
        :param name:  文件名
        :return:
        {
            "bound_count": 边界条件的数量
            "boundaries": list[dict] 边界条件的列表
            属性可以通过dicr访问, 名字为bound_name
        }
        """
        sbound = self._read_sfile(name)
        bound_count = self._match_counts(sbound)
        sbound = re.search("\([\s\r\n]*[\s\S]+?\)", sbound).group(0)[1:-1]
        bounds = re.finditer("[A-z]+[\s\r\n]*?\{[\s\S]+?\}", sbound)
        l_bounds = []
        # boundary list
        for bound in bounds:
            lines = bound.group().split(sep="\r")
            bound_name = lines[0].strip()
            lines = lines[2:-1]
            sind_bound = {"bound_name": bound_name}
            # single_dict_boundary
            for line in lines:
                l_value, r_value = line.split()
                r_value = re.sub(";", "", r_value)
                sind_bound[l_value] = r_value
            l_bounds.append(sind_bound)
        return {
            "bound_count": bound_count,
            "boundaries": l_bounds
        }

    def _fill_face(self, owner_info, neighbour_info):
        cells_matrix: List[List] = owner_info["cells_matrix"]
        ncells: List = neighbour_info["ncells"]
        for iface, cell in enumerate(ncells):
            cells_matrix[cell].append(iface)
        return owner_info

    def ploymesh_read(self):
        # TODO: 实现多进程
        faces_info = self._faces_parse()
        points_info = self._points_parse()
        owner_info = self._owner_parse()
        neighbour_info = self._neighbour_parse()
        boundary_info = self._boundary_parse()

        cell_info = self._fill_face(owner_info, neighbour_info)
        del owner_info
        del neighbour_info
        gc.collect()
        return {
            "faces_info": faces_info,
            "points_info": points_info,
            "cell_info": cell_info,
            "boundary_info": boundary_info
        }

    def covert(self):
        of_minfo = self.ploymesh_read()


# =========================
# Reading of the input file
# =========================
nameFile = "path"
listLinesInput = []
try:
    InputFile = open(nameFile, 'r')
    for line in InputFile:
        listLinesInput.append(line[0:-1])
    InputFile.close()
    pathOpenFoamMesh = listLinesInput[0]
    pathSU2Mesh = listLinesInput[1]
    nameOutputFile = listLinesInput[2]
    kindMesh = listLinesInput[3]
    dimMesh = int(kindMesh[0])
    if (dimMesh == 2):
        axisProjection = listLinesInput[4][0]
    listLinesInput = []
    print
    "pathOpenFoamMesh =", pathOpenFoamMesh
    print
    "pathSU2Mesh      =", pathSU2Mesh
    print
    "nameSU2MeshFile  =", nameOutputFile
    print
    "kindMesh (2D/3D) =", kindMesh
    if (dimMesh == 2):
        print
        "axisProjection   =", axisProjection
    print
    "Input file read correctly\n"
except:
    print
    "Problem during the input file reading (InputOpenFoam2SU2.dat)"
    exit(1)

# ==================================
# Reading of the OpenFoam mesh files
# ==================================
#
# 1) "points" file
#
listLinesPointsFile = []
listPoints = []
dimRef = 3
try:
    print
    "Reading of the 'points' file"
    pathAndFileName = pathOpenFoamMesh
    if pathAndFileName[-1] != "/":
        pathAndFileName = pathAndFileName + "/"
    pathAndFileName = pathAndFileName + "points"
    PointsFile = open(pathAndFileName, 'r')
    for line in PointsFile:
        listLinesPointsFile.append(line[0:-1])
    PointsFile.close()
    # The first lines are skipped
    i = SkipFirstLines(listLinesPointsFile)
    # Reading of the number of points
    nb_points = int(listLinesPointsFile[i])
    print
    "nb points = ", nb_points
    i = i + 1
    # Reading of points coordinates
    for j in range(nb_points):
        i = i + 1
        strTemp = listLinesPointsFile[i].replace("(", "")
        strTemp = strTemp.replace(")", "")
        listStrPoint = strTemp.split(" ", dimRef)
        listCoordPoint = []
        for k in range(dimRef):
            listCoordPoint.append(float(listStrPoint[k]))
        listPoints.append(listCoordPoint)
    listLinesPointsFile = []
    print
    "'points' file read correctly\n"
except:
    print
    "Problem during the 'points' file reading"
    exit(1)

#
# 2) "faces" file
#
listLinesFacesFile = []
listFaces = []
try:
    print
    "Reading of the 'faces' file"
    pathAndFileName = pathAndFileName.replace("points", "faces")
    FacesFile = open(pathAndFileName, 'r')
    for line in FacesFile:
        listLinesFacesFile.append(line[0:-1])
    FacesFile.close()
    # The first lines are skipped
    i = SkipFirstLines(listLinesFacesFile)
    # Reading of the number of faces
    nb_faces = int(listLinesFacesFile[i])
    print
    "nb faces = ", nb_faces
    i = i + 1
    # Reading of faces
    for j in range(nb_faces):
        i = i + 1
        k1 = listLinesFacesFile[i].find("(")
        k2 = listLinesFacesFile[i].find(")")
        n = int(listLinesFacesFile[i][0:k1])
        strTemp = listLinesFacesFile[i][k1 + 1:k2]
        listStrPoints = strTemp.split(" ", n)
        listPointsFace = []
        for k in range(n):
            listPointsFace.append(int(listStrPoints[k]))
        listFaces.append(listPointsFace)
    listLinesFacesFile = []
    print
    "'faces' file read correctly\n"
except:
    print
    "Problem during the 'faces' file reading"
    exit(1)

#
# 3) "owner" file
#
listLinesOwnerFile = []
try:
    print
    "Reading of the 'owner' file"
    pathAndFileName = pathAndFileName.replace("faces", "owner")
    OwnerFile = open(pathAndFileName, 'r')
    for line in OwnerFile:
        listLinesOwnerFile.append(line[0:-1])
    OwnerFile.close()
    # Reads the number of cells and internal faces
    i = 0
    while (listLinesOwnerFile[i].__contains__("nCells") == False):
        i = i + 1
    k1 = listLinesOwnerFile[i].find("nCells") + 6
    while (listLinesOwnerFile[i][k1 + 1] == " "):
        k1 = k1 + 1
    k2 = listLinesOwnerFile[i].find(" ", k1 + 1)
    nb_cells = int(listLinesOwnerFile[i][k1 + 1:k2])
    print
    "nb cells =", nb_cells
    k1 = listLinesOwnerFile[i].find("nInternalFaces") + 14
    while (listLinesOwnerFile[i][k1 + 1] == " "):
        k1 = k1 + 1
    k2 = listLinesOwnerFile[i].find('"', k1 + 1)
    nb_internal_faces = int(listLinesOwnerFile[i][k1 + 1:k2])
    print
    "nb internal faces =", nb_internal_faces
    # The first lines are skipped
    i = SkipFirstLines(listLinesOwnerFile)
    i = i + 1
    # Initialize the list of cells
    listCells = []
    for n in range(nb_cells):
        listCells.append([])
    # Reading of owners(listCells[n] contains the internal faces numbers)
    for j in range(nb_faces):
        i = i + 1
        n = int(listLinesOwnerFile[i])
        listCells[n].append(j)
    listLinesOwnerFile = []
    print
    "'owner' file read correctly\n"
except:
    print
    "Problem during the 'owner' file reading"
    exit(1)

#
# 4) "neighbour" file
#
listLinesNeighbourFile = []
try:
    print
    "Reading of the 'neighbour' file"
    pathAndFileName = pathAndFileName.replace("owner", "neighbour")
    NeighbourFile = open(pathAndFileName, 'r')
    for line in NeighbourFile:
        listLinesNeighbourFile.append(line[0:-1])
    NeighbourFile.close()
    # The first lines are skipped
    i = SkipFirstLines(listLinesNeighbourFile)
    i = i + 1
    # Reading of the neighbour cells (only for internal faces)
    # We remind that the external faces are ranked after the internal faces
    for j in range(nb_internal_faces):
        i = i + 1
        n = int(listLinesNeighbourFile[i])
        listCells[n].append(j)
    listLinesNeighbourFile = []
    print
    "'neighbour' file read correctly\n"
except:
    print
    "Problem during the 'neighbour' file reading"
    exit(1)

#
# 5) "boundary" file
#
listLinesBoundaryFile = []
listBoundaries = {}
try:
    print
    "Reading of the 'boundary' file"
    pathAndFileName = pathAndFileName.replace("neighbour", "boundary")
    BoundaryFile = open(pathAndFileName, 'r')
    for line in BoundaryFile:
        listLinesBoundaryFile.append(line[0:-1])
    BoundaryFile.close()
    # The first lines are skipped
    i = SkipFirstLines(listLinesBoundaryFile)
    nb_boundaries = int(listLinesBoundaryFile[i])
    print
    "nb boundaries =", nb_boundaries
    i = i + 1
    while (listLinesBoundaryFile[i][0] != ")"):
        i = i + 1
        if (listLinesBoundaryFile[i + 1].__contains__("{") == True):
            nameBoundary = listLinesBoundaryFile[i].replace(" ", "")
            listBoundaries[nameBoundary] = [0, 0, ""]
        if (listLinesBoundaryFile[i].__contains__("nFaces") == True):
            k1 = listLinesBoundaryFile[i].find("nFaces") + 6
            k2 = listLinesBoundaryFile[i].find(";")
            nFacesBoundary = int(listLinesBoundaryFile[i][k1 + 1:k2].replace(" ", ""))
            listBoundaries[nameBoundary][1] = nFacesBoundary
        if (listLinesBoundaryFile[i].__contains__("startFace") == True):
            k1 = listLinesBoundaryFile[i].find("startFace") + 9
            k2 = listLinesBoundaryFile[i].find(";")
            nFirstFace = int(listLinesBoundaryFile[i][k1 + 1:k2].replace(" ", ""))
            listBoundaries[nameBoundary][0] = nFirstFace
        if (listLinesBoundaryFile[i].__contains__("type") == True):
            k1 = listLinesBoundaryFile[i].find("type") + 4
            k2 = listLinesBoundaryFile[i].find(";")
            typeBoundary = listLinesBoundaryFile[i][k1 + 1:k2].replace(" ", "")
            listBoundaries[nameBoundary][2] = typeBoundary
    listLinesBoundaryFile = []
    print
    "Boundaries =", listBoundaries
    print
    "'boundary' file read correctly\n"
except:
    print
    "Problem during the 'boundary' file reading"
    exit(1)

# ====================================================================
# Creation of the cells table (with the points contained in each cell)
# ====================================================================
#
# The cell format is given in http://adl.stanford.edu/docs/display/SUSQUARED/Mesh+files
# and in http://www.vtk.org/VTK/img/file-formats.pdf page
# (both are necessary)
#

try:
    print
    "Beginning of the format conversion process"
    # Initialization
    # Gives the correspondances "nb points in element" => "VTK format number associated"

    # SU2里面的类型定义
    listKind1DElements = {2: 3}  # Segments
    listKind2DElements = {3: 5, 4: 9}  # Triangles and quads
    listKind3DElements = {4: 10, 5: 14, 6: 13, 8: 12}  # Tetras, pyramids, prisms and hexas
    listKindElements = {"1D": listKind1DElements, "2D": listKind2DElements, "3D": listKind3DElements}

    # cell的点矩阵
    listCellsPoints = []
    for i in range(nb_cells):
        listCellsPoints.append([])

    # Filling of the list
    q = 1
    for i in range(nb_cells):
        if (i == q * nb_cells / 10):
            # 就是只是想计数看弄到百分之几了
            print
            "Conversion progress:", 10 * q, "% done"
            q = q + 1
        if (len(listCells[i]) == 6):
            # 如果是六面体的时候
            # Hexaedron cell
            # To get all the points, two opposite faces are selected
            j_indices = [0, 1]
            while (j_indices[1] < len(listCells[i])) and (
                    HaveCommonPoints(listFaces[listCells[i][j_indices[0]]], listFaces[listCells[i][j_indices[1]]])):
                    # 当j_indices[1] 是小于这个六面体的面数的时候
                    # 遍历第i个cell的所有面
                    # 且这个cell的第零个面和另外的几个面都没有共同的点的时候
                j_indices[1] = j_indices[1] + 1
            # The two series of points from the two faces must be ordered (see VTK format)
            listLateralFacesOrdered = []
            j0 = 1
            if (j_indices[1] == j0):
                j0 = 2
            p = 0
            listLateralFacesOrdered.append(j0)
            nb_lateral_faces = 4
            while (len(listLateralFacesOrdered) < nb_lateral_faces):
                for j in range(2, len(listCells[i])):
                    if (PointIsInList(j, listLateralFacesOrdered) == False) and (j != j_indices[1]):
                        if (HaveCommonPoints(listFaces[listCells[i][j]],
                                             listFaces[listCells[i][listLateralFacesOrdered[p]]]) == True):
                            listLateralFacesOrdered.append(j)
                            p = p + 1
            for num_face in range(2):
                for num_lateral_face in range(nb_lateral_faces):
                    num_point = 0
                    while (num_point < nb_lateral_faces) \
                            and ((PointIsInList(listFaces[listCells[i][j_indices[num_face]]][num_point], listFaces[
                        listCells[i][listLateralFacesOrdered[num_lateral_face]]]) == False) \
                                 or (PointIsInList(listFaces[listCells[i][j_indices[num_face]]][num_point], listFaces[
                                listCells[i][listLateralFacesOrdered[num_lateral_face - 1]]]) == False)):
                        num_point = num_point + 1
                    listCellsPoints[i].append(listFaces[listCells[i][j_indices[num_face]]][num_point])
        elif (len(listCells[i]) == 5):
            # Pyramid or prism cell
            isPrism = True
            nb_triangles = 0
            for n in range(5):
                if (len(listFaces[listCells[i][n]]) == 3):
                    nb_triangles = nb_triangles + 1
            if (nb_triangles == 2):
                # Prism cell
                # To get all the points, the two triangle faces are selected
                j_indices = [0, 0]
                n = 0
                for j in range(2):
                    while (n < 5) and (len(listFaces[listCells[i][n]]) != 3):
                        n = n + 1
                    j_indices[j] = n
                    n = n + 1
                # The two series of points from the two faces must be ordered (see VTK format)
                listLateralFacesOrdered = []
                j0 = 0
                while (j_indices[0] == j0) or (j_indices[1] == j0):
                    j0 = j0 + 1
                p = 0
                #  TODO 这里存在异常跳出的问题
                listLateralFacesOrdered.append(j0)
                nb_lateral_faces = 3
                while (len(listLateralFacesOrdered) < nb_lateral_faces):
                    for j in range(1, len(listCells[i])):
                        if (PointIsInList(j, listLateralFacesOrdered) == False) and (j != j_indices[0]) and (
                                j != j_indices[1]):
                            if (HaveCommonPoints(listFaces[listCells[i][j]],
                                                 listFaces[listCells[i][listLateralFacesOrdered[p]]]) == True):
                                listLateralFacesOrdered.append(j)
                                p = p + 1
                for num_face in range(2):
                    for num_lateral_face in range(nb_lateral_faces):
                        num_point = 0
                        while (num_point < nb_lateral_faces) \
                                and ((PointIsInList(listFaces[listCells[i][j_indices[num_face]]][num_point], listFaces[
                            listCells[i][listLateralFacesOrdered[num_lateral_face]]]) == False) \
                                     or (PointIsInList(listFaces[listCells[i][j_indices[num_face]]][num_point],
                                                       listFaces[listCells[i][
                                                           listLateralFacesOrdered[num_lateral_face - 1]]]) == False)):
                            num_point = num_point + 1
                        listCellsPoints[i].append(listFaces[listCells[i][j_indices[num_face]]][num_point])
            else:
                # Pyramid cell
                # To get all the points, the square face is selected, and then the last point is added
                j_indices = [0]
                n = 0
                for j in range(1):
                    while (n < 5) and (len(listFaces[listCells[i][n]]) != 4):
                        n = n + 1
                    j_indices[j] = n
                # The serie of points from the square face must be ordered (see VTK format)
                listLateralFacesOrdered = []
                j0 = 0
                while (j_indices[0] == j0):
                    j0 = j0 + 1
                p = 0
                listLateralFacesOrdered.append(j0)
                nb_lateral_faces = 4
                while (len(listLateralFacesOrdered) < nb_lateral_faces):
                    for j in range(1, len(listCells[i])):
                        if (PointIsInList(j, listLateralFacesOrdered) == False) and (j != j_indices[0]):
                            if (len(CommonPoints(listFaces[listCells[i][j]],
                                                 listFaces[listCells[i][listLateralFacesOrdered[p]]])) == 2):
                                listLateralFacesOrdered.append(j)
                                p = p + 1
                # Points from the square
                for num_face in range(1):
                    for num_lateral_face in range(nb_lateral_faces):
                        num_point = 0
                        while (num_point < nb_lateral_faces) \
                                and ((PointIsInList(listFaces[listCells[i][j_indices[num_face]]][num_point], listFaces[
                            listCells[i][listLateralFacesOrdered[num_lateral_face]]]) == False) \
                                     or (PointIsInList(listFaces[listCells[i][j_indices[num_face]]][num_point],
                                                       listFaces[listCells[i][
                                                           listLateralFacesOrdered[num_lateral_face - 1]]]) == False)):
                            num_point = num_point + 1
                        listCellsPoints[i].append(listFaces[listCells[i][j_indices[num_face]]][num_point])
                # Last point to add
                n = 0
                while (n < 3) and (PointIsInList(listFaces[listCells[i][listLateralFacesOrdered[0]]][n],
                                                 listCellsPoints[i]) == True):
                    n = n + 1
                listCellsPoints[i].append(listFaces[listCells[i][listLateralFacesOrdered[0]]][n])
        elif (len(listCells[i]) == 4):
            # Tetra cell
            # There is no specific order, so we select 2 triangles to get all the points
            j = 0
            for num_point in range(3):
                listCellsPoints[i].append(listFaces[listCells[i][j]][num_point])
            j = 1
            for num_point in range(3):
                if (PointIsInList(listFaces[listCells[i][j]][num_point], listCellsPoints[i]) == False):
                    listCellsPoints[i].append(listFaces[listCells[i][j]][num_point])
    print
    "Conversion progress: 100% done"

    if (kindMesh == "2D"):
        # If the mesh must be converted to 2D mesh, we must get only prisms or hexas
        # (the 3D mesh must have been obtained by extrusion)
        # Selection of the first point that will fix the value along the axis projection
        # All the points that have the same value will be kept
        print
        "Conversion to 2D mesh"
        if (axisProjection == "X"):
            nproj = 0
        elif (axisProjection == "Y"):
            nproj = 1
        else:
            nproj = 2
        valRef = listPoints[0][nproj]
        tolerance = 1.0 * 10.0 ** (-6)
        # Selection of points that will be kept
        listKeptPoints = []
        listCorrespondance = []
        p = 0
        for num_point in range(nb_points):
            if abs(listPoints[num_point][nproj] - valRef) < tolerance:
                listKeptPoints.append(num_point)
                listCorrespondance.append(p)
                p = p + 1
            else:
                listCorrespondance.append(0)
        print
        "listCorrespondance done"
        # Modification of the list of faces: only points that belong to the right plane are kept
        for num_face in range(nb_faces):
            listTemp = []
            for num_point in range(len(listFaces[num_face])):
                if abs(listPoints[listFaces[num_face][num_point]][nproj] - valRef) < tolerance:
                    listTemp.append(listCorrespondance[listFaces[num_face][num_point]])
            listFaces[num_face] = listTemp
        print
        "listFaces updated"
        # Removal of points indices inside the cells
        listKeptCells = []
        for num_cell in range(nb_cells):
            listTemp = []
            for num_point in range(len(listCellsPoints[num_cell])):
                if abs(listPoints[listCellsPoints[num_cell][num_point]][nproj] - valRef) < tolerance:
                    listTemp.append(listCorrespondance[listCellsPoints[num_cell][num_point]])
            if (len(listTemp) > 0):
                listKeptCells.append(num_cell)
                listCellsPoints[num_cell] = listTemp
        print
        "listCellsPoints updated"
        # Final lists (points and cells)
        listPtsTemp = []
        for i in range(len(listKeptPoints)):
            listPtsTemp.append([])
            for n in range(3):
                if (n != nproj):
                    listPtsTemp[-1].append(listPoints[listKeptPoints[i]][n])
        listPoints = listPtsTemp
        nb_points = len(listPoints)
        print
        "Final listPoints created"
        listCellsTemp = []
        for i in range(len(listKeptCells)):
            listCellsTemp.append(listCellsPoints[listKeptCells[i]])
        listCellsPoints = listCellsTemp
        nb_cells = len(listCellsPoints)
        # Reorders the points (only for quad cells)
        for i in range(nb_cells):
            if (len(listCellsPoints[i]) == 4):
                case = 1
                for j in range(-1, 1):
                    if (ScalarProduct(listPoints[listCellsPoints[i][j]], listPoints[listCellsPoints[i][j + 1]], \
                                      listPoints[listCellsPoints[i][j + 2]],
                                      listPoints[listCellsPoints[i][j + 3]]) > 0):
                        case = j
                if (case != 1):
                    indexTemp = listCellsPoints[i][case]
                    listCellsPoints[i][case] = listCellsPoints[i][case + 1]
                    listCellsPoints[i][case + 1] = indexTemp
        print
        "Final listCellsPoints created"
        # Deleting of the "empty" boundaries
        listSurfToDelete = []
        for key in listBoundaries.keys():
            if (listBoundaries[key][2] == "empty"):
                nb_boundaries = nb_boundaries - 1
                listSurfToDelete.append(key)
        for i in range(len(listSurfToDelete)):
            listBoundaries.__delitem__(listSurfToDelete[i])
        print
        "listBoundaries updated"
    print
    "Format conversion process ended with success!\n"
except:
    print
    "Problem during the format conversion process"
    exit(1)

# ==============================
# Writting of the .su2 mesh file
# ==============================
try:
    print
    "Beginning of the .su2 mesh file writting"
    pathAndFileName = pathSU2Mesh
    if (pathAndFileName[-1] != "/"):
        pathAndFileName = pathAndFileName + "/"
    pathAndFileName = pathAndFileName + nameOutputFile
    print
    "pathAndFileName =", pathAndFileName
    OutputFile = open(pathAndFileName, 'w')
    print
    "File opened"
    strTemp = "NDIME= " + str(dimMesh) + "\n"
    OutputFile.write(strTemp)
    strTemp = "NELEM= " + str(nb_cells) + "\n"
    OutputFile.write(strTemp)
    # Writting of cells (kind of cell, points indices that belong to the cell, and rank of the cell)
    for n in range(nb_cells):
        strPoints = "\t"
        for i in range(len(listCellsPoints[n])):
            strPoints = strPoints + str(listCellsPoints[n][i]) + "\t"
        strTemp = str(listKindElements[kindMesh][len(listCellsPoints[n])]) + strPoints + str(n) + "\n"
        OutputFile.write(strTemp)
    listCellsPoints = []
    # Writting of points (coordinates and rank)
    strTemp = "NPOIN= " + str(nb_points) + "\n"
    OutputFile.write(strTemp)
    for p in range(nb_points):
        strPoints = "\t"
        for i in range(dimMesh):
            strPoints = strPoints + str(listPoints[p][i]) + "\t"
        strTemp = strPoints + str(p) + "\n"
        OutputFile.write(strTemp)
    listPoints = []
    # Writting of domain boundaries
    strTemp = "NMARK= " + str(nb_boundaries) + "\n"
    OutputFile.write(strTemp)
    for key in listBoundaries.keys():
        strTemp = "MARKER_TAG= " + key + "\n"
        OutputFile.write(strTemp)
        nb_faces_in_boundary = 0
        for q in range(listBoundaries[key][0], listBoundaries[key][0] + listBoundaries[key][1]):
            if (len(listFaces[q]) > 0):
                nb_faces_in_boundary = nb_faces_in_boundary + 1
        strTemp = "MARKER_ELEMS= " + str(nb_faces_in_boundary) + "\n"
        OutputFile.write(strTemp)
        n = 0
        kindFace = str(int(kindMesh[0]) - 1) + "D"
        for q in range(listBoundaries[key][0], listBoundaries[key][0] + listBoundaries[key][1]):
            if (len(listFaces[q]) > 0):
                strTemp = str(listKindElements[kindFace][len(listFaces[q])]) + "\t"
                for i in range(len(listFaces[q])):
                    strTemp = strTemp + str(listFaces[q][i]) + "\t"
                strTemp = strTemp + str(n) + "\n"
                OutputFile.write(strTemp)
                n = n + 1
    OutputFile.close()
    print
    "The mesh file", nameOutputFile, "has been written correctly!\n"
    print
    "Now, you just have to hope it works! :o)\n"
except:
    OutputFile.close()
    print
    "Problem during the .su2 mesh file writting"
