from datetime import datetime
from bson import ObjectId
import pandas as pd
from tqdm import tqdm
from core.analysis import summary
from utils.db_utils import drop_collection, find_collection_data, store_df_to_mongodb, update_by_id
from services.tushare import get_stocks
from config.db import listed_stocks_collection, news_collection_name
import logging

logger = logging.getLogger(__name__)

def init_stock_market_info():
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
        row['type'] = stock_type(row['ts_code'])
        return row

    df = df.apply(process_row,axis=1)

    drop_collection(listed_stocks_collection)
    store_df_to_mongodb(df, listed_stocks_collection)


def stock_type(ts_code: str):
    # Mapping of prefixes to stock types
    stock_type_mapping = {
        ('300', '301'): '创业板',
        ('688', '689'): '科创板',  # 科创板股票代码以“688”开头，存托凭证以“689”开头
        ('000', '001', '002', '003'): '深市主板',
        ('600', '601', '603', '605'): '沪市主板',
        ('400', '430', '830'): '新三板',
        ('8', '9'): '北交所',
    }

    # Check each mapping for a matching prefix
    for prefixes, stock_type_name in stock_type_mapping.items():
        if any(ts_code.startswith(prefix) for prefix in prefixes):
            return stock_type_name

    return '未知'

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

