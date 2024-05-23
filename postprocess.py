import matplotlib
matplotlib.use('TkAgg')  # 或者使用 'Qt5Agg'
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import cm
from scipy import interpolate
def plot_contour2D(coords, result, input_labels, out_labels):
    """
    简单2D云图使用自己编写的程序即可实现，复杂云图得用其他工具包
    :param coords:
    :param result:
    :param input_labels:
    :param out_labels:
    :return:
    """
    levels_contour = np.linspace(min(result), max(result), 20)
    levels_cbar = np.linspace(min(result), max(result), 10)
    x1_meshnode = np.linspace(min(coords[0]), max(coords[0]), 1000)
    x2_meshnode = np.linspace(min(coords[1]), max(coords[1]), 1000)
    # 生成二维数据坐标点
    x1_interpolate, x2_interpolate = np.meshgrid(x1_meshnode, x2_meshnode)
    # 通过griddata函数插值得到所有的(X1, Y1)处对应的值
    result_interpolate = interpolate.griddata(tuple(coords), result, (x1_interpolate, x2_interpolate), method='cubic')
    fig, ax = plt.subplots(figsize=(12, 8))
    #ax.axis('off')
    # level设置云图颜色范围以及颜色梯度划分。其中，设置cmap为jet，即最小值为蓝色，最大为红色，和有限元软件云图配色类似
    result_contour = ax.contourf(x1_interpolate, x2_interpolate, result_interpolate, levels_contour, cmap=cm.jet)
    ax.set_xlabel(input_labels[0], size=15)
    ax.set_ylabel(input_labels[1], size=15)
    ax.set_aspect('equal')
    # 为结果云图添加colorbar
    cbar = fig.colorbar(result_contour, shrink=0.5)
    cbar.set_label(out_labels, size=18)
    cbar.set_ticks(levels_cbar)
    # 显示结果
    plt.show()
if __name__ == "__main__":
    # 读取数据
    data = pd.read_csv(r'D:\GuoHB\MyFiles\Simulation\Test\test_20240312_files\user_files\fluent_out.txt')
    # 提取坐标和速度数据
    y = data.iloc[:, 2]
    z = data.iloc[:, 3]
    v = data.iloc[:, 4]
    coords = [z, y]
    input_labels = ["x1[m]", "x2[m]"]
    out_label = "v[m/s]"
    plot_contour2D(coords, v, input_labels, out_label)