from datetime import datetime
from bson import ObjectId
import pandas as pd
from tqdm import tqdm
from core.analysis import summary
from utils.db_utils import drop_collection, find_collection_data, store_df_to_mongodb, update_by_id
from services.tushare import get_stocks, stock_daily_basic, stock_performance
from config.db import listed_stocks_collection, news_collection_name
import logging


logger = logging.getLogger(__name__)

def update_stocks_data():
    """
    初始化股票基础数据
    """
    df = get_stocks()
    if df.empty:
        logger.error("初始化股票基础数据失败, 未获取到数据，请检查tushare接口")
        return
    now = datetime.now()
    
    def process_row(row):
        row['create_time'] = now
        row['_id'] = str(ObjectId())
        return row
    
    df = df.apply(process_row,axis=1)
    
    drop_collection(listed_stocks_collection)
    store_df_to_mongodb(df, listed_stocks_collection)


def update_none_title(batch_size=5, max_retries=2):
    """
    找出title为空的新闻，用ai根据content内容总结出一个简短的标题，更新回mongodb
    """
    query = {
                '$or': [
                    {'title': {'$exists': False}},
                    {'title': {'$in': [None, '']}}
                ],
                'content': {'$exists': True, '$ne': ''}  # 确保有内容可以生成标题
            }
    news_to_update = find_collection_data(news_collection_name(), query, {}, batch_size)
    if not news_to_update:
        logger.info("没有需要更新标题的新闻")
        return
    for doc in tqdm(news_to_update):
            content = doc['content']
            news_id = doc['_id']

            # 生成标题（需要实现generate_title_by_ai函数）
            for attempt in range(max_retries):
                try:
                    new_title = summary(content)  # 假设的AI生成函数
                    # print(f"id: {news_id} title: {new_title} content: {content}")
                    if new_title:
                        doc['title'] = new_title
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        logger.error(f"为文档 {news_id} 生成标题失败: {str(e)}")
    update_by_id(pd.DataFrame(news_to_update), news_collection_name())


def update_ranked_stock_price():
    stock_rank_collection = 'stock_rank_0208'
    trade_date = '20250207'
    data = find_collection_data(stock_rank_collection)
    if not data:
        logger.info(f"没有stock_rank数据，停止更新价格")
        return
    df = pd.DataFrame(data)
    # 取出df中所有的ts_code,组合成字符串，用逗号分隔
    ts_codes = ','.join(df['ts_code'].astype(str).tolist())
    # 调用tushare接口获取当日的股票价格信息
    price_df = stock_performance(ts_codes=ts_codes, trade_date=trade_date)
    stock_basic_df = stock_daily_basic(ts_codes=ts_codes, trade_date=trade_date)
    # 将price_df中的数据按照ts_code关联添加到df中
    df = pd.merge(df, price_df, on='ts_code', how='left')
    df = pd.merge(df, stock_basic_df, on='ts_code', how='left')
    drop_collection('stock_rank_price_0208')
    store_df_to_mongodb(df, 'stock_rank_price_0208')