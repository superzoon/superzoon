from unittest.mock import inplace

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


def 你好(name: str = 'world'):
    print('{}, time={}'.format(name, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))


def clean_data(_bankuai: pd.DataFrame, _gupiao: pd.DataFrame):
    # print(_bankuai.columns, _gupiao.columns)
    # 预取价格
    train_data = dc.clean_data(_bankuai, _gupiao)

    return train_data[0:2]
def loadGuPiaoHangQing(listName:list, count:int=1):
    if count > 50:
        return
    newList = list()
    for keys in listName:
        try:
            temp = dc.guPiaoHangQing(keys[0], keys[1], keys[2], keys[3])
            temp.to_csv(os.path.join('assets', r'{}_{}.csv'.format(row['代码'], row['名称'])))
        except:
            newList.append(keys)

    if len(newList) > 0:
        loadGuPiaoHangQing(newList, count + 1)

if __name__ == '__main__':
    你好('预测开启')

    read_from_csv = False
    df = pd.DataFrame()
    data_space = dc.getDateSpace()
    if False and os.path.isfile('pre_expect_data.csv'):
        df= pd.DataFrame(pd.read_csv('pre_expect_data.csv', dtype={'code': str}))
    else :
        # 读取所有的板块
        if read_from_csv:
            bankuai = pd.DataFrame(pd.read_csv(os.path.join('assets', 'bankuai.csv')))
        else:
            bankuai = dc.banKuai()
            bankuai.to_csv(os.path.join('assets', 'bankuai.csv'))

        # 遍历所有的板块
        number = 0

        errorList = list()
        for bankuai_name in bankuai['板块名称']:

            # 读取板块的行情数据
            cheng_fen_hangqing_path = os.path.join('assets', r'{}.csv'.format(bankuai_name))
            if read_from_csv and os.path.isfile(cheng_fen_hangqing_path):
                bankuaihangqing = pd.DataFrame(pd.read_csv(cheng_fen_hangqing_path))
            else:
                bankuaihangqing = dc.banKuaiHangQing(bankuai_name, data_space[0], data_space[1])
                bankuaihangqing.to_csv(cheng_fen_hangqing_path)

            bankuaihangqing = bankuaihangqing.reset_index(drop=True)
            bankuaihangqing = bankuaihangqing.iloc[0:70]

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
                    try:
                        gupiaohangqing = dc.guPiaoHangQing(row['代码'], row['名称'], data_space[0], data_space[1])
                        gupiaohangqing.to_csv(os.path.join('assets', r'{}_{}.csv'.format(row['代码'], row['名称'])))
                    except:
                        errorList.append([row['代码'], row['名称'], data_space[0], data_space[1]])
                        continue

                gupiaohangqing = gupiaohangqing.reset_index(drop=True)
                gupiaohangqing = gupiaohangqing.iloc[0:70]
                # 清洗数据
                temp_df = clean_data(bankuaihangqing, gupiaohangqing)
                # 使用 concat 函数按行拼接
                df = pd.concat([df, temp_df], ignore_index=True)
                #break
                time.sleep(0.1)
            print('')
            print('')
            if not read_from_csv:
                time.sleep(5)
            #break
        if len(errorList) > 0:
            loadGuPiaoHangQing(errorList, 0)
        df.to_csv('pre_expect_data.csv', index=False)
    for i in range(3 , 6):
        model_day_len = int(i * 10)
        print('model_day_len = {}'.format(model_day_len))
        src_model_path = 'stock_{}.h5'.format(model_day_len)
        model_path = 'stock_{}_back.h5'.format(model_day_len)
        import shutil
        import msvcrt
        if not os.path.isfile(src_model_path):
            continue
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
        features = dc.getFeature(model_day_len)
        #print(df)
        #print(features)
        x = df[features]
        predictions = pd.DataFrame(loaded_model.predict(x), columns=['optimistic','pessimistic'])
       # print(predictions)
        save_df = pd.DataFrame()
        save_df['Datetime'] = df['Datetime']
        save_df['code'] = df['code'].apply(dc.reassign_code)
        save_df['name'] = df['name']
        if 'bankuai_name' in df.columns:
            save_df['bankuai'] = df['bankuai_name']
        else :
            save_df['bankuai'] = df['name']
        save_df['optimistic'] = predictions['optimistic']
        save_df['pessimistic'] = predictions['pessimistic']
        save_df['next_rf'] = df['next_rf_1']
        save_df.reset_index(inplace=True)
        del save_df['index']
        print(save_df.head(5))

        #乐观数据
        optimistic_path = 'expect_{}_optimistic.csv'.format(model_day_len)
        #悲观数据
        pessimistic_path = 'expect_{}_pessimistic.csv'.format(model_day_len)

        full_df = save_df

        #full_df = full_df[[col for col in full_df.columns if col != 'next_rf'] + ['next_rf']]
        grouped = full_df.groupby('Datetime')
        for date, item_df in grouped:
            if len(item_df) < 10:
                continue
            # 删除全为空值的列
            item_df = item_df.dropna(axis=1, how='all')
            optimistic_df = item_df.sort_values(by='optimistic', ascending=False)
            optimistic_df = optimistic_df.reset_index()
            del optimistic_df['index']
            optimistic_df.to_csv('{}_{}'.format(date, optimistic_path), index = True)

            #分组显示
            my_df = optimistic_df.loc[0:200]
            expect_df = pd.DataFrame()
            # 统计每个名称的出现次数
            counts = my_df['bankuai'].value_counts()
            for item in counts.items():
                expect_df = pd.concat([expect_df, my_df[my_df['bankuai']==item[0]]], ignore_index=True)
            #expect_df.reset_index(inplace=True)
            expect_df.to_csv('{}_bankuai_{}.csv'.format(date, optimistic_path), index=True)

            # 获取列名列表
            columns = item_df.columns.tolist()
            # 找到 a 和 b 列的索引
            index_a = columns.index('optimistic')
            index_b = columns.index('pessimistic')
            # 交换 a 和 b 列的位置
            columns[index_a], columns[index_b] = columns[index_b], columns[index_a]
            # 根据新的列名顺序重新排列 DataFrame
            item_df = item_df[columns]

            pessimistic_df = item_df.sort_values(by='pessimistic', ascending=False)
            pessimistic_df = pessimistic_df.reset_index()
            del pessimistic_df['index']
            pessimistic_df.to_csv('{}_{}'.format(date, pessimistic_path), index = True)

            #分组显示
            my_df = pessimistic_df.iloc[0:200]
            expect_df = pd.DataFrame()
            # 统计每个名称的出现次数
            counts = my_df['bankuai'].value_counts()
            for item in counts.items():
                expect_df = pd.concat([expect_df, my_df[my_df['bankuai']==item[0]]], ignore_index=True)
            #expect_df.reset_index(inplace=True)
            expect_df.to_csv('{}_bankuai_{}.csv'.format(date, pessimistic_path), index=True)

            #根据bankuai列分组，然后按照每个组的大小进行排序
            # my_df = my_df.groupby('bankuai', group_keys=False) \
            #   .apply(lambda x: x.sort_values(by='optimistic', ascending=False)) \
            #   .reset_index(drop=True) \
            #   .sort_values(by='bankuai', key=lambda x: x.map(counts), ascending=False) \
            #   .reset_index(drop=True)
            # print(my_df)
            # my_df.to_csv('expect_{}.csv'.format(model_day_len))
            # my_df = None
    你好('预测结束')
