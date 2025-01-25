import pandas as pd
import numpy as np
import os

from aktools import dongcai as dc
from datetime import datetime, timedelta

from aktools.dongcai import isInSS

print(pd.__version__)
print(np.__version__)

read_from_csv = True


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


def train(_bankuai: pd.DataFrame, _gupiao: pd.DataFrame):
    #print(_bankuai.columns, _gupiao.columns)
    bankuai = _bankuai.loc[_bankuai['日期'] == _gupiao['日期']]
    gupiao = _gupiao.loc[_bankuai['日期'] == _gupiao['日期']]
    train_data = pd.DataFrame()
    # 日期
    train_data.insert(0, 'Datetime', gupiao['日期'])
    # 代码
    train_data.insert(1, 'code', gupiao['股票代码'])
    # 名称
    train_data.insert(2, 'name', gupiao['股票名称'])
    # 股票价格
    train_data.insert(3, 'price', gupiao['收盘'])
    # 股票相对板块的涨幅
    train_data.insert(4, 'RF', (gupiao['涨跌幅'] - bankuai['涨跌幅']) / 100)
    # 股票成交金额
    train_data.insert(5, 'Turnover', gupiao['成交额'])
    # 股票相对板块多日涨幅
    train_data['RF_5'] = [multiply_rf(train_data, 'RF', i, 5) for i in range(len(train_data))]
    train_data['RF_10'] = [multiply_rf(train_data, 'RF', i, 10) for i in range(len(train_data))]
    train_data['RF_15'] = [multiply_rf(train_data, 'RF', i, 15) for i in range(len(train_data))]
    train_data['RF_20'] = [multiply_rf(train_data, 'RF', i, 20) for i in range(len(train_data))]

    # 股票成交多日金额比
    train_data['Turnover_5'] = [mean_col(train_data, 'Turnover', i, 5) for i in range(len(train_data))]
    train_data['Turnover_10'] = [mean_col(train_data, 'Turnover', i, 10) for i in range(len(train_data))]

    # 股票成交多日均线比
    train_data['price_5'] = [mean_price(train_data, 'price', i, 5) for i in range(len(train_data))]
    train_data['price_10'] = [mean_price(train_data, 'price', i, 5) for i in range(len(train_data))]

    # 预取价格
    train_data['expect'] = train_data['price'].rolling(window=5, min_periods=5).max().shift(1) / train_data['price'] - 1

    train_data = train_data.dropna()
    #print(train_data)

    train_data.to_csv('train_data.csv')
    #print(train_data.columns)
    return train_data


test_losses = []
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


def training_model(bankuai: str, gupiao: str, df: pd.DataFrame):
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error
    from tensorflow.python.keras import Sequential
    from tensorflow.python.keras.layers import Dense
    from tensorflow.python.keras.models import save_model, load_model
    import matplotlib.pyplot as plt

    你好('训练 {}---{}'.format(bankuai, gupiao))
    features = ['RF_5', 'RF_10', 'RF_15', 'RF_20', 'Turnover_5', 'Turnover_10', 'price_5', 'price_10']
    X = df[features]
    y = df['expect']
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05, random_state=42)
    model_path = 'stock_20.h5'
    if os.path.isfile(model_path):
        print('加载模型{}'.format(model_path))
        # 加载模型
        model = load_model(model_path)
    else:
        print('创建神经网络模型64X32X1')
        # 构建神经网络模型
        model = Sequential()
        model.add(Dense(64, input_dim=len(features), activation='relu'))
        model.add(Dense(32, activation='relu'))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='adam')

    # 训练 10000 轮
    history = model.fit(X_train, y_train, epochs=1000, batch_size=32, validation_data=(X_test, y_test), verbose=0)

    # 在测试集上进行评估
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"Initial training MSE: {mse}")

    # 收集本次训练的测试损失
    test_losses.extend(history.history['val_loss'])
    with open('losses', mode='a') as f:
        f.write('{}\n'.format(history.history['val_loss']))
        f.flush()
        f.close()

    # 保存模型
    model_path = 'regression_model.h5'
    save_model(model, model_path)

    # 绘制训练的测试结果图像（折线图）
    plt.figure(figsize=(10, 6))
    plt.plot(range(1, len(test_losses) + 1), test_losses, marker='o', linestyle='-')
    plt.xlabel('Epochs')
    plt.ylabel('Test Mean Squared Error')
    plt.title('Test MSE over Training Epochs')
    plt.grid(True)
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    你好('训练开启')

    # 读取所有的板块
    if read_from_csv:
        bankuai = pd.DataFrame(pd.read_csv(os.path.join('assets', 'bankuai.csv')))
    else:
        data_space = getDateSpace()
        bankuai = dc.banKuai()
        bankuai.to_csv(os.path.join('assets', 'bankuai.csv'))

    for i in range(10):
        # 遍历所有的板块
        for bankuai_name in bankuai['板块名称']:

            # 读取板块的行情数据
            if read_from_csv:
                bankuaihangqing = pd.DataFrame(pd.read_csv(os.path.join('assets', r'{}.csv'.format(bankuai_name))))
            else:
                bankuaihangqing = dc.banKuaiHangQing(bankuai_name, data_space[0], data_space[1])
                bankuaihangqing.to_csv(os.path.join('assets', r'{}.csv'.format(bankuai_name)))

            # 读取板块所有的成分股
            bankuaichengfen = dc.banKuaiChengFen(bankuai_name)
            chengfen = bankuaichengfen.loc[:, ['代码', '名称']]

            # 遍历该板块所有的成分股
            for index, row in chengfen.iterrows():
                if not isInSS(row['代码'], row['名称']):
                    continue
                print('{}_{}.csv'.format(row['代码'], row['名称']))

                # 获取股票的行情数据
                if read_from_csv:
                    gupiaohangqing = pd.DataFrame(
                        pd.read_csv(os.path.join('assets', r'{}_{}.csv'.format(row['代码'], row['名称']))))
                else:
                    gupiaohangqing = dc.guPiaoHangQing(row['代码'], row['名称'], data_space[0], data_space[1])
                    gupiaohangqing.to_csv(os.path.join('assets', r'{}_{}.csv'.format(row['代码'], row['名称'])))

                # 清洗数据
                df = train(bankuaihangqing, gupiaohangqing)
                # 训练模型
                training_model(bankuai_name, row['名称'], df)
    你好('训练结束')
