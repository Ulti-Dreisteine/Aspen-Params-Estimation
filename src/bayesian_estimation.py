# -*- coding: utf-8 -*-
"""
Created on 2021/10/09 16:17:49

@File -> bayesian_estimation.py

@Author: luolei

@Email: dreisteine262@163.com

@Describe: 使用贝叶斯方法对过程参数进行估计
"""

import numpy as np
import sys
import os

from numpy.core.fromnumeric import shape

BASE_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '../' * 2))
sys.path.append(BASE_DIR)

from src.settings import plt

if __name__ == '__main__':
    
    # ---- 载入数据 ---------------------------------------------------------------------------------
    
    X_arr = np.load(os.path.join(BASE_DIR, 'data/dataset/X.npy'))
    Y_arr = np.load(os.path.join(BASE_DIR, 'data/dataset/Y.npy'))
    status_arr = np.load(os.path.join(BASE_DIR, 'data/dataset/status.npy'))  # type: np.ndarray

    # plt.plot(status_arr.flatten())  # 都是正常收敛的结果.

    # ---- 数据整理 ---------------------------------------------------------------------------------

    data = np.hstack((Y_arr, X_arr))
    
    # ---- 贝叶斯估计  ------------------------------------------------------------------------------

    y_obs = 83.5
    eps = 1.0

    sub_data = data[np.where(np.abs(data[:, 0] - y_obs) <= eps)[0], :]

    # 重采样.
    repeats = 10000
    samples = None
    for i in range(repeats):
        idx = np.random.choice(np.arange(sub_data.shape[0]))

        if i == 0:
            samples = sub_data[idx: idx + 1, :]
        else:
            samples = np.vstack((samples, sub_data[idx: idx + 1, :]))

    # ---- 画出分布图 -------------------------------------------------------------------------------

    D_y = Y_arr.shape[1]
    D_x = X_arr.shape[1]

    x_cols = ['FEED_pressure', 'FEED_ETHANOL', 'FEED_ACETIC', 'FEED_H2O']

    fig, axis = plt.subplots(1, D_x, figsize = (10, 3))

    for i in range(D_x):
        w = 1.0 / samples.shape[0] * np.ones_like(samples[:, 0])
        axis[i].hist(samples[:, D_y + i], bins = 25, weights = w)
        axis[i].set_xlabel(x_cols[i])
        axis[i].set_ylabel('posterior PDF value')
    
    fig.tight_layout()

    





    

