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

read_from_csv = True
model_day_len =60


def 你好(name: str = 'world'):
    print('{}, time={}'.format(name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


def getDateSpace(days: int = 365):
    current_date = datetime.now()
    day_ago = current_date - timedelta(days=days)
    return day_ago.strftime('%Y%m%d'), current_date.strftime('%Y%m%d')


def multiply_rf(df: pd.DataFrame, name: str, index: int, count: int = 5):
    '''
    :return: 返回最近count日期的涨跌幅
    '''

    start_index = index;
    end_index = start_index + count
    if end_index < len(df):
        result = 1
        for i in range(count):
            # print('{},{},{},{}'.format(index,name, i, start_index + count - i))
            cvalue = df[name][start_index + count - i - 1]
            result = result + cvalue * result
            # print('{} {} {} {}'.format(index, i,cvalue,result))
        return result
    else:
        return np.nan


def mean_col(df: pd.DataFrame, name: str, index: int, count: int = 5):
    '''
    返回df的name列的index行,该行是后面5行的平均值
    '''
    start_index = index
    end_index = start_index + count
    if end_index < len(df):
        return df[name][index] / df[name][start_index:end_index].mean()
    else:
        return np.nan


def mean_price(df: pd.DataFrame, name: str, index: int, count: int = 5):
    '''
    返回df的name列的index行,该行是后面5行的平均值差比
    '''
    start_index = index
    end_index = start_index + count
    if end_index < len(df):
        return (df[name][index] - df[name][start_index:end_index].mean()) / df[name][index]
    else:
        return np.nan


def max_expect(df: pd.DataFrame, name: str, index: int, count: int = 5):
    '''
    返回df的name列的index行,该行是前面面5行的最大值
    '''

    start_index = index
    end_index = start_index + count
    if end_index < len(df):
        return (df[name][index] - df[name][start_index:end_index].max()) / df[name][index]
    else:
        return np.nan


def clean_data(_bankuai: pd.DataFrame, _gupiao: pd.DataFrame):
    # print(_bankuai.columns, _gupiao.columns)
    # 按行对齐，去除多余的行
    bankuai = pd.DataFrame(_bankuai)
    bankuai.set_index('日期')
    gupiao = pd.DataFrame(_gupiao)
    gupiao.set_index('日期')
    bankuai, gupiao = bankuai.align(gupiao, join='inner', axis=0)
    # bankuai = _bankuai.loc[_bankuai['日期'] == _gupiao['日期']]
    # gupiao = _gupiao.loc[_bankuai['日期'] == _gupiao['日期']]

    train_data = pd.DataFrame()
    # 日期
    train_data.insert(0, 'Datetime', gupiao['日期'])
    # 代码
    train_data.insert(1, 'code', gupiao['股票代码'])
    # 名称
    train_data.insert(2, 'name', gupiao['股票名称'])
    # 股票价格
    train_data.insert(3, 'price', gupiao['收盘'])
    # 股票价格
    train_data.insert(4, 'ushadow', (gupiao['最高'] - gupiao['收盘']) / gupiao['收盘'])
    # 股票价格
    train_data.insert(5, 'dshadow', (gupiao['收盘'] - gupiao['最低']) / gupiao['收盘'])
    # 股票相对板块的涨幅
    train_data.insert(6, 'RF', (gupiao['涨跌幅'] - bankuai['涨跌幅']) / 100)
    # 股票成交金额
    train_data.insert(7, 'Turnover', gupiao['成交额'])
    # 名称
    train_data['bankuai_name'] = bankuai['板块']
    # 股票相对板块多日涨幅
    train_data['RF_1'] = [multiply_rf(train_data, 'RF', i, 1) for i in range(len(train_data))]
    train_data['RF_2'] = [multiply_rf(train_data, 'RF', i, 2) for i in range(len(train_data))]
    train_data['RF_3'] = [multiply_rf(train_data, 'RF', i, 4) for i in range(len(train_data))]
    train_data['RF_4'] = [multiply_rf(train_data, 'RF', i, 4) for i in range(len(train_data))]
    train_data['RF_6'] = [multiply_rf(train_data, 'RF', i, 6) for i in range(len(train_data))]
    train_data['RF_8'] = [multiply_rf(train_data, 'RF', i, 8) for i in range(len(train_data))]
    train_data['RF_10'] = [multiply_rf(train_data, 'RF', i, 10) for i in range(len(train_data))]
    train_data['RF_12'] = [multiply_rf(train_data, 'RF', i, 12) for i in range(len(train_data))]
    train_data['RF_14'] = [multiply_rf(train_data, 'RF', i, 14) for i in range(len(train_data))]
    train_data['RF_16'] = [multiply_rf(train_data, 'RF', i, 16) for i in range(len(train_data))]
    train_data['RF_18'] = [multiply_rf(train_data, 'RF', i, 18) for i in range(len(train_data))]
    train_data['RF_20'] = [multiply_rf(train_data, 'RF', i, 20) for i in range(len(train_data))]
    train_data['RF_22'] = [multiply_rf(train_data, 'RF', i, 22) for i in range(len(train_data))]
    train_data['RF_24'] = [multiply_rf(train_data, 'RF', i, 24) for i in range(len(train_data))]
    train_data['RF_26'] = [multiply_rf(train_data, 'RF', i, 26) for i in range(len(train_data))]
    train_data['RF_28'] = [multiply_rf(train_data, 'RF', i, 28) for i in range(len(train_data))]
    train_data['RF_30'] = [multiply_rf(train_data, 'RF', i, 30) for i in range(len(train_data))]
    train_data['RF_32'] = [multiply_rf(train_data, 'RF', i, 32) for i in range(len(train_data))]
    train_data['RF_34'] = [multiply_rf(train_data, 'RF', i, 34) for i in range(len(train_data))]
    train_data['RF_36'] = [multiply_rf(train_data, 'RF', i, 36) for i in range(len(train_data))]
    train_data['RF_38'] = [multiply_rf(train_data, 'RF', i, 38) for i in range(len(train_data))]
    train_data['RF_40'] = [multiply_rf(train_data, 'RF', i, 40) for i in range(len(train_data))]
    train_data['RF_42'] = [multiply_rf(train_data, 'RF', i, 42) for i in range(len(train_data))]
    train_data['RF_44'] = [multiply_rf(train_data, 'RF', i, 44) for i in range(len(train_data))]
    train_data['RF_46'] = [multiply_rf(train_data, 'RF', i, 46) for i in range(len(train_data))]
    train_data['RF_48'] = [multiply_rf(train_data, 'RF', i, 48) for i in range(len(train_data))]
    train_data['RF_50'] = [multiply_rf(train_data, 'RF', i, 50) for i in range(len(train_data))]
    train_data['RF_52'] = [multiply_rf(train_data, 'RF', i, 52) for i in range(len(train_data))]
    train_data['RF_54'] = [multiply_rf(train_data, 'RF', i, 54) for i in range(len(train_data))]
    train_data['RF_56'] = [multiply_rf(train_data, 'RF', i, 56) for i in range(len(train_data))]
    train_data['RF_58'] = [multiply_rf(train_data, 'RF', i, 58) for i in range(len(train_data))]
    train_data['RF_60'] = [multiply_rf(train_data, 'RF', i, 60) for i in range(len(train_data))]

    # 股票成交多日金额比
    train_data['Turnover_5'] = [mean_col(train_data, 'Turnover', i, 5) for i in range(len(train_data))]
    train_data['Turnover_10'] = [mean_col(train_data, 'Turnover', i, 10) for i in range(len(train_data))]
    train_data['Turnover_20'] = [mean_col(train_data, 'Turnover', i, 20) for i in range(len(train_data))]

    # 股票成交多日均线比
    train_data['price_5'] = [mean_price(train_data, 'price', i, 5) for i in range(len(train_data))]
    train_data['price_10'] = [mean_price(train_data, 'price', i, 10) for i in range(len(train_data))]
    train_data['price_20'] = [mean_price(train_data, 'price', i, 20) for i in range(len(train_data))]

    train_data = train_data.dropna()
    # 预取价格
    price = train_data['price'].rolling(window=5, min_periods=5)
    train_data['expect_max'] = (price.max().shift(1) / train_data['price'] - 1) * 100
    train_data['expect_min'] = (price.min().shift(1) / train_data['price'] - 1) * 100

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

    features = ['ushadow', 'dshadow', 'Turnover_5', 'Turnover_10', 'Turnover_20', 'price_5', 'price_10', 'price_20',
                'RF_1', 'RF_2', 'RF_3', 'RF_4', 'RF_6', 'RF_8', 'RF_10',
                'RF_12', 'RF_14', 'RF_16', 'RF_18', 'RF_20']
    if model_day_len >= 30:
        features.extend(['RF_22', 'RF_24', 'RF_26', 'RF_28', 'RF_30'])
    if model_day_len >= 40:
        features.extend(['RF_32', 'RF_34', 'RF_36', 'RF_38', 'RF_40'])
    if model_day_len >= 50:
        features.extend(['RF_42', 'RF_44', 'RF_46', 'RF_48', 'RF_50'])
    if model_day_len >= 60:
        features.extend(['RF_52', 'RF_54', 'RF_56', 'RF_58', 'RF_60'])

    x = df[features]
    features_count = len(features)
    hide_count = int(features_count * 2)#int(features_count * 2 / 3 + 1)
    for i in range(2):
        y = df['expect_max'] if i == 0 else df['expect_min']
        # 进行数据集划分
        print('进行数据集划分')
        if len(x) > 0 and len(y) > 0:
            # 划分训练集和测试集
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.05, random_state=42)
        else:
            print(df)
            return
        model_path = ('stock_{}_max.h5' if i == 0 else 'stock_{}_min.h5').format(model_day_len)
        if os.path.isfile(model_path):
            print('加载模型{}'.format(model_path))
            # 加载模型
            model = load_model(model_path)
        else:
            print('创建神经网络模型{}X{}X1'.format(features_count, hide_count))
            # 构建神经网络模型
            model = Sequential()
            model.add(Dense(features_count, input_dim=len(features), activation='linear'))
            model.add(Dense(hide_count, activation='linear'))
            model.add(Dense(1))
            model.compile(loss='mean_squared_error', optimizer='adam')

        # 训练 2000 轮
        你好('训练 2000 轮 train len = {}'.format(len(x_train)))
        # early_stopping = EarlyStopping(monitor='val_loss', patience=10, verbose=1)
        # history = model.fit(X_train, y_train, epochs=2000, batch_size=1024, validation_data=(x_test, y_test), verbose=0, callbacks=[early_stopping])
        history = model.fit(x_train, y_train, epochs=2000, batch_size=1024, validation_data=(x_test, y_test), verbose=0)

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


def launch_traing():
    你好('训练开启')
    count = 0
    if True and os.path.isfile('pre_training_data.csv'):
        full_df = pd.DataFrame(pd.read_csv('pre_training_data.csv'))
    else:
        full_df = pd.DataFrame()
        # 读取所有的板块
        if read_from_csv:
            bankuai = pd.DataFrame(pd.read_csv(os.path.join('assets', 'bankuai.csv')))
        else:
            data_space = getDateSpace()
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

        expect_df = full_df[full_df['expect_max'].isna()].drop(['expect_max', 'expect_min'], axis=1, inplace=False)
        expect_df.dropna().to_csv('pre_expect_data.csv')
        full_df = full_df.dropna().reset_index(drop=True)
        full_df.to_csv('pre_training_data.csv')

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
    plot_losses()
