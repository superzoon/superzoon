import pandas as pd
import numpy as np
import akshare as ak
from sqlalchemy import create_engine, text, MetaData
import sqlite3
import os

from datetime import datetime, timedelta

def __save_to_db__(df, table_name, replace=True):
    engine = create_engine('sqlite:///assets/ak_dongcai.db', echo=False)  # echo=True 用于调试
    conn = engine.connect()
    df.to_sql(table_name, index=False, con=conn, if_exists='replace' if replace else 'append', chunksize=1000)
    conn.close()


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

def next_value(df: pd.DataFrame, name: str, index: int, count: int = 1):
    '''
    返回df的name列的index行,该行是前面行的平均值差比
    '''
    current_index = index + count
    if len(df) > current_index >= 0:
        return df[name][current_index]
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
    # 板块名称
    train_data.insert(3, 'bankuai_name', bankuai['板块'])
    # 股票价格
    train_data.insert(4, 'price', gupiao['收盘'])

    # train_data['price_next'] = train_data['price'].shift(1)
    # print(train_data.head(5))
    # exit(0)
    # 股票价格
    train_data.insert(5, 'ushadow', (gupiao['最高'] - gupiao['收盘']) / gupiao['收盘'])
    # 股票价格
    train_data.insert(6, 'dshadow', (gupiao['收盘'] - gupiao['最低']) / gupiao['收盘'])
    # 股票相对板块的涨幅
    train_data.insert(7, 'RF', (gupiao['涨跌幅'] - bankuai['涨跌幅']) / 100)
    # 股票成交金额
    train_data.insert(8, 'Turnover', gupiao['成交额'])

    train_data['price_high'] = gupiao['最高']
    train_data['price_low'] = gupiao['最低']
    # 股票相对板块多日涨幅
    train_data['RF_1'] = [multiply_rf(train_data, 'RF', i, 1) for i in range(len(train_data))]
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
    train_data['Turnover_20'] = [mean_col(train_data, 'Turnover', i, 20) for i in range(len(train_data))]
    train_data['Turnover_25'] = [mean_col(train_data, 'Turnover', i, 25) for i in range(len(train_data))]
    train_data['Turnover_30'] = [mean_col(train_data, 'Turnover', i, 30) for i in range(len(train_data))]
    train_data['Turnover_35'] = [mean_col(train_data, 'Turnover', i, 35) for i in range(len(train_data))]
    train_data['Turnover_40'] = [mean_col(train_data, 'Turnover', i, 40) for i in range(len(train_data))]
    train_data['Turnover_45'] = [mean_col(train_data, 'Turnover', i, 45) for i in range(len(train_data))]
    train_data['Turnover_50'] = [mean_col(train_data, 'Turnover', i, 50) for i in range(len(train_data))]
    train_data['Turnover_55'] = [mean_col(train_data, 'Turnover', i, 55) for i in range(len(train_data))]
    train_data['Turnover_60'] = [mean_col(train_data, 'Turnover', i, 60) for i in range(len(train_data))]

    # 股票成交多日均线比
    train_data['price_5'] = [mean_price(train_data, 'price', i, 5) for i in range(len(train_data))]
    train_data['price_10'] = [mean_price(train_data, 'price', i, 10) for i in range(len(train_data))]
    train_data['price_20'] = [mean_price(train_data, 'price', i, 20) for i in range(len(train_data))]
    train_data['price_25'] = [mean_price(train_data, 'price', i, 25) for i in range(len(train_data))]
    train_data['price_30'] = [mean_price(train_data, 'price', i, 30) for i in range(len(train_data))]
    train_data['price_35'] = [mean_price(train_data, 'price', i, 35) for i in range(len(train_data))]
    train_data['price_40'] = [mean_price(train_data, 'price', i, 40) for i in range(len(train_data))]
    train_data['price_45'] = [mean_price(train_data, 'price', i, 45) for i in range(len(train_data))]
    train_data['price_50'] = [mean_price(train_data, 'price', i, 50) for i in range(len(train_data))]
    train_data['price_55'] = [mean_price(train_data, 'price', i, 55) for i in range(len(train_data))]
    train_data['price_60'] = [mean_price(train_data, 'price', i, 60) for i in range(len(train_data))]

    train_data = train_data.dropna()
    # 预取价格
    price = train_data['price'].rolling(window=5, min_periods=5)
    train_data['expect_max_5'] = (price.max().shift(1) / train_data['price'] - 1) * 100
    train_data['expect_min_5'] = (price.min().shift(1) / train_data['price'] - 1) * 100

    # price = train_data['price_high'].rolling(window=1, min_periods=1)
    # train_data['expect_max'] = (price.max().shift(1) / train_data['price'] - 1) * 100
    # price = train_data['price_low'].rolling(window=1, min_periods=1)
    # train_data['expect_min'] = (price.min().shift(1) / train_data['price'] - 1) * 100
    train_data['expect_max'] = (train_data['price_high'].shift(1) / train_data['price'] - 1) * 100
    train_data['expect_min'] = (train_data['price_low'].shift(1) / train_data['price'] - 1) * 100

    #下一个交易日涨跌
    train_data['next_rf_1'] = [next_value(gupiao, '涨跌幅', i ,-1) for i in range(len(train_data))]
    # print(train_data)

    return train_data

def getFeature(model_day_len:int = 20):
    features = ['ushadow', 'dshadow', 'Turnover_5', 'Turnover_10', 'Turnover_20', 'price_5', 'price_10', 'price_20',
                'RF_1', 'RF_5', 'RF_10', 'RF_15', 'RF_20']
    if model_day_len >= 30:
        features.extend(['RF_25', 'RF_30'])
        features.extend(['Turnover_25', 'Turnover_30'])
        features.extend(['price_25', 'price_30'])
    if model_day_len >= 40:
        features.extend(['RF_35', 'RF_40'])
        features.extend(['Turnover_35', 'Turnover_40'])
        features.extend(['price_35', 'price_40'])
    if model_day_len >= 50:
        features.extend(['RF_45', 'RF_50'])
        features.extend(['Turnover_45', 'Turnover_50'])
        features.extend(['price_45', 'price_50'])
    if model_day_len >= 60:
        features.extend(['RF_55', 'RF_60'])
        features.extend(['Turnover_55', 'Turnover_60'])
        features.extend(['price_55', 'price_60'])
    return features

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


def banKuai(updateDB=False, debug=False):
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
                    updateDB=False, debug=False):
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


def banKuaiChengFen(symbol, updateDB=False, debug=False):
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
                   updateDB=False, debug=False):
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

    gupiao_path = os.path.join('assets', r'{}_{}.csv'.format(symbol, name))
    full = list()
    if os.path.isfile(gupiao_path):
        gupiaohangqing = pd.DataFrame(pd.read_csv(gupiao_path, dtype={'股票代码': str}))
        gupiaohangqing['日期'] = pd.to_datetime(gupiaohangqing['日期'])
        if len(gupiaohangqing) > 0:
            daydate = gupiaohangqing.loc[0, '日期']
            # 计算下一天的日期
            next_day_obj = daydate + timedelta(days=1)
            start_date = next_day_obj.strftime('%Y%m%d')
            # 定义日期字符串的格式
            date_format = '%Y%m%d'
            if datetime.strptime(start_date, date_format) > datetime.strptime(end_date, date_format):
                print(' realy, ', end='')
                return gupiaohangqing[['日期','股票名称','股票代码','开盘','收盘','最高','最低','成交量','成交额','振幅','涨跌幅','涨跌额','换手率']]
        full.append(gupiaohangqing)

    table_name = 'gupiao_hangqing'
    df = ak.stock_zh_a_hist(symbol, period=period, start_date=start_date, end_date=end_date, adjust=adjust)
    if len(df) > 0:
        df.insert(loc=df.columns.get_loc('股票代码'), column='股票名称', value=name)
        df['日期'] = pd.to_datetime(df['日期'])
        full.append(df)
    df = pd.concat(full, ignore_index=True)
    # 将日期列中的 datetime.date 对象转换为 pandas.Timestamp 对象
    df.sort_values(by='日期', ascending=False, inplace=True)
    df.reset_index(inplace=True)
    df = df[0:365]
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
    return df[['日期','股票名称','股票代码','开盘','收盘','最高','最低','成交量','成交额','振幅','涨跌幅','涨跌额','换手率']]
