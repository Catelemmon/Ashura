# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: sub_snipthumb.py
@time: 2019/5/16 上午10:15 
"""

from paraview.simple import *
import sys
import os

paraview.simple._DisableFirstRenderCameraReset()

input_file = sys.argv[1]
output_file = sys.argv[2]
input_file = os.path.abspath(input_file)
output_file = os.path.abspath(output_file)

# 读取文件
# src =  XMLMultiBlockDataReader(FileName=["/data/home/liuwei//Conpy/isshiki/isshiki.vtm"])
src = XMLMultiBlockDataReader(FileName=[input_file])

# 创建 'Render View'
renderView = CreateView('RenderView')

# 隐藏坐标轴
renderView.OrientationAxesVisibility = 0

# 设置背景颜色
renderView.Background = [1.0, 0.98, 0.98]

# 激活当前窗口
SetActiveView(renderView)

# 显示
display = Show(src, renderView)

# 显示颜色
# ColorBy(display, ('CELLS', 'vtkCompositeIndex'))
ColorBy(display, ('FIELD', 'vtkBlockColors'))

display.RescaleTransferFunctionToDataRange(True, False)
# display.SetScalarBarVisibility(renderView, True)

# 设置透明度
display.Opacity = 0.5

# 设置相机
camera = GetActiveCamera()
camera.Yaw(20)
camera.Roll(20)
renderView.ResetCamera()

# 激活当前source
SetActiveSource(src)


if os.path.exists(output_file):
    os.remove(output_file)

# 保存图片
# SaveScreenshot("/data/home/liuwei/SaveScreen/oooo.png", renderView, ImageResolution=[800, 600])
SaveScreenshot(output_file, renderView, ImageResolution=[720, 462])
Delete(src)
