from time import sleep

import pandas as pd
import numpy as np
import akshare as ak
import os
from prometheus_client.context_managers import Timer
from pygments.lexer import words

from aktools import dongcai as dc
from datetime import datetime, timedelta

from aktools.dongcai import isInSS

print(pd.__version__)
print(np.__version__)


def 你好(name: str = 'world'):
    print('hellow {}, time={}'.format(name, datetime.now().strftime('%Y%m%d%H%M%S')))


def getDateSpace(days: int = 365):
    current_date = datetime.now()
    day_ago = current_date - timedelta(days=days)
    return day_ago.strftime('%Y%m%d'), current_date.strftime('%Y%m%d')


if __name__ == '__main__':
    你好('world start')
    data_space = getDateSpace()
    print(data_space)
    bankuai = dc.banKuai()
    bankuai.to_csv(os.path.join('assets','bankuai.csv'))
    count = 0
    for bankuai_name in bankuai['板块名称']:
        bankuaihangqing = dc.banKuaiHangQing(bankuai_name, data_space[0], data_space[1])
        bankuaihangqing.to_csv(os.path.join('assets',r'{}.csv'.format(bankuai_name)))
        bankuaichengfen = dc.banKuaiChengFen(bankuai_name)
        chengfen = bankuaichengfen.loc[:, ['代码', '名称']]
        print(chengfen)
        for index, row in chengfen.iterrows() :
            if not isInSS(row['代码'], row['名称']):
                continue
            print('{}_{}.csv'.format(row['代码'],row['名称']))
            gupiaohangqing = dc.guPiaoHangQing(row['代码'],row['名称'], data_space[0], data_space[1])
            gupiaohangqing.to_csv(os.path.join('assets',r'{}_{}.csv'.format(row['代码'],row['名称'].replace('*',''))))

            print(gupiaohangqing)
            count = count + 1
            if count % 100 == 0:
                sleep(5)
    你好('world end')
