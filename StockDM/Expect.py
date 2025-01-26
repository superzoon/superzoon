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
    # 按行对齐，去除多余的行 清洗数据
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
    train_data = train_data.dropna()
    return train_data[0:1]


if __name__ == '__main__':
    你好('预测开启')
    df = pd.DataFrame()
    # 读取所有的板块
    if read_from_csv:
        bankuai = pd.DataFrame(pd.read_csv(os.path.join('assets', 'bankuai.csv')))
    else:
        data_space = getDateSpace()
        bankuai = dc.banKuai()
        bankuai.to_csv(os.path.join('assets', 'bankuai.csv'))

    # 遍历所有的板块
    number = 0;
    for bankuai_name in bankuai['板块名称']:

        # 读取板块的行情数据
        if read_from_csv:
            bankuaihangqing = pd.DataFrame(pd.read_csv(os.path.join('assets', r'{}.csv'.format(bankuai_name))))
        else:
            bankuaihangqing = dc.banKuaiHangQing(bankuai_name, data_space[0], data_space[1])
            bankuaihangqing.to_csv(os.path.join('assets', r'{}.csv'.format(bankuai_name)))

        bankuaihangqing = bankuaihangqing.loc[0:60]
        # 读取板块所有的成分股
        bankuaichengfen = dc.banKuaiChengFen(bankuai_name)
        chengfen = bankuaichengfen.loc[:, ['代码', '名称']]
        # chengfen = pd.DataFrame({'代码':['603887'],'名称':['城地香江']})#测试训练过程出现错误的股票
        # 遍历该板块所有的成分股
        for index, row in chengfen.iterrows():
            if not isInSS(row['代码'], row['名称']):
                continue
            number = number + 1
            print('{} {}_{}.csv'.format(number, row['代码'], row['名称']))

            # 获取股票的行情数据
            if read_from_csv:
                gupiaohangqing = pd.DataFrame(
                    pd.read_csv(os.path.join('assets', r'{}_{}.csv'.format(row['代码'], row['名称']))))
            else:
                gupiaohangqing = dc.guPiaoHangQing(row['代码'], row['名称'], data_space[0], data_space[1])
                gupiaohangqing.to_csv(os.path.join('assets', r'{}_{}.csv'.format(row['代码'], row['名称'])))

            gupiaohangqing = gupiaohangqing.loc[0:60]
            # 清洗数据
            temp_df = clean_data(bankuaihangqing, gupiaohangqing)

            # 使用 concat 函数按行拼接
            df = pd.concat([df, temp_df], ignore_index=True)

    # 预测模型
    from tensorflow.keras.models import load_model

    model_path = 'stock_20.h5'
    loaded_model = load_model(model_path)
    features = ['RF_5', 'RF_10', 'RF_15', 'RF_20', 'Turnover_5', 'Turnover_10', 'price_5', 'price_10']
    X = df[features]
    predictions = loaded_model.predict(X)
    df['expext'] = predictions
    df.sort_values(by='expext', ascending=False, inplace=True)
    df.reset_index()
    df = df.loc[:, ['Datetime','code','name','expext']]
    df.to_csv('expect.csv')
    print(df.head(20))
    你好('预测结束')
