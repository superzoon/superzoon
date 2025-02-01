import pandas as pd
import numpy as np
import akshare as ak
from sqlalchemy import create_engine, text, MetaData
import sqlite3


def __save_to_db__(df, table_name, replace=True):
    engine = create_engine('sqlite:///assets/ak_dongcai.db', echo=False)  # echo=True 用于调试
    conn = engine.connect()
    df.to_sql(table_name, index=False, con=conn, if_exists='replace' if replace else 'append', chunksize=1000)
    conn.close()


def reassign_code(code):
    if code.startswith('60'):
        return 'SH.ZB_' + code
    elif code.startswith('68'):
        return 'SH.KC_' + code
    elif code.startswith('00'):
        return 'SZ.ZB_' + code
    elif code.startswith('30'):
        return 'SH.KC_' + code
    else:
        return 'A_' + code


def isInSS(code: str, name: str):
    if name.__contains__('ST'):
        return False
    elif name.__contains__('st'):
        return False
    elif code.startswith('60'):  # 上交主板
        return True
    elif code.startswith('68'):  # 上交科创
        return True
    elif code.startswith('00'):  # 深交主板
        return True
    elif code.startswith('30'):  # 深交科创
        return True
    else:
        return False


def banKuai(updateDB=True, debug=False):
    '''
    东方财富-行业板块
    接口：stock_board_industry_name_em
    目标地址：https://quote.eastmoney.com/center/boardlist.html#industry_board
    描述：东方财富-沪深京板块-行业板块
    限量：单次返回当前时刻所有行业板块数据
    :return:
    '''
    df = ak.stock_board_industry_name_em()
    if debug: print(df)
    if updateDB: __save_to_db__(df, 'bankuai')
    return df


def banKuaiHangQing(symbol, start_date, end_date,
                    period="日k", adjust="hfq",
                    updateDB=True, debug=False):
    '''
    东方财富-指数-日频
    接口:stock_board_industry_hist_em
    目标地址:https://quote.eastmoney.com/bk/90.BK1027.html
    描述:东方财富-沪深板块-行业板块-历史行情数据
    限量:单次返回指定symbol和adjust的所有历史数据

    输入参数：
    symbol        str     symbol="小金属"；可以通过ak.stock_board_industry_name_em()查看所有东方财富行业板块行业代码
    start_date    str     start_date="20250101"
    end_date      str     end_date="20250101"
    period        str     period="日k" ；周期；choice of{"日k","周k","月k"}
    adjust        str     adjust="" ;复权类型 ；choice of{"" : 不复权,"qfq" : 前复权,"hfq" : 后复权}

    前复权能轻松看出股价走势，会存在负数
    后复权能看出股价收益
    :return:
    '''
    table_name = 'bankuai_hangqing'
    df = ak.stock_board_industry_hist_em(symbol, start_date, end_date, period, adjust)
    df.sort_values(by='日期', ascending=False, inplace=True)
    df.insert(loc=df.columns.get_loc('开盘'), column='板块', value=symbol)
    if debug: print(df)
    if updateDB:
        engine = create_engine('sqlite:///assets/ak_dongcai.db', echo=False)  # echo=True 用于调试
        conn = engine.connect()
        metaData = MetaData()
        metaData.reflect(bind=engine)
        if debug: print(metaData.tables)
        # 删除相同板块的数据
        if table_name in metaData.tables:
            exec_str = 'DELETE FROM {} WHERE "板块" = "{}";'.format(table_name, symbol)
            conn.execute(text(exec_str))
        df.to_sql(table_name, index=False, con=conn, if_exists='append', chunksize=1000)
        conn.commit()
        conn.close()

    return df


def banKuaiChengFen(symbol, updateDB=True, debug=False):
    '''
    东方财富-成分股
    接口：stock_board_industry_cons_em
    目标地址：https://data_eastmoney.com/bkzj/BK1037.html
    描述：东方财富-沪深板块-行业板块-板块成分
    限量：单次返回指定symbol的所有成分股

    输入参数：
    symbol        str     symbol="小金属"；可以通过ak.stock_board_industry_name_em()查看所有东方财富行业板块行业代码
    :return:
    '''
    table_name = 'bankuai_chengfen'
    df = ak.stock_board_industry_cons_em(symbol)
    df.insert(loc=df.columns.get_loc('序号'), column='板块', value=symbol)
    del df['序号']
    if debug: print(df)

    if updateDB:
        engine = create_engine('sqlite:///assets/ak_dongcai.db', echo=False)  # echo=True 用于调试
        conn = engine.connect()
        metaData = MetaData()
        metaData.reflect(bind=engine)
        if debug: print(metaData.tables)
        # 删除相同板块的数据
        if table_name in metaData.tables:
            exec_str = 'DELETE FROM {} WHERE "板块" = "{}";'.format(table_name, symbol)
            conn.execute(text(exec_str))
        df.to_sql(table_name, index=False, con=conn, if_exists='append', chunksize=1000)
        conn.commit()
        conn.close()
    return df


def guPiaoHangQing(symbol, name, start_date, end_date, period='daily', adjust='hfq', timeout=None,
                   updateDB=True, debug=False):
    '''
    接口：stock_zh_a_hist
    目标地址：https://quote.eastmoney.com/concept/sh603777.html?from=classic(实例)
    限量：单词返回指定沪深京A股上市公司，指定周期和指定日期的历史行情日频率数据
    输入参数：
    symbol        str    symbol="603777" : 股票代码可以在ak.stock_zh_a_spot_em()中获取
    period        str     period="daily" ；周期；choice of{'daily', 'weekly', 'monthly'}
    start_date    str     start_date="20250101"
    end_date      str     end_date="20250101"
    adjust        str     adjust="" ;复权类型 ；choice of{"" : 不复权,"qfq" : 前复权,"hfq" : 后复权}
    timeout       float   timeout=None; 默认不设置超市参数
    :return:
    '''
    table_name = 'gupiao_hangqing'
    df = ak.stock_zh_a_hist(symbol, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
    df.insert(loc=df.columns.get_loc('股票代码'), column='股票名称', value=name)
    df.sort_values(by='日期', ascending=False, inplace=True)
    if debug: print(df)
    if updateDB:
        engine = create_engine('sqlite:///assets/ak_dongcai.db', echo=False)  # echo=True 用于调试
        conn = engine.connect()
        metaData = MetaData()
        metaData.reflect(bind=engine)
        # 删除相同板块的数据
        if table_name in metaData.tables:
            conn.execute(text('DELETE FROM {} WHERE "股票代码" = "{}";'.format(table_name, symbol)))
            conn.commit()
        df.to_sql(table_name, index=False, con=conn, if_exists='append', chunksize=1000)
        conn.commit()
        conn.close()
    return df
