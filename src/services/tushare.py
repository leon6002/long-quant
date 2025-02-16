from datetime import datetime
import logging
import tushare as ts
import pandas as pd
from tqdm import tqdm
from config.base import TUSHARE_TOKEN
from config.db import listed_stocks_collection
from utils.common import get_date_range
from utils.db_utils import find_collection_data
logger = logging.getLogger(__name__)

news_src = ["sina", "wallstreetcn", "10jqka", "eastmoney", "yuncaijing", "fenghuang", "jinrongjie"]

ts.set_token(TUSHARE_TOKEN)

def get_client():
    pro = ts.pro_api()
    return pro


def get_news(time_range, sources=news_src):
    """
    Fetch news briefings from the Tushare API,
    """
    pro = get_client()
    dfs = []

    for source in tqdm(sources):
        # Fetch news data (example, adjust according to your API)
        df = pro.news(src=source, start_date=time_range[0], end_date=time_range[1])
        if not df.empty:
            df['source'] = source
            dfs.append(df)
    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data was fetched


def get_stocks():
    pro = get_client()
    # Query the list of all currently listed and trading stocks
    data = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
    return data


def realtime_quote(ts_code: str, column_map: bool=False) -> pd.DataFrame:
    df = ts.realtime_quote(ts_code=ts_code, src='dc')
    column_mapping = {
        'name': '股票名称',
        'ts_code': '股票代码',
        'date': '交易日期',
        'time': '交易时间',
        'open': '开盘价',
        'pre_close': '昨收价',
        'price': '现价',
        'high': '今日最高价',
        'low': '今日最低价',
        'bid': '竞买价',
        'ask': '竞卖价',
        'volume': '成交量',
        'amount': '成交金额',
        'b1_v': '委买一（量）',
        'b1_p': '委买一（价）',
        'b2_v': '委买二（量）',
        'b2_p': '委买二（价）',
        'b3_v': '委买三（量）',
        'b3_p': '委买三（价）',
        'b4_v': '委买四（量）',
        'b4_p': '委买四（价）',
        'b5_v': '委买五（量）',
        'b5_p': '委买五（价）',
        'a1_v': '委卖一（量）',
        'a1_p': '委卖一（价）',
        'a2_v': '委卖二（量）',
        'a2_p': '委卖二（价）',
        'a3_v': '委卖三（量）',
        'a3_p': '委卖三（价）',
        'a4_v': '委卖四（量）',
        'a4_p': '委卖四（价）',
        'a5_v': '委卖五（量）',
        'a5_p': '委卖五（价）'
    }
    if column_map:
        df.columns = [col.lower() for col in df.columns]
        df.rename(columns=column_mapping, inplace=True)
    return df


def stock_price(ts_code, time_range, freq, column_map=False) -> pd.DataFrame:
    logger.info(f'stock_price time_range: {time_range}')
    df: pd.DataFrame = ts.pro_bar(ts_code=ts_code, asset="E", start_date=time_range[0], end_date=time_range[1], freq=freq)
    column_mapping = {
        'ts_code': '股票代码',
        'trade_date': '交易日期',
        'open': '开盘价',
        'high': '最高价',
        'low': '最低价',
        'close': '收盘价',
        'pre_close': '昨收价',
        'change': '涨跌额',
        'pct_chg': '涨跌幅',
        'vol': '成交量 （手）',
        'amount': '成交额 （千元）'
    }
    if column_map:
        df = df.rename(columns=column_mapping)
    return df


def stock_performance(ts_codes: str, trade_date: str, period: str='D', column_rename=False) -> pd.DataFrame:
    """
    Args:
    ts_codes: 股票代码，多个以逗号隔开，比如：'002594.SZ,000977.SZ,002475.SZ'

        名称        | 类型   | 描述
    ------------|--------|--------------------------------------------------------
    ts_code     | str    | 股票代码
    trade_date  | str    | 交易日期
    open        | float  | 开盘价
    high        | float  | 最高价
    low         | float  | 最低价
    close       | float  | 收盘价
    pre_close   | float  | 昨收价【除权价，前复权】
    change      | float  | 涨跌额
    pct_chg     | float  | 涨跌幅 【基于除权后的昨收计算的涨跌幅：（今收-除权昨收）/除权昨收】
    vol         | float  | 成交量 （手）
    amount      | float  | 成交额 （千元）
    """
    pro = get_client()
    if period == 'D':
        df = pro.daily(ts_code=ts_codes, trade_date=trade_date)
    elif period == "W":
        df = pro.weekly(ts_code=ts_codes, trade_date=trade_date)
    elif period == 'M':
        df = pro.monthly(ts_code=ts_codes, trade_date=trade_date)
    column_mapping = {
        'ts_code': '股票代码',
        'trade_date': '交易日期',
        'open': '开盘价',
        'high': '最高价',
        'low': '最低价',
        'close': '收盘价',
        'pre_close': '昨收价【除权价，前复权】',
        'change': '涨跌额',
        'pct_chg': '涨跌幅(除权后)',
        'vol': '成交量 （手）',
        'amount': '成交额 （千元）'
    }
    if column_rename:
        df.rename(columns=column_mapping, inplace=True)
    return df


def stock_daily_basic(ts_codes, trade_date, column_rename=False):
    """
    获取股票每日基本面数据
    | 名称            | 类型   | 描述
    |-----------------|--------|---------------------------------
    | ts_code         | str    | TS股票代码
    | trade_date      | str    | 交易日期
    | close           | float  | 当日收盘价
    | turnover_rate   | float  | 换手率（%）
    | turnover_rate_f | float  | 换手率（自由流通股）
    | volume_ratio    | float  | 量比
    | pe              | float  | 市盈率（总市值/净利润，亏损的PE为空）
    | pe_ttm        | float  | 市盈率（TTM，亏损的PE为空）
    | pb              | float  | 市净率（总市值/净资产）
    | ps              | float  | 市销率
    | ps_ttm         | float  | 市销率（TTM）
    | dv_ratio       | float  | 股息率 （%）
    | dv_ttm          | float  | 股息率（TTM）（%）
    | total_share     | float  | 总股本  （万股）
    | float_share     | float  | 流通股本  （万股）
    | free_share     | float  | 自由流通股本  （万）
    | total_mv       | float  | 总市值  （万元）
    | circ_mv        | float  | 流通市值（万元）
    """
    pro = get_client()
    df = pro.daily_basic(ts_code=ts_codes, trade_date=trade_date)

    # Rename columns to Chinese descriptions
    column_mapping = {
        'ts_code': 'TS股票代码',
        'trade_date': '交易日期',
        'close': '当日收盘价',
        'turnover_rate': '换手率（%）',
        'turnover_rate_f': '换手率（自由流通股）',
        'volume_ratio': '量比',
        'pe': '市盈率（总市值/净利润，亏损的PE为空）',
        'pe_ttm': '市盈率（TTM，亏损的PE为空）',
        'pb': '市净率（总市值/净资产）',
        'ps': '市销率',
        'ps_ttm': '市销率（TTM）',
        'dv_ratio': '股息率 （%）',
        'dv_ttm': '股息率（TTM）（%）',
        'total_share': '总股本  （万股）',
        'float_share': '流通股本  （万股）',
        'free_share': '自由流通股本  （万）',
        'total_mv': '总市值  （万元）',
        'circ_mv': '流通市值（万元）'
    }
    if column_rename:
        df.rename(columns=column_mapping, inplace=True)
    return df


def trade_calendar(time_range: tuple, exchange: str=''):
    """
        名称       | 类型   | 默认显示   | 描述
    --------------|--------|----------|-------------------------
    exchange      | str    | Y        | 交易所 SSE上交所 SZSE深交所
    cal_date      | str    | Y        | 日历日期
    is_open       | str    | Y        | 是否交易 0休市 1交易
    pretrade_date | str    | Y        | 上一个交易日
    """
    pro = get_client()
    df = pro.trade_cal(exchange=exchange, start_date=time_range[0], end_date=time_range[1])
    return df

def get_trade_date_range(n: int=1) -> tuple:
    """
    获取最近n个股市交易日期的起始日期和截止日期
    """
    df_calendar = trade_calendar(get_date_range(n//20 + 1))
    df_calendar = df_calendar[df_calendar['is_open']==1]
    df_calendar = df_calendar.head(n)
    return (df_calendar.iloc[-1]['cal_date'], df_calendar.iloc[0]['cal_date'])

def get_last_trade_date() -> str:
    df_calendar = trade_calendar(get_date_range())
    return df_calendar.iloc[0]['pretrade_date']

def is_today_open():
    df_calendar = trade_calendar(get_date_range())
    return df_calendar.iloc[0]['is_open']

def is_date_open(date: str):
    df_calendar = trade_calendar((date, date))
    return df_calendar.iloc[0]['is_open'] == 1

def get_next_trade_date(given_date: datetime):
    reverse_range = get_date_range(-1, given_date)
    df_calendar = trade_calendar((reverse_range[1], reverse_range[0]))
    df_calendar = df_calendar[df_calendar['is_open']==1]
    if df_calendar.iloc[-1]['cal_date'] == given_date.strftime('%Y%m%d'):
        return df_calendar.iloc[-2]['cal_date']
    else:
        return df_calendar.iloc[-1]['cal_date']


def find_stock_name(ts_code: str) -> str | None:
    df_name = find_collection_data(listed_stocks_collection, {'ts_code': ts_code}, {'_id': 0, 'name': 1})
    if len(df_name) == 0:
        return None
    name = df_name[0]['name']
    return name

def find_stock_code(name: str) -> str | None:
    df_name = find_collection_data(listed_stocks_collection,  {'name': name}, {'_id': 0, 'ts_code': 1})
    if len(df_name) == 0:
        return None
    code = df_name[0]['ts_code']
    return code


def news_trade_date():
    now = datetime.now().time()
    market_close_time = datetime.strptime("14:00", "%H:%M").time()
    if is_today_open() == 1 and now < market_close_time:
        # 在下午三点之前，取最近的交易日期
        return get_trade_date_range(1)[1]
    else:
        return get_next_trade_date()

def trade_date_by_given_date(given_date: datetime):
    date_str = given_date.strftime("%Y%m%d")
    given_time = given_date.time()
    # 这里取下午2:50， 因为一般最后10分钟的新闻不大可能在3:00前反应在股市上
    market_close_time = datetime.strptime("14:50", "%H:%M").time()
    if is_date_open(date_str) and given_time < market_close_time:
        # 在下午三点之前，取最近的交易日期
        return given_date.strftime('%Y%m%d')
    else:
        return get_next_trade_date(given_date)

def news_collection_name(date: datetime=None):
    """
    获取新闻collection名称，格式是news_0207这种
    """
    date = date or datetime.now()
    suffix = trade_date_by_given_date(date)
    suffix = suffix[4:]
    news_collection = f"news_{suffix}"
    return news_collection
