# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: OFDictParser.py
@time: 2019/5/29 上午9:48 
"""

import codecs
import copy
from collections import deque
from pathlib import Path
from typing import Dict, Iterable, List

from constants.maps import OPENFOAM_CLASSES

HEADER_DICT = {
    "FoamFile": {
        "version": "2.0",
        "format": "ascii",
        "class": "dictionary",
        "object": "meshDict"
    }
}


class Stack(object):

    def __init__(self, init_value=None):
        if init_value is None:
            self._stack = deque()
        else:
            self._stack = deque(init_value)

    def __len__(self):
        return len(self._stack)

    def push(self, item):
        self._stack.append(item)

    def pop(self):
        return self._stack.pop()

    def empty(self):
        self._stack.clear()

    def top(self):
        if self.is_empty():
            return None
        return self._stack[-1]

    def is_empty(self):
        return len(self._stack) <= 0


class OFDictParse(object):

    def __init__(self, fdict_path):
        self.fdict = fdict_path
        self.fdict_name = str(Path(fdict_path).name)
        self.ofclass = OPENFOAM_CLASSES[self.fdict_name]
        self._dict_sign_stack = Stack()
        self._indent = " " * 4
        self._data = ""

    @classmethod
    def _is_iterable(cls, obj):
        return isinstance(obj, Iterable)

    @classmethod
    def _is_list(cls, obj):
        return isinstance(obj, List)

    @classmethod
    def _is_dict(cls, obj):
        return isinstance(obj, Dict)

    def hard_render(self, config_data: Dict):
        """
        硬渲染 依赖程序对配置文件进行写入
        :param config_data: 渲染参数
        :return:
        """
        self._header_render()
        self._structure_render(config_data)
        return self._data

    def _structure_render(self, config_data: Dict, depth=0):
        for key in config_data:
            if self._is_dict(config_data[key]):
                if "|" in key:
                    key_str = depth * self._indent + f"\"{key}\"" + "\n" + depth * self._indent + "{\n"
                else:
                    key_str = depth * self._indent + key + "\n" + depth * self._indent + "{\n"
                self._dict_sign_stack.push(depth * self._indent + "}\n")
                self._data += key_str
                self._structure_render(config_data[key], depth+1)
                self._data += self._dict_sign_stack.pop()
            elif self._is_list(config_data[key]):
                # TODO 暂时不用实现list
                pass
            elif isinstance(config_data[key], str) or \
                    isinstance(config_data[key], int) or \
                    isinstance(config_data[key], float):
                line = self._indent * depth + key + self._indent + str(config_data[key]) + ";\n"
                self._data += line
            else:
                # TODO 得到的数据是无效的 做处理
                pass

    def write_config(self):
        with codecs.open(self.fdict_name, mode="w", encoding="utf-8") as fdict_obj:
            fdict_obj.write(self._data)

    def merge_config(self, up_data, down_data):
        pass

    def temp_render(self, config_data, temp_file):
        # 模板渲染
        """
        :param config_data:
        :param temp_file:
        :return:
        """
        pass

    def _header_render(self):
        header_dict = copy.deepcopy(HEADER_DICT)
        header_dict["FoamFile"]["class"] = self.ofclass
        self._structure_render(header_dict)
        return self._data


if __name__ == '__main__':
    mesh_dict = OFDictParse("meshDict")
    d = {"假装配置文件1": {"假装配|置文件2": {"inc1": 1, "inc2": 0.22}, "假装配置文件3": "dododo"}}
    print(mesh_dict.hard_render(d))
    mesh_dict.write_config()
