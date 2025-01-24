import pandas as pd
import numpy as np
import akshare as ak
from prometheus_client.context_managers import Timer
from pygments.lexer import words

from aktools import dongcai as dc
from datetime import datetime,timedelta

print(pd.__version__)
print(np.__version__)

def 你好(name:str='world'):
    print('hellow {}, time={}'.format(name, datetime.now().strftime('%Y%m%d%H%M%S')))
def getDateSpace(days:int = 365):
    current_date=datetime.now()
    day_ago = current_date - timedelta(days=days)
    return day_ago.strftime('%Y%m%d'), current_date.strftime('%Y%m%d')
if __name__ == '__main__':
    你好('world start')
    data_space=getDateSpace()
    print(data_space)
    dc.banKuai()
    dc.banKuaiHangQing('汽车零部件',data_space[0],data_space[1])
    dc.banKuaiChengFen('汽车零部件')
    dc.guPiaoHangQing('000001',data_space[0],data_space[1])
    你好('world end')
