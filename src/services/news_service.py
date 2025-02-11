from bson import Regex
import pandas as pd
from crawlers.general import search_engine
from utils.common import get_today
from utils.db_utils import find_collection_data
from services.tushare import find_stock_name, get_last_trade_date, get_trade_date_range, realtime_quote, stock_daily_basic, stock_price, trade_calendar


def get_stock_news(name: str) -> pd.DataFrame:
    query = {"stocks": {"$regex": Regex(name)}}
    projection = {
        "_id": 0,
        "title": 1,
        "content": 1
    }
    news_list = find_collection_data('news_0209', query, projection, 10)
    return pd.DataFrame(news_list)
def search(name):
    search_results = search_engine(f'{name} {get_today()} 股票新闻 ')
    res = ''
    for index, item in enumerate(search_results):
        res += f'cite_index: {index+1} \n'
        res += f'标题：\n {item['title']} \n'
        res += f'链接：{item['link']} \n'
        res += f'内容：\n {item['content']} \n\n'
    return res

def stock_analyze_prompt(ts_code):
    name = find_stock_name(ts_code)
    if not name:
        return None
    df_realtime = realtime_quote(ts_code, True)
    df_daily = stock_price(ts_code, get_trade_date_range(10), 'D', True)
    df_weekly = stock_price(ts_code, get_trade_date_range(31), 'W', True)
    df_basic = stock_daily_basic(ts_code, get_last_trade_date(), column_rename=True)
    # df_basic = stock_daily_basic(ts_code, '20250210', column_rename=True)
    df_news = get_stock_news(name)
    df_news = df_news.rename(columns={"title": '新闻标题', 'content': '新闻内容'})
    prompt = '根据下面的股票数据和新闻，分析一下投资建议，严格按照给定的格式给出结论：\n\n'
    prompt += f'股票名称： {name}({ts_code})\n\n'
    prompt += f'股票当前实时数据：\n'
    prompt += df_realtime.to_markdown(index=False)
    prompt += '\n\n'
    prompt += '股票最近一个交易日基本面数据：\n\n'
    prompt += df_basic.to_markdown(index=False)
    prompt += '\n\n'
    prompt += '股票最近五个交易日的日线数据：\n\n'
    prompt += df_daily.head(5).to_markdown(index=False)
    prompt += '\n\n'
    prompt += '股票最近一个月周线数据：\n\n'
    prompt += df_weekly.head(5).to_markdown(index=False)
    prompt += '\n\n'
    prompt += '最近几天相关的新闻：\n\n'
    prompt += df_news.to_markdown(index=False)
    prompt += '\n\n'
    prompt += '网页搜索相关信息：\n\n'
    prompt += search(name)
    prompt += '\n\n'
    prompt += '给出的结论格式：\n短期: <买入、观望或者卖出>\n理由: <理由>\n中期: <买入、观望或者卖出>\n理由: <理由>\n长期: <买入、观望或者卖出>\n理由: <理由>'
    return prompt