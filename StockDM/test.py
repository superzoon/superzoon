import threading
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

# 模拟 test_losses 数组
test_losses = []

# 模拟更新 test_losses 数组的函数
def update_losses():
    global test_losses
    while True:
        # 模拟新的损失值
        new_loss = np.random.rand()
        test_losses.append(new_loss)
        time.sleep(5)

# 绘制折线图的函数
def plot_losses():
    fig, ax = plt.subplots()
    line, = ax.plot([], [])

    def init():
        line.set_data([], [])
        return line,

    def update(frame):
        x = np.arange(len(test_losses))
        y = test_losses
        line.set_data(x, y)
        ax.relim()
        ax.autoscale_view()
        return line,

    ani = animation.FuncAnimation(fig, update, init_func=init, interval=1000, blit=True)
    plt.show()
if __name__ == '__main__':

    # 创建并启动更新数据的子线程
    update_thread = threading.Thread(target=update_losses)
    update_thread.daemon = True
    update_thread.start()

    # 启动绘制折线图的函数
    plot_losses()