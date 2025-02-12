import pandas as pd
from config.ai import ModelProvider
from core.analysis import analyze_stock
from core.news import stock_rank
from crawlers.general import search_engine
from crawlers.tonghuashun.main import fetch_investment_calendar, realtime_news
from crawlers.tonghuashun.tonghuashun import get_SSE_datas, get_favored_sectors, get_glamour_stocks
from maintenance.init_action import init_stock_market_info
from maintenance.manual import batch_analyze_ranked_stock
from services.ai_service import ai_search
from services.news_service import get_stock_news, stock_analyze_prompt
from services.tushare import find_stock_name, get_last_trade_date, get_trade_date_range, realtime_quote, stock_daily_basic, stock_performance, stock_price, trade_calendar
from utils.common import get_date_range, get_today, parse_stock_suggesion
from utils.db_utils import drop_collection, find_collection_data, store_df_to_mongodb, update_by_id
import logging
from pprint import pprint

logger = logging.getLogger(__name__)

def copy_analyze():
    list_old = find_collection_data('stock_rank_0210_s_01',{},{'_id':0, 'rating': 0, 'stock': 0})
    list_new = find_collection_data('stock_rank_0210_s_02')
    print(list_new[0])
    df_old = pd.DataFrame(list_old)
    df_new = pd.DataFrame(list_new)
    df_new = pd.merge(df_new, df_old,  on="ts_code", how='inner')
    update_by_id(df_new, "stock_rank_0210_s_02")

def transfer():
    drop_collection('stock_rank_0210_s_01')
    data = find_collection_data('stock_rank_0210_s_02')
    store_df_to_mongodb(pd.DataFrame(data), 'stock_rank_0210_s_01')
    drop_collection('stock_rank_0210_s_02')



def update_ranked_stock_price():
    # trade_date = get_last_trade_date()
    date = '0211'
    trade_date = f'2025{date}'
    ts_codes = find_collection_data(f'stock_rank_{date}')
    if not ts_codes:
        logger.info(f"没有stock_rank数据，停止更新价格")
        return
    df = pd.DataFrame(ts_codes)
    # 取出df中所有的ts_code,组合成字符串，用逗号分隔
    ts_codes = ','.join(df['ts_code'].astype(str).tolist())
    # 调用tushare接口获取当日的股票价格信息
    price_df = stock_performance(ts_codes=ts_codes, trade_date=trade_date)
    if price_df.empty:
        raise Exception(f"没有{trade_date}这天的股票数据")
    stock_basic_df = stock_daily_basic(ts_codes=ts_codes, trade_date=trade_date)
    if stock_basic_df.empty:
        raise Exception(f"没有{trade_date}这天的基本面数据")
    # 将price_df中的数据按照ts_code关联添加到df中
    df = pd.merge(df, price_df, on='ts_code', how='inner')
    df = pd.merge(df, stock_basic_df, on='ts_code', how='inner')
    drop_collection(f'stock_rank_price_{date}')
    store_df_to_mongodb(df, f'stock_rank_price_{date}')






# rank_stocks = find_collection_data('stock_rank_0210',selection={'ts_code': 1, 'rating': 1})
# print(rank_stocks)

# res = stock_analyze_prompt('002261.SZ')
# # res = analyze_stock('600157.SH', ModelProvider.SILICONFLOW)
# print(res)

if 0:
    update_ranked_stock_price()

if 0:
    find_collection_data('stock_rank_price_0211', selection={})


if 0:
    data_strings = get_favored_sectors()

    for i in range(1, len(data_strings)):
            print("{:d}: {:s}".format(i, data_strings[i-1]))

# 获取同花顺热门股票数据
if 0:
    data_strings = get_glamour_stocks()
    total_rise = 0

    for i in range (1, 10):
            print("{:d}: {:s}\t {:4.1f}%".format(i, data_strings[i-1][0], data_strings[i-1][1]))
            total_rise = total_rise +data_strings[i-1][1]
    average = total_rise/9
    if(average >= 0):
            print("+{:4.1f} %".format(average))
    else:
            print("{:4.1f}%".format(average))

if 1:

    res = ai_search("优刻得-W(SH:688158)这只股票怎么样，明天可以买吗?")

    print(res)

if 0:
    pass