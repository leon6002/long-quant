from collections import defaultdict
from datetime import datetime
import re
import pandas as pd
from tqdm import tqdm
from config.db import listed_stocks_collection
from core.analysis import analyze_news
from services.tushare import get_last_trade_date, news_collection_name, stock_daily_basic, stock_performance
from utils.db_utils import drop_collection, find_collection_data, store_df_to_mongodb, update_by_id
from utils.common import process_news, time_now
import logging


logger = logging.getLogger(__name__)

def save_news_to_db(news_list) -> None:
    """
    将新闻存进数据库
    """
    if not news_list:
        logger.info("news_list为空，没有新记录需要插入到MongoDB")
    news_list = process_news(news_list)
    groups = {}
    dfs = {}
    # 新闻所影响的交易日
    for news in tqdm(news_list):
        if news:
            name = news_collection_name(news['datetime'])
            if name not in groups.keys():
                groups[name] = [news]
            else:
                groups[name].append(news)
    for k, v in groups.items():
        dfs[k] = store_df_to_mongodb(pd.DataFrame(v), k)
    return dfs


def ai_analysis(collection: str, news_df: pd.DataFrame) -> None:
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
    update_by_id(news_df, collection)


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
        if score < 0 or score >= 0.9:
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


def stock_rank(trade_date: str=None) -> None:
    """
    根据新闻计算出股票排名
    trade_date: 指定trade_date, 格式是'%Y%m%d'， 比如20250217
    """
    logger.info('开始股票排名')
    if trade_date is None:
        news_collection = news_collection_name()
    else:
        news_collection = news_collection_name(datetime.strptime(trade_date, '%Y%m%d'))
    rank_collection = news_collection.replace('news_', 'stock_rank_')
    # 计算股票排名
    rank_data = aggregate_stocks_rating(news_collection)
    integrated_rank_data = stock_rank_data_integrate(rank_data)
    if integrated_rank_data.empty:
        logger.info("没有股票排名数据")
        return
    # 整合基础信息
    stock_list = integrated_rank_data['ts_code'].to_list()
    query = {'ts_code': {'$in': stock_list}}
    selection = {'industry': 1, 'ts_code': 1, '_id': 0, 'type': 1}
    listed_stocks = find_collection_data(listed_stocks_collection, query=query, selection=selection)
    integrated_rank_data = pd.merge(integrated_rank_data, pd.DataFrame(listed_stocks), on='ts_code', how='inner')
    # 存储排名
    drop_collection(rank_collection)
    store_df_to_mongodb(integrated_rank_data,rank_collection)
    logger.info(f"已存储股票排名数据")

def update_ranked_stock_price(news_date, trade_date):
    """
    更新昨日价格
    """
    ts_codes = find_collection_data(f"stock_rank_{news_date[4:]}")
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
    drop_collection(f"stock_rank_price_{trade_date[4:]}")
    store_df_to_mongodb(df, f"stock_rank_price_{trade_date[4:]}")