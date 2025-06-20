import pymongo
from pymongo import MongoClient, UpdateOne
import pandas as pd
from bson import ObjectId
import logging
from config.base import MONGODB_URI, MONGODB_NAME
from config.db import trade_calendar_collection
from message.wx_push import push_news
# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_client():
    """获取MongoDB客户端连接"""
    return MongoClient(MONGODB_URI)


def drop_collection(collection_name):
    with get_client() as client:
        db = client[MONGODB_NAME]
        collection = db[collection_name]
        collection.drop()


def store_df_to_mongodb(df: pd.DataFrame, collection_name: str) -> pd.DataFrame:
    """
    将DataFrame数据存储到MongoDB集合
    df可以没有"_id"字段，如果没有会自动生成一个

    Args:
        df: 要存储的DataFrame
        collection_name: 目标集合名称

    Raises:
        ValueError: 如果DataFrame中缺少content字段
    """
    # 参数验证
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df参数必须是pandas DataFrame")
    if not collection_name:
        raise ValueError("数据库名和集合名不能为空")
    if df is None or df.empty:
        logger.info("df为空，没有数据需要插入到MongoDB")
        return df
    # 使用上下文管理器处理MongoDB连接
    with get_client() as client:
        db = client[MONGODB_NAME]
        collection = db[collection_name]
        records = df.to_dict('records')
        # 获取现有ID集合
        existing_ids = set(collection.distinct('_id'))
        inserted_records = []
        bulk_ops = []
        # 准备批量操作
        for record in records:
            if '_id' not in record.keys() or record['_id'] is None:
                record['_id'] = str(ObjectId())
            if record['_id'] not in existing_ids:
                bulk_ops.append(pymongo.InsertOne(record))
                # Update the original DataFrame with the new _id
                inserted_records.append(record)
        if bulk_ops:
            try:
                result = collection.bulk_write(bulk_ops, ordered=False)
                logger.info(f"成功插入 {result.inserted_count} 条记录到 MongoDB: {collection_name}")
            except pymongo.errors.BulkWriteError as bwe:
                logger.error(f"批量写入错误: {bwe.details}")
        else:
            logger.info(f"没有新记录需要插入到MongoDB: {collection_name}")
        df = pd.DataFrame(inserted_records)
    if inserted_records:
        push_news(inserted_records)
    return df


def find_collection_data(collection_name, query={}, selection={}, limit=0):
    with get_client() as client:
        db = client[MONGODB_NAME]
        collection = db[collection_name]
        data = list(collection.find(query, selection).limit(limit))
        return data

def find_trade_calendar_min_max():
    with get_client() as client:
        db = client[MONGODB_NAME]
        collection = db[trade_calendar_collection]
        # 通过聚合查询获取最大最小值
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "max_time": {"$max": "$cal_time"},
                    "min_time": {"$min": "$cal_time"}
                }
            }
        ]
        result = list(collection.aggregate(pipeline))
        if result:
            max_time = result[0]["max_time"]
            min_time = result[0]["min_time"]
            return min_time, max_time
        else:
            return None, None

def update_by_id(df, collection_name):
    # 根据df中的_id字段更新mongodb中对应的数据

    with get_client() as client:
        db = client[MONGODB_NAME]
        collection = db[collection_name]
        try:
            # 将DataFrame转换为字典列表
            records = df.to_dict('records')

            # 创建批量更新操作
            bulk_ops = [
                UpdateOne(
                    {'_id': record['_id']},  # 查询条件
                    {'$set': {k: v for k, v in record.items() if k != '_id'}}  # 更新内容，排除_id字段
                )
                for record in records if '_id' in record
            ]

            # 执行批量更新
            if bulk_ops:
                result = collection.bulk_write(bulk_ops)
                logger.info(f"成功更新 {result.modified_count} 条记录")
            else:
                logger.warning("没有需要更新的记录")
        except Exception as e:
            logger.error(f"更新失败: {e}")