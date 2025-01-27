import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# 示例 losses 数组，你可以将其替换
def 你好(name: str = 'world'):
    print('{}, time={}'.format(name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
if __name__ == '__main__':

    with open('losses.txt', mode='r') as losses_file:
        你好('start read ')
        lines = losses_file.readlines()
        你好('end read ')
        print(len(lines))
        losses = []
        for line in lines:
            values=line.replace('[','').replace(']','').replace(' ','').split(',')
            # 使用map()函数将字符串元素转换为浮点数
            float_list = list(map(float, values))
            losses.extend(float_list)



        print(len(losses))
        losses = losses[0::500]
        print(len(losses))

        # 生成横坐标，即losses数组的索引
        x = range(len(losses))

        # 创建图形
        plt.figure(figsize=(10, 6))

        # 绘制折线图
        plt.plot(x, losses, marker='o', linestyle='-', color='b')

        # 设置标题和坐标轴标签
        plt.title('Losses折线图')
        plt.xlabel('Losses的数量')
        plt.ylabel('Losses的值')

        # 显示网格
        plt.grid(True)

        # 显示图形
        plt.show()