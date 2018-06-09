# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
# 生成数据
import numpy as np


def draw_pie(keyworld, infos):
    """绘制饼图
    :param infos:
    """
    labels = u'北京', u'上海', u'广州', u'深圳'

    # 画饼图尺寸
    plt.figure(1, figsize=(6, 6))
    expl = [0, 0.1, 0, 0]  # 第二块即China离开圆心0.1
    # Colors used. Recycle if not enough.
    colors = ["blue", "red", "green", "yellow"]  # 设置颜色（循环显示）

    # autopct: 百分数格式
    pie = plt.pie(infos, explode=expl, colors=colors, labels=labels, autopct='%1.1f%%', pctdistance=0.8,
                  shadow=False)

    # 中文字体库
    font = fm.FontProperties(fname=r"/usr/local/lib/python3.6/site-packages/matplotlib/mpl-data/fonts/ttf/MSYH.ttf",
                             size=14)
    # 解决标签中文乱码问题
    for lable in pie[1]:
        lable.set_fontproperties(font)

    # 解决标题中文乱码问题
    plt.title('北上广深%s个%s岗位分布情况' % (sum(infos), keyworld), fontproperties=font)
    plt.show()
    # plt.savefig("pie.jpg") #保存图片
    plt.close()

    print('北上广深%s个%s岗位分布情况' % (sum(infos), keyworld))


def draw_line(keyworld, x, y):
    """绘制圆柱/线型图
       """

    # 中文字体库
    font = fm.FontProperties(fname=r"/usr/local/lib/python3.6/site-packages/matplotlib/mpl-data/fonts/ttf/MSYH.ttf",
                             size=14)

    plt.figure(figsize=(12, 4))  # 创建绘图对象
    # plt.plot(x, y, "b--", linewidth=2)  # 在当前绘图对象绘图（X轴，Y轴，蓝色虚线，线宽度）
    plt.bar(x, y, 0.3, color="green")
    plt.xlabel("money")  # X轴标签
    plt.ylabel("quantity")  # Y轴标签
    # 解决标题中文乱码问题
    plt.title('%s岗位薪资分析' % keyworld, fontproperties=font)
    plt.show()  # 显示图
    # plt.savefig("salary_line.jpg")  # 保存图


if __name__ == '__main__':
    # X轴，Y轴数据y
    x = ['0.7', '0.5', '1.2', '0.9', '0.4', '0.6', '0.8', '1.0', '1.1', '1.4']
    y = [285, 232, 170, 161, 150, 145, 140, 114, 65, 58]

    draw_line("demo",x, y)
