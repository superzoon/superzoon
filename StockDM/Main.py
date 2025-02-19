import pandas
import pandas as pd
import numpy as np
import os

import threading
import time
from aktools import dongcai as dc
from datetime import datetime, timedelta

from aktools.dongcai import isInSS

print(pd.__version__)
print(np.__version__)

model_day_len =50


def 你好(name: str = 'world'):
    print('{}, time={}'.format(name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

def clean_data(_bankuai: pd.DataFrame, _gupiao: pd.DataFrame):
    # print(_bankuai.columns, _gupiao.columns)
    # 按行对齐，去除多余的行
    train_data = dc.clean_data(_bankuai, _gupiao)
    # print(train_data)

    return train_data


os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

test_losses = []


def training_model(df: pd.DataFrame):
    global test_losses
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error
    import tensorflow as tf
    from tensorflow.python.keras.models import save_model, load_model
    from tensorflow.python.keras import Sequential, layers, optimizers
    from tensorflow.python.keras.layers import Dense, LSTM
    from tensorflow.python.keras.callbacks import EarlyStopping

    你好(r'学习开始 {}'.format(model_day_len))

    features = dc.getFeature(model_day_len)
    x = df[features]
    features_count = int(len(features) * 1)
    hide_count = int(features_count * 2)#int(features_count * 2 / 3 + 1)

    y = df[['next_rf_1', 'expect_max', 'expect_min', 'expect_max_5', 'expect_min_5']]
    # 进行数据集划分
    print('进行数据集划分')
    if len(x) > 0 and len(y) > 0:
        # 划分训练集和测试集
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.05, random_state=42)
    else:
        print(df)
        return
    model_path = 'stock_{}.h5'.format(model_day_len)
    if os.path.isfile(model_path):
        print('加载模型{}'.format(model_path))
        # 加载模型
        model = load_model(model_path)
    else:
        print('创建神经网络模型{}X{}X{}'.format(features_count, hide_count, len(y.columns)))
        # 构建神经网络模型
        model = Sequential()
        model.add(Dense(features_count, input_dim=len(features), activation='linear'))
        model.add(Dense(hide_count, activation='linear'))
        model.add(Dense(features_count, activation='linear'))
        model.add(Dense(len(y.columns)))
        model.compile(loss='mean_squared_error', optimizer='adam')

    # 训练 10000 轮
    你好('训练 10000 轮 train len = {}'.format(len(x_train)))
    #early_stopping = EarlyStopping(monitor='val_loss', patience=10, verbose=1)
    #history = model.fit(x_train, y_train, epochs=10000, batch_size=512, validation_data=(x_test, y_test), verbose=0, callbacks=[early_stopping])
    history = model.fit(x_train, y_train, epochs=10000, batch_size=1024, validation_data=(x_test, y_test), verbose=0)

    # 在测试集上进行评估
    你好('测试集上进行评估')
    # 确保输入数据的形状一致
    x_test_tensor = tf.convert_to_tensor(x_test.values, dtype=tf.float32)
    y_pred = model.predict(x_test_tensor)
    mse = mean_squared_error(y_test, y_pred)
    你好(f"Initial training MSE: {mse}")

    # 收集本次训练的测试损失
    test_losses.extend(history.history['val_loss'])

    test_losses = test_losses[1::5]
    with open('losses_{}.txt'.format(model_day_len), mode='w') as f:
        f.write('{}\n'.format(history.history['val_loss']))
        f.flush()
        f.close()

    # 保存模型
    import msvcrt
    with open('lock_file_{}'.format(model_day_len), 'w') as lock_file:
        try:
            # 获取排他锁
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            print(f"Process {os.getpid()} acquired the lock.")
            # 模拟一些耗时操作
            save_model(model, model_path)
        except Exception as e:
            print(f"发生未知错误: {e}")
        finally:
            # 释放锁
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            print(f"Process {os.getpid()} released the lock.")


# 绘制折线图的函数
def plot_losses():
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import numpy as np
    fig, ax = plt.subplots()
    line, = ax.plot([], [])

    def init():
        line.set_data([], [])
        return line,

    def update(frame):
        if len(test_losses) > 0:
            # 设置 x 轴和 y 轴的刻度范围
            ax.set_xlim(0, len(test_losses))
            ax.set_ylim(0, max(test_losses) + 0.001)

            # 设置 x 轴和 y 轴的刻度标签（可选）
            x_ticks = np.arange(0, len(test_losses), 1)
            ax.set_xticks(x_ticks)
            ax.set_xticklabels([f'Epoch {i}' for i in x_ticks])

        x = np.arange(len(test_losses))
        y = test_losses
        line.set_data(x, y)
        ax.relim()
        ax.autoscale_view()
        return line,

    ani = animation.FuncAnimation(fig, update, init_func=init, interval=1000, blit=True, cache_frame_data=False)
    # 设置窗口标题为 losses
    fig.canvas.manager.set_window_title('losses_{}'.format(model_day_len))
    # 设置 x 轴和 y 轴的标签
    ax.set_xlabel('Epoch')
    ax.set_ylabel('Test Loss')
    ax.set_xlim(0, 10000)
    ax.set_ylim(0, 0.1)
    plt.show()

def show_loss():
    import matplotlib.pyplot as plt
    import numpy as np
    # 绘制折线图
    plt.plot(test_losses)
    # 设置图表标题和坐标轴标签
    plt.title('Test Losses Over Time')
    plt.xlabel('Epoch')
    plt.ylabel('Test Loss')
    # 显示图表
    plt.show()
def launch_traing():
    你好('训练开启')
    count = 0
    read_from_csv = True
    if False and os.path.isfile('pre_training_data.csv'):
        full_df = pd.DataFrame(pd.read_csv('pre_training_data.csv'))
    else:
        full_df = pd.DataFrame()
        # 读取所有的板块
        if read_from_csv:
            bankuai = pd.DataFrame(pd.read_csv(os.path.join('assets', 'bankuai.csv')))
        else:
            data_space = dc.getDateSpace()
            bankuai = dc.banKuai()
            bankuai.to_csv(os.path.join('assets', 'bankuai.csv'))

        # 遍历所有的板块
        import threading
        lock = threading.Lock()
        for bankuai_name in bankuai['板块名称']:
            print('加载板块:{} \n'.format(bankuai_name))
            log_txt = []
            # 读取板块的行情数据
            cheng_fen_hangqing_path = os.path.join('assets', r'{}.csv'.format(bankuai_name))
            if read_from_csv and os.path.isfile(cheng_fen_hangqing_path):
                bankuaihangqing = pd.DataFrame(pd.read_csv(cheng_fen_hangqing_path))
            else:
                bankuaihangqing = dc.banKuaiHangQing(bankuai_name, data_space[0], data_space[1])
                bankuaihangqing.to_csv(cheng_fen_hangqing_path)

            bankuaihangqing = bankuaihangqing.reset_index(drop=True)
            # 读取板块所有的成分股
            cheng_fen_name_path = os.path.join('assets', r'{}_成分.csv'.format(bankuai_name))
            if read_from_csv and os.path.isfile(cheng_fen_name_path):
                bankuaichengfen = pd.DataFrame(pd.read_csv(cheng_fen_name_path, dtype={'代码': str}))
            else:
                bankuaichengfen = dc.banKuaiChengFen(bankuai_name)
                bankuaichengfen.to_csv(cheng_fen_name_path)

            chengfen = bankuaichengfen.loc[:, ['代码', '名称']]
            # chengfen = pd.DataFrame({'代码':['301581'],'名称':['黄山谷捷']})#测试训练过程出现错误的股票
            # 遍历该板块所有的成分股
            log_txt.append('{} {} ==> '.format(bankuai_name, len(chengfen)))
            for index, row in chengfen.iterrows():
                if not isInSS(row['代码'], row['名称']):
                    continue
                # 使用with语句自动管理锁
                with lock:
                    count = count + 1
                log_txt.append('{}:{}_{}'.format(count, row['代码'], row['名称']))
                # 获取股票的行情数据
                gupiao_path = os.path.join('assets', r'{}_{}.csv'.format(row['代码'], row['名称']))
                if read_from_csv and os.path.isfile(gupiao_path):
                    gupiaohangqing = pd.DataFrame(pd.read_csv(gupiao_path, dtype={'股票代码': str}))
                else:
                    gupiaohangqing = dc.guPiaoHangQing(row['代码'], row['名称'], data_space[0], data_space[1])
                    gupiaohangqing.to_csv(os.path.join('assets', r'{}_{}.csv'.format(row['代码'], row['名称'])))

                gupiaohangqing = gupiaohangqing.reset_index(drop=True)
                # 清洗数据
                temp_df = clean_data(bankuaihangqing, gupiaohangqing)
                # 获取锁
                lock.acquire()
                try:
                    # 按行拼接DataFrame
                    full_df = pd.concat([full_df, temp_df], axis=0)
                finally:
                    # 释放锁
                    lock.release()
                time.sleep(0.1)
                # break
            print(' '.join(log_txt))
            print('')
            # break

            if not read_from_csv:
                time.sleep(5)

        expect_df = full_df[full_df['expect_max_5'].isna()]
        expect_df.to_csv('pre_expect_data.csv', index=False)
        full_df = full_df.dropna().reset_index(drop=True)
        full_df.to_csv('pre_training_data.csv', index=False)
        full_df = pd.DataFrame(pd.read_csv('pre_training_data.csv'))

    for i in range(1):
        print('训练大轮询{}'.format(i))
        # 训练模型
        training_model(full_df)

    你好('训练结束')


if __name__ == '__main__':
    # update_thread = threading.Thread(target=launch_traing)
    # update_thread.daemon = True
    # update_thread.start()
    launch_traing()
    show_loss()
