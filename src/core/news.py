from collections import defaultdict
import re
import pandas as pd
from config.db import news_collection_name, listed_stocks_collection
from core.analysis import analyze_news
from utils.db_utils import drop_collection, find_collection_data, store_df_to_mongodb, update_by_id
from utils.common import process_news
import logging


logger = logging.getLogger(__name__)

def save_news_to_db(news_list):
    """
    将新闻存进数据库
    """
    if not news_list:
        logger.info("news_list为空，没有新记录需要插入到MongoDB")
    news_list = process_news(news_list)
    # 保存新闻到数据库
    return store_df_to_mongodb(pd.DataFrame(news_list), news_collection_name())


def ai_analysis(news_df: pd.DataFrame):
    """
    对新闻进行ai分析，并将结果保存到mongodb

    Args:
    news_df: 已经存进mongodb的新闻，包含_id字段，因为会通过_id直接更新db
    """
    news_count = len(news_df)
    if news_count == 0:
        logger.info("没有新闻流程结束")
        return
    logger.info(f"待分析的新闻数量: {news_count}")

    def process_row(row):
        logger.info(f"analyzing: { row['title']}")
        result = analyze_news(row['title'], row['content'], row['datetime'])
        row['stocks'] = result['stocks']
        row['sectors'] = result['sectors']
        row['rating'] = result['rating']
        return row

    news_df = news_df.apply(process_row,axis=1)
    # 根据_id字段将ai分析出来的数据更新到mongodb
    update_by_id(news_df, news_collection_name())


def combine_stocks_analysis(news_collection):
    data = find_collection_data(news_collection)
    if not data:
        return None
    # 获取指定数量的未处理文档
    df = pd.DataFrame(data)
    stocks_combined = ''
    # 检查是否存在'stocks'列
    if 'stocks' in df.columns:
        # 将所有'stocks'字段的值合并成一个字符串
        stocks_combined = '\n'.join(df['stocks'].dropna().astype(str))
    else:
        logger.error("DataFrame中不存在'stocks'列")
    return stocks_combined


def aggregate_stocks_rating(news_collection):
    data = combine_stocks_analysis(news_collection)
    if data is None:
        return pd.DataFrame()
    # 使用正则表达式提取股票名称和分数
    pattern = r"([\u4e00-\u9fa5A-Za-z]+)\(\d+\)\s+(-?\d+\.\d+)"
    matches = re.findall(pattern, data)

    # 存储聚合结果
    stock_data = defaultdict(lambda: {"total_score": 0, "count": 0})

    # 遍历匹配结果，进行聚合
    for name, score in matches:
        score = float(score)
        stock_data[name]["total_score"] += score
        stock_data[name]["count"] += 1

    # 计算每个股票的平均分数，并按总分数排序
    sorted_stocks = sorted(
        stock_data.items(),
        key=lambda x: x[1]["total_score"],
        reverse=True
    )

    # 输出结果
    results = []
    for stock, data in sorted_stocks:
        result = {"stock": stock, "rating": round(data['total_score'], 2)}
        results.append(result)
    return pd.DataFrame(results)


def stock_rank_data_integrate(rank_data: pd.DataFrame):
    if rank_data.empty:
        return pd.DataFrame()
    # 获取上市正常交易的股票基本信息列表
    active_stocks = find_collection_data(listed_stocks_collection,
                                                 {},
                                                 {'_id': 0, 'name': 1, 'ts_code': 1})
    # 创建一个字典来存储股票名称和ts_code的映射
    stock_map = {}
    for stock in active_stocks:
        stock_map[stock['name']] = stock['ts_code']

    # 筛选rank_data并添加ts_code字段
    def process_row(row):
        if row['stock'] in stock_map:
            row['ts_code'] = stock_map[row['stock']]
            return row
        return None

    rank_data = rank_data.apply(process_row, axis=1).dropna()

    return rank_data.reset_index(drop=True)


def stock_rank() -> None:
    news_collection = news_collection_name()
    rank_collection = news_collection.replace('news_', 'stock_rank_')
    # 计算股票排名
    rank_data = aggregate_stocks_rating(news_collection)
    integrated_rank_data = stock_rank_data_integrate(rank_data)
    if integrated_rank_data.empty:
        logger.info("没有股票排名数据")
        return
    # 整合基础信息
    stock_list = integrated_rank_data['ts_code'].to_list()
    listed_stocks = find_collection_data(listed_stocks_collection, query={'ts_code': {'$in': stock_list}}, selection={'industry': 1, 'ts_code': 1, '_id': 0, 'type': 1})
    integrated_rank_data = pd.merge(integrated_rank_data, pd.DataFrame(listed_stocks), on='ts_code', how='inner')
    # 存储排名
    drop_collection(rank_collection)
    store_df_to_mongodb(integrated_rank_data,rank_collection)
    logger.info(f"已存储股票排名数据")