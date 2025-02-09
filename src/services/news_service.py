from bson import Regex
import pandas as pd
from utils.db_utils import find_collection_data
from services.tushare import stock_daily_basic, stock_performance_combined


def get_stock_news(name):
    query = {"stocks": {"$regex": Regex(name)}}
    projection = {
        "_id": 0,
        "title": 1,
    }
    news_list = find_collection_data('news_0209', query, projection, 10)
    df = pd.DataFrame(news_list)
    df = df.rename(columns={"title": '新闻标题',})
    result = df.to_markdown(index=False)
    return result


def stock_analyze_prompt(tick, name, trade_date):
    prompt = '根据下面的股票数据和新闻，分析一下投资建议，严格按照给定的格式给出结论：\n'
    df_performance = stock_performance_combined(tick, name, trade_date)
    df_basic = stock_daily_basic(tick, trade_date)
    prompt += '股票日线周线月线数据：\n'
    prompt += df_performance.to_markdown(index=False)
    prompt += '\n\n'
    prompt += '股票当日基本面数据：\n'
    prompt += df_basic.to_markdown(index=False)
    prompt += '\n\n'
    prompt += '最近几天相关的新闻：\n'
    prompt += get_stock_news(name)
    prompt += '\n\n'
    prompt += '''给出的结论格式：
            短期: [买入、观望或者卖出] [理由]
            中期: [买入、观望或者卖出] [理由]
            长期: [买入、观望或者卖出] [理由]
            '''
    return prompt