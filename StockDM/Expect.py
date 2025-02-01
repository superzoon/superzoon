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
    train_data.insert(1, 'code', gupiao['股票代码'].astype(str))
    # 名称
    train_data.insert(2, 'name', gupiao['股票名称'])
    # 板块名称
    train_data.insert(3, 'bankuai_name', bankuai['板块'])
    # 股票价格
    train_data.insert(4, 'price', gupiao['收盘'])
    # 股票价格
    train_data.insert(5, 'ushadow', (gupiao['最高'] - gupiao['收盘']) / gupiao['收盘'])
    # 股票价格
    train_data.insert(6, 'dshadow', (gupiao['收盘'] - gupiao['最低']) / gupiao['收盘'])
    # 股票相对板块的涨幅
    train_data.insert(7, 'RF', (gupiao['涨跌幅'] - bankuai['涨跌幅']) / 100)
    # 股票成交金额
    train_data.insert(8, 'Turnover', gupiao['成交额'])

    # 股票相对板块多日涨幅
    train_data['RF_2'] = [multiply_rf(train_data, 'RF', i, 2) for i in range(len(train_data))]
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

    # 股票成交多日均线比
    train_data['price_5'] = [mean_price(train_data, 'price', i, 5) for i in range(len(train_data))]
    train_data['price_10'] = [mean_price(train_data, 'price', i, 10) for i in range(len(train_data))]

    # 预取价格
    train_data = train_data.dropna()
    return train_data[0:2]


if __name__ == '__main__':
    你好('预测开启')

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

        bankuaihangqing = bankuaihangqing.loc[0:70]
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
                gupiaohangqing = pd.DataFrame(pd.read_csv(gupiao_path, dtype={'股票代码': str}))
            else:
                gupiaohangqing = dc.guPiaoHangQing(row['代码'], row['名称'], data_space[0], data_space[1])
                gupiaohangqing.to_csv(os.path.join('assets', r'{}_{}.csv'.format(row['代码'], row['名称'])))

            gupiaohangqing = gupiaohangqing.loc[0:70]
            # 清洗数据
            temp_df = clean_data(bankuaihangqing, gupiaohangqing)
            # 使用 concat 函数按行拼接
            df = pd.concat([df, temp_df], ignore_index=True)
            # print(df)
            # break
        print('')
        print('')
        if not read_from_csv:
            time.sleep(5)
        # break

    for i in range(2 * 2, 7 * 2):
        model_day_len = int(int(i * 0.5) * 10)
        print('model_day_len = {}'.format(model_day_len))
        src_model_path = ('stock_{}_max.h5' if (i % 2) == 0 else 'stock_{}_min.h5').format(model_day_len)
        model_path = ('stock_{}_max_back.h5' if (i % 2) == 0 else 'stock_{}_min_back.h5').format(model_day_len)
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

        # 预测模型
        from tensorflow.keras.models import load_model

        loaded_model = load_model(model_path)
        features = ['ushadow', 'dshadow', 'Turnover_5', 'Turnover_10', 'price_5', 'price_10',
                    'RF_2', 'RF_4', 'RF_6', 'RF_8', 'RF_10',
                    'RF_12', 'RF_14', 'RF_16', 'RF_18', 'RF_20']
        if model_day_len >= 30:
            features.extend(['RF_22', 'RF_24', 'RF_26', 'RF_28', 'RF_30'])
        if model_day_len >= 40:
            features.extend(['RF_32', 'RF_34', 'RF_36', 'RF_38', 'RF_40'])
        if model_day_len >= 50:
            features.extend(['RF_42', 'RF_44', 'RF_46', 'RF_48', 'RF_50'])
        if model_day_len >= 60:
            features.extend(['RF_52', 'RF_54', 'RF_56', 'RF_58', 'RF_60'])
        # print(features)
        # print('columns')
        # print(df)
        x = df[features]
        predictions = loaded_model.predict(x)
        save_df = pd.DataFrame()
        save_df['Datetime'] = df['Datetime']
        save_df['code'] = df['code'].apply(dc.reassign_code)
        save_df['name'] = df['name']
        save_df['bankuai'] = df['bankuai_name']
        save_df['expext'] = predictions * 100
        save_df.sort_values(by='expext', ascending=False, inplace=True)
        save_df.reset_index(inplace=True)
        del save_df['index']
        save_df.to_csv(('expect_{}_max.csv' if (i % 2) == 0 else 'expect_{}_min.csv').format(model_day_len))

        print(save_df.tail(20))
        print(save_df.head(20))
    你好('预测结束')
