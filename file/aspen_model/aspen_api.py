# -*- coding: utf-8 -*-
"""
Created on 2021/10/09 13:34:06

@File -> aspen_api_v2.0.py

@Author: luolei

@Email: dreisteine262@163.com

@Describe: 使用python调用ASPEN的模拟接口
"""

import win32com.client as win32
import numpy as np
import time
import sys
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), "../" * 3))
sys.path.append(BASE_DIR)


class PyASPENPlus(object):
    """使用Python运行ASPEN模拟"""

    def __init__(self):
        pass

    def init_app(self, ap_version: str = "11.0"):
        """开启ASPEN Plus

        :param ap_version: ASPEN Plus版本号, defaults to "11.0"
        """
        version_match = {
        "11.0": "37.0",
        "10.0": "36.0",
        "9.0": "35.0",
        "8.8": "34.0",
        }
        self.app = win32.Dispatch("Apwn.Document.{}".format(version_match[ap_version]))


    def load_ap_file(self, file_name: str, file_dir: str = None, visible: bool = False, dialogs: bool = False):
        """载入待运行的ASPEN文件"""
        # 文件类型检查.
        if file_name[-4:] != ".bkp":
            raise ValueError("not an ASPEN bkp file")
        
        self.file_dir = os.getcwd() if file_dir is None else file_dir  # ASPEN文件所处目录, 默认为当前目录

        self.app.InitFromArchive2(os.path.join(self.file_dir, file_name))
        self.app.Visible = 1 if visible else 0
        self.app.SuppressDialogs = 0 if dialogs else 1

        print("The ASPEN file \"%s\" has been reloaded" % file_name)

    def assign_node_values(self, nodes: list, values: list, call_address: dict):
        for i, node in enumerate(nodes):
            self.app.Tree.FindNode(call_address[node]).Value = values[i]

    def run_simulation(self, reinit: bool = True, sleep: float = 0.01):
        """进行模拟

        :param reinit: 是否重新初始化迭代参数设置, defaults to True
        :param sleep: 每次检测运行状态的间隔时长, defaults to 2.0
        """
        if reinit:
            self.app.Reinit()
        
        self.app.Engine.Run2()
        while self.app.Engine.IsRunning == 1:
            time.sleep(sleep)

    def get_target_values(self, target_nodes: list, call_address):
        """从模拟结果中获得目标值"""
        values = []
        for node in target_nodes:
            values.append(self.app.Tree.FindNode(call_address[node]).Value)
        return values

    def check_simulation_status(self):
        """检查模拟是否收敛等"""
        value = self.app.Tree.FindNode("\Data\Results Summary\Run-Status\Output\RUNID").Value
        file_path = self.file_dir + "\\" + value + ".his"

        with open(file_path,"r") as f: 
            isError = np.any(np.array([line.find("SEVERE ERROR") for line in f.readlines()])>=0)
        return [not isError]

    def quit_app(self):
        self.app.Quit()

    def close_app(self):
        self.app.Close()


if __name__ == "__main__":

    # ---- 接口和值 ---------------------------------------------------------------------------------

    x_cols = ["FEED_pressure", "FEED_ETHANOL", "FEED_ACETIC", "FEED_H2O"]
    y_cols = ["PRODUCT_ETHYL-01"]

    # 自行整理调用地址.
    # 调用地址查找方法参考：https://zhuanlan.zhihu.com/p/321125404
    call_address = {
        "FEED_pressure": "\Data\Streams\FEED\Input\PRES\MIXED",
        "FEED_ETHANOL": "\Data\Streams\FEED\Input\FLOW\MIXED\ETHANOL",
        "FEED_ACETIC": "\Data\Streams\FEED\Input\FLOW\MIXED\ACETIC",
        "FEED_H2O": "\Data\Streams\FEED\Input\FLOW\MIXED\H2O",

        "PRODUCT_ETHYL-01": "\Data\Streams\PRODUCT\Output\MOLEFLOW\MIXED\ETHYL-01",
    }

    x_range = {
        "FEED_pressure": [0.0500, 0.1500],
        "FEED_ETHANOL": [150.0, 240.0],
        "FEED_ACETIC": [150.0, 240.0],
        "FEED_H2O": [650.0, 800.0],

        "PRODUCT_ETHYL-01": None,
    }
    
    # ---- ASPEN 模拟 ------------------------------------------------------------------------------


    def random_x_values():
        x_values = []
        for i, x_col in enumerate(x_cols):
            x_values.append(np.random.uniform(*x_range[x_col]))
        return x_values


    # 指定ASPEN文件名和所处目录.
    file_name = "cstr.bkp"
    file_dir = os.getcwd()

    # 进行ASPEN模拟.
    pyaspen = PyASPENPlus()

    pyaspen.init_app()
    pyaspen.load_ap_file(file_name, file_dir)

    x_records, y_records, status_records = [], [], []
    repeats = 100
    for i in range(repeats):
        print("simulating %d" % i)

        # 随机给定一个参数值.
        x_values = random_x_values()

        pyaspen.assign_node_values(x_cols, x_values, call_address)
        pyaspen.run_simulation(reinit=False)

        y_values = pyaspen.get_target_values(y_cols, call_address)
        simul_status = pyaspen.check_simulation_status()

        x_records.append(x_values)
        y_records.append(y_values)
        status_records.append(simul_status)

    pyaspen.close_app()

    # ---- 获得结果 ---------------------------------------------------------------------------------

    x_records = np.array(x_records)
    y_records = np.array(y_records)
    status_records = np.array(status_records)
    
    np.save(os.path.join(BASE_DIR,"data/dataset/X.npy"), x_records)
    np.save(os.path.join(BASE_DIR,"data/dataset/Y.npy"), y_records)
    np.save(os.path.join(BASE_DIR,"data/dataset/status.npy"), status_records)
    

    



