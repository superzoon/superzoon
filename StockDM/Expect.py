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

model_day_len = 50


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
    # 股票价格
    train_data.insert(4, 'ushadow', (gupiao['最高'] - gupiao['收盘']) / gupiao['收盘'])
    # 股票价格
    train_data.insert(5, 'dshadow', (gupiao['收盘'] - gupiao['最低']) / gupiao['收盘'])
    # 股票相对板块的涨幅
    train_data.insert(6, 'RF', (gupiao['涨跌幅'] - bankuai['涨跌幅']) / 100)
    # 股票成交金额
    train_data.insert(7, 'Turnover', gupiao['成交额'])
    # 股票相对板块多日涨幅
    train_data['RF_5'] = [multiply_rf(train_data, 'RF', i, 5) for i in range(len(train_data))]
    train_data['RF_10'] = [multiply_rf(train_data, 'RF', i, 10) for i in range(len(train_data))]
    train_data['RF_15'] = [multiply_rf(train_data, 'RF', i, 15) for i in range(len(train_data))]
    train_data['RF_20'] = [multiply_rf(train_data, 'RF', i, 20) for i in range(len(train_data))]
    train_data['RF_25'] = [multiply_rf(train_data, 'RF', i, 25) for i in range(len(train_data))]
    train_data['RF_30'] = [multiply_rf(train_data, 'RF', i, 30) for i in range(len(train_data))]
    train_data['RF_35'] = [multiply_rf(train_data, 'RF', i, 35) for i in range(len(train_data))]
    train_data['RF_40'] = [multiply_rf(train_data, 'RF', i, 40) for i in range(len(train_data))]
    train_data['RF_45'] = [multiply_rf(train_data, 'RF', i, 45) for i in range(len(train_data))]
    train_data['RF_50'] = [multiply_rf(train_data, 'RF', i, 50) for i in range(len(train_data))]
    train_data['RF_55'] = [multiply_rf(train_data, 'RF', i, 55) for i in range(len(train_data))]
    train_data['RF_60'] = [multiply_rf(train_data, 'RF', i, 60) for i in range(len(train_data))]

    # 股票成交多日金额比
    train_data['Turnover_5'] = [mean_col(train_data, 'Turnover', i, 5) for i in range(len(train_data))]
    train_data['Turnover_10'] = [mean_col(train_data, 'Turnover', i, 10) for i in range(len(train_data))]

    # 股票成交多日均线比
    train_data['price_5'] = [mean_price(train_data, 'price', i, 5) for i in range(len(train_data))]
    train_data['price_10'] = [mean_price(train_data, 'price', i, 10) for i in range(len(train_data))]

    # 预取价格
    train_data = train_data.dropna()
    return train_data[0:3]


if __name__ == '__main__':
    你好('预测开启')

    src_model_path = 'stock_{}.h5'.format(model_day_len)
    model_path = 'stock_{}_back.h5'.format(model_day_len)
    import shutil
    import msvcrt

    with open('lock_file_{}'.format(model_day_len), 'w') as lock_file:
        try:
            # 获取排他锁
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
            print(f"Process {os.getpid()} acquired the lock.")
            # 模拟一些耗时操作
            # 复制文件
            shutil.copy2(src_model_path, model_path)
            print(f"文件 {src_model_path} 已成功拷贝到 {model_path}。")
        except FileNotFoundError:
            print(f"源文件 {src_model_path} 未找到，请检查文件路径。")
        except PermissionError:
            print("没有足够的权限进行文件拷贝操作，请检查文件权限。")
        except Exception as e:
            print(f"发生未知错误: {e}")
        finally:
            # 释放锁
            msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
            print(f"Process {os.getpid()} released the lock.")

    if not os.path.isfile(model_path):
        print('没有模型文件')
        exit(0)
    df = pd.DataFrame()
    data_space = getDateSpace()
    # 读取所有的板块
    if read_from_csv:
        bankuai = pd.DataFrame(pd.read_csv(os.path.join('assets', 'bankuai.csv')))
    else:
        bankuai = dc.banKuai()
        bankuai.to_csv(os.path.join('assets', 'bankuai.csv'))

    # 遍历所有的板块
    number = 0
    for bankuai_name in bankuai['板块名称']:

        # 读取板块的行情数据
        cheng_fen_hangqing_path = os.path.join('assets', r'{}.csv'.format(bankuai_name))
        if read_from_csv and os.path.isfile(cheng_fen_hangqing_path):
            bankuaihangqing = pd.DataFrame(pd.read_csv(cheng_fen_hangqing_path))
        else:
            bankuaihangqing = dc.banKuaiHangQing(bankuai_name, data_space[0], data_space[1])
            bankuaihangqing.to_csv(cheng_fen_hangqing_path)

        bankuaihangqing = bankuaihangqing.loc[0:model_day_len+10]
        # 读取板块所有的成分股
        cheng_fen_name_path = os.path.join('assets', r'{}_成分.csv'.format(bankuai_name))
        if read_from_csv and os.path.isfile(cheng_fen_name_path):
            bankuaichengfen = pd.DataFrame(pd.read_csv(cheng_fen_name_path, dtype={'代码': str}))
        else:
            bankuaichengfen = dc.banKuaiChengFen(bankuai_name)
            bankuaichengfen.to_csv(cheng_fen_name_path)
        chengfen = bankuaichengfen.loc[:, ['代码', '名称']]
        # chengfen = pd.DataFrame({'代码':['603887'],'名称':['城地香江']})#测试训练过程出现错误的股票
        # 遍历该板块所有的成分股
        print('{} {}'.format(bankuai_name, len(chengfen)), end=' == > ')
        for index, row in chengfen.iterrows():
            if not isInSS(row['代码'], row['名称']):
                continue
            number = number + 1
            print('{}:{}_{}'.format(number, row['代码'], row['名称']), end=' ')

            # 获取股票的行情数据
            gupiao_path = os.path.join('assets', r'{}_{}.csv'.format(row['代码'], row['名称']))
            if read_from_csv and os.path.isfile(gupiao_path):
                gupiaohangqing = pd.DataFrame(pd.read_csv(gupiao_path))
            else:
                gupiaohangqing = dc.guPiaoHangQing(row['代码'], row['名称'], data_space[0], data_space[1])
                gupiaohangqing.to_csv(os.path.join('assets', r'{}_{}.csv'.format(row['代码'], row['名称'])))

            gupiaohangqing = gupiaohangqing.loc[0:60]
            # 清洗数据
            temp_df = clean_data(bankuaihangqing, gupiaohangqing)

            # 使用 concat 函数按行拼接
            df = pd.concat([df, temp_df], ignore_index=True)
        print(' ')
        if not read_from_csv:
            time.sleep(5)

    # 预测模型
    from tensorflow.keras.models import load_model

    loaded_model = load_model(model_path)
    features = ['ushadow', 'dshadow', 'Turnover_5', 'Turnover_10', 'price_5',
                'price_10', 'RF_5', 'RF_10', 'RF_15', 'RF_20']
    if model_day_len >= 30:
        features.extend(['RF_25', 'RF_30'])
    if model_day_len >= 40:
        features.extend(['RF_35', 'RF_40'])
    if model_day_len >= 50:
        features.extend(['RF_45', 'RF_50'])
    if model_day_len >= 60:
        features.extend(['RF_55', 'RF_60'])

    X = df[features]
    predictions = loaded_model.predict(X)
    df['expext'] = predictions
    df.sort_values(by='expext', ascending=False, inplace=True)
    df.reset_index(inplace=True)
    df = df.loc[:, ['Datetime', 'code', 'name', 'expext']]
    df.to_csv('expect_{}.csv'.format(model_day_len))

    print(df.tail(20))
    print(df.head(20))
    你好('预测结束')
