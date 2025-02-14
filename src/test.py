from datetime import datetime
import re
import pandas as pd
from config.ai import ModelProvider
from core.analysis import analyze_stock, analyze_stock_no_parse
from core.news import stock_rank, update_ranked_stock_price
from crawlers.general import search_engine
from crawlers.tonghuashun.main import fetch_investment_calendar, realtime_news
from crawlers.tonghuashun.tonghuashun import get_SSE_datas, get_favored_sectors, get_glamour_stocks
from maintenance.init_action import init_stock_market_info
from maintenance.manual import batch_analyze_ranked_stock
from services.ai_service import ai_search, cite_update
from services.news_service import get_stock_news, stock_analyze_prompt
from services.tushare import find_stock_name, get_last_trade_date, get_trade_date_range, realtime_quote, stock_daily_basic, stock_performance, stock_price, trade_calendar
from utils.common import get_date_range, get_today, parse_stock_suggesion, time_now
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










# rank_stocks = find_collection_data('stock_rank_0210',selection={'ts_code': 1, 'rating': 1})
# print(rank_stocks)

# res = stock_analyze_prompt('002261.SZ')
# # res = analyze_stock('600157.SH', ModelProvider.SILICONFLOW)
# print(res)

if 0:
    # 用交易日前一天的新闻验证当天的股价
    # 新闻表格当天应该收录的是前一天15:00到当天15:00的新闻
    update_ranked_stock_price('20250211', '20250212')

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

if 0:
    query = "fen"
    res_json = ai_search(query)
    time = datetime.now()
    time_str = time.strftime('%m%d_%H%M')
    filename = f'{query[:8]}_{time_str}.md'
    save_path = f'/Users/cgl/Library/Mobile Documents/iCloud~md~obsidian/Documents/md/ask_ai/ai_search/{filename}'
    save_content = f"**问题：** {res_json['query']}\n\n"
    save_content += f"{res_json['answer']}"
    with open(save_path, "w") as f:
         f.write(save_content)
    logger.info("AI搜索分析结束，文件已保存")

if 1:
    ts_code= '600728.SH'
    prompt, suggestion=analyze_stock_no_parse(ts_code)
    filename = f'stock_{ts_code[:6]}_{time_now('%m%d_%H%M')}.md'
    save_path = f'/Users/cgl/Library/Mobile Documents/iCloud~md~obsidian/Documents/md/ask_ai/stock_analyze/{filename}'
    save_content = f'# 个股分析：{ts_code}'
    save_content += '\n\n'
    save_content += suggestion
    save_content += '\n\n**提问词：**\n'
    save_content += prompt
    with open(save_path, "w") as f:
         f.write(save_content)