# Estimating-ASPEN-Parameters-by-the-Bayesian-Analysis

使用贝叶斯分析估计ASPEN模型参数

# 一、使用Python调用ASPEN模型

ASPEN模型保存为bkp文件;

在ASPEN的Variable Explorer中查找相应变量的调用地址Call:

* 进料压力：Application.Tree.FindNode("\Data\Streams\FEED\Input\PRES\MIXED")Data.Streams.FEED.Input.PRES.#0
* 进料流量：
  * ETHANOL: Application.Tree.FindNode("\Data\Streams\FEED\Input\FLOW\MIXED\ETHANOL")
  * ACETIC: Application.Tree.FindNode("\Data\Streams\FEED\Input\FLOW\MIXED\ACETIC")
  * H2O: Application.Tree.FindNode("\Data\Streams\FEED\Input\FLOW\MIXED\H2O")
* 出料流量：
  * ETHYL-01: Application.Tree.FindNode("\Data\Streams\PRODUCT\Stream Results\Table\  ETHYL-01 PRODUCT")
