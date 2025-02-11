
import pandas as pd
from config.ai import ModelProvider
from core.analysis import analyze_stock
from utils.db_utils import drop_collection, find_collection_data, store_df_to_mongodb, update_by_id
from services.tushare import  stock_daily_basic, stock_performance, stock_price
import logging
import concurrent.futures


logger = logging.getLogger(__name__)



def batch_analyze_ranked_stock():
    collection = 'stock_rank_0210_s_01'
    stocks = find_collection_data(collection, {
        '$or': [
            {'prompt': None},
            {'prompt': {'$type': 'double', '$exists': True}}
        ]
    }, limit=10)
    if not stocks:
        logger.info(f"没有stock_rank数据，停止分析")
        return

    # 使用多线程共同处理 stocks
    num_threads = 5  # 设置线程数量
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for stock in stocks:
            # 每个线程处理一个股票，并指定 ModelProvider
            futures.append(executor.submit(_analyze_single_stock, stock, ModelProvider.SILICONFLOW))

        # 等待所有线程完成
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # 如果有异常会在这里抛出
            except Exception as e:
                logger.error(f"线程执行出错: {e}")

    update_by_id(pd.DataFrame(stocks), collection)


def _analyze_single_stock(stock, model_provider):
    """
    分析单个股票数据。
    :param stock: 单个股票数据字典
    :param model_provider: 当前线程使用的 ModelProvider
    """
    logger.info(f'analyzing for stock: {stock["stock"]} using {model_provider}')
    res = analyze_stock(stock['ts_code'], model_provider)
    stock['prompt'] = res[0]
    analyze_res = res[1]
    for k, v in analyze_res.items():
        stock[k] = v