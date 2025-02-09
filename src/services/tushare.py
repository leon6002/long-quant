import logging
import tushare as ts
import pandas as pd
from tqdm import tqdm
from config.base import TUSHARE_TOKEN
logger = logging.getLogger(__name__)

news_src = ["sina", "wallstreetcn", "10jqka", "eastmoney", "yuncaijing", "fenghuang", "jinrongjie"]


def get_client():
    ts.set_token(TUSHARE_TOKEN)
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


def realtime_quote(ts_code):
    df = ts.realtime_quote(ts_code=ts_code, src='dc')
    return df


def stock_price(ts_code, time_range):
    ts.set_token(TUSHARE_TOKEN)
    df = ts.pro_bar(ts_code=ts_code, asset="E", start_date=time_range[0], end_date=time_range[1], freq='5min')
    return df


def stock_performance(ts_codes: str, trade_date: str, period: str='D') -> pd.DataFrame:
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
    # df.rename(columns=column_mapping, inplace=True)
    return df


def stock_daily_basic(ts_codes, trade_date):
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
    df.rename(columns=column_mapping, inplace=True)
    return df


def trade_calendar(time_range, exchange=''):
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


def calculate_period_last_trade_date():
    df = trade_calendar(('20250125', '20250208'))
    # print(df.to_markdown())
    # 过滤出所有交易日
    df_trading = df[df['is_open'] == 1].copy()

    # 将 cal_date 转换为 datetime 类型
    df_trading['cal_date'] = pd.to_datetime(df_trading['cal_date'], format='%Y%m%d')

    # 计算 ISO 年份和周数
    iso_calendar = df_trading['cal_date'].dt.isocalendar()
    df_trading['iso_year'] = iso_calendar.year
    df_trading['iso_week'] = iso_calendar.week

    # 按 ISO 年份和周分组，找到每周的最后交易日
    weekly_last = df_trading.groupby(['iso_year', 'iso_week'])['cal_date'].max().reset_index()

    # 按日期降序排序，获取最近的周
    weekly_last_sorted = weekly_last.sort_values('cal_date', ascending=False)

    # 提取本周和上周的最后一个交易日
    current_week_last = weekly_last_sorted.iloc[0]['cal_date']
    last_week_last = weekly_last_sorted.iloc[1]['cal_date']

    # 格式化为字符串
    current_week_last_str = current_week_last.strftime('%Y%m%d')
    last_week_last_str = last_week_last.strftime('%Y%m%d')

    print(f"本周最后一个交易日: {current_week_last_str}")
    print(f"上周最后一个交易日: {last_week_last_str}")


def stock_performance_combined(ts_code, name, trade_date):
    df_daily = stock_performance(ts_code, trade_date, 'D')
    df_daily['period'] = '日线'
    df_weekly = stock_performance(ts_code, trade_date, 'W')
    df_weekly['period'] = '周线'
    df_monthly = stock_performance(ts_code, trade_date, 'M')
    df_monthly['period'] = '月线'
    # 合并三个df
    df_combined = pd.concat([df_daily, df_weekly, df_monthly], ignore_index=True)
    df_combined['name'] = name
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
        'amount': '成交额 （千元）',
        'period': '数据周期',
        'name': '股票名称'
    }
    df_combined.rename(columns=column_mapping, inplace=True)
    return df_combined