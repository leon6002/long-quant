from datetime import datetime, timedelta
import re
import pandas as pd
import hashlib
from config.base import logger
from dateutil.relativedelta import relativedelta


def process_news(news_list):
    """
    对news做一些预处理

    """
    # 生成MD5作为唯一ID
    try:
        seen_ids = set()  # 用于跟踪当前批次内的重复ID
        unique_records = []
        for record in news_list:
            if 'datetime' in record and isinstance(record['datetime'], str):
                try:
                    # 尝试解析带有秒的日期时间格式
                    record['datetime'] = datetime.strptime(
                        record['datetime'],
                        '%Y-%m-%d %H:%M:%S'
                    )
                except ValueError:
                    # 如果失败，尝试解析不带秒的日期时间格式
                    record['datetime'] = datetime.strptime(
                        record['datetime'],
                        '%Y-%m-%d %H:%M'
                    )
                except (ValueError, TypeError) as e:
                    logger.error(f"日期转换失败: {str(e)}，原始值: {record['datetime']}")
            if 'content' not in record:
                raise ValueError("news_list必须包含'content'字段")
            # 生成content的MD5哈希作为_id
            content_hash = hashlib.md5(record['content'].encode()).hexdigest()
            # 先检查当前批次内是否重复
            if content_hash in seen_ids:
                continue
            seen_ids.add(content_hash)

            # 添加插入时间字段
            record['insert_time'] = datetime.now()
            record['_id'] = content_hash
            unique_records.append(record)
        return unique_records
    except Exception as e:
        logger.error(f"数据预处理失败: {e}")
        return


def compute_timedelta(n):
    """
    计算最近n分钟的时间范围。

    参数:
        n (int): 分钟数

    返回:
        tuple: 包含起始时间和结束时间的元组，格式为('YYYY-MM-DD HH:MM:SS', 'YYYY-MM-DD HH:MM:SS')
    """
    now = datetime.now()
    start_time = now - timedelta(minutes=n)
    start_date = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_date = now.strftime('%Y-%m-%d %H:%M:%S')
    return (start_date, end_date)


def remove_duplicate(df: pd.DataFrame) -> pd.DataFrame:
    """Removes duplicate rows from a DataFrame and provides cleanup feedback.

    Args:
        df: Input DataFrame containing potential duplicate rows.

    Returns:
        pd.DataFrame: Cleaned DataFrame with duplicates removed and index reset.

    Note:
        Prints detailed information about the deduplication process including:
        - Original row count
        - Number of duplicate rows detected
        - Number of rows removed
        - Final row count after cleanup
    """
    original_row_count = len(df)
    logger.info(f"Original number of rows: {original_row_count}")

    duplicated_count = df.duplicated().sum()
    logger.info(f"Number of duplicate rows found: {duplicated_count}")

    # Perform deduplication and reset index
    df_cleaned = df.drop_duplicates().reset_index(drop=True)

    # Calculate actual removed rows (accounts for multiple duplicates per row)
    removed_rows = original_row_count - len(df_cleaned)
    logger.info(f"Number of duplicate rows removed: {removed_rows}")
    logger.info(f"New number of rows after removing duplicates: {len(df_cleaned)}")

    return df_cleaned


def print_news_df(df):
    """
    打印DataFrame中的新闻内容及舆情分析结果。

    参数:
        df (DataFrame): 新闻数据集
    """
    if not df.empty:
        for index, row in df.iterrows():
            logger.info(f"标题：{row['title']}")
            logger.info(f"内容：{row['content']}")
            logger.info(f"发布时间：{row['datetime']}")
            # 打印舆情分析结果
            sentiment = row.get('sentiment', None)
            if sentiment:
                logger.info(f"分析结果：{sentiment['result']}")
                # logger.info(f"积极得分：{sentiment['positive']:.4f}")
                # logger.info(f"消极得分：{sentiment['negative']:.4f}")
                logger.info(f"情绪类别：{sentiment['sentiment']}\n")
            else:
                logger.info("舆情分析结果未获取到\n")
    else:
        logger.info("没有新闻数据")

def parse_stock_suggesion(text):
    actions = []
    reasons = []
    lines = text.split('\n')
    for line in lines:
        line: str = line.strip()
        if not line:
            continue
        if line.startswith('理由'):
            reasons.append(line.replace('理由:', '').strip())
        elif line.startswith('短期') or line.startswith('中期') or line.startswith('长期'):
            actions.append(line.split(' ')[1].strip())
        else:
            continue
    return {'short_term_action': actions[0],
     'short_term_reason': reasons[0],
     'medium_term_action': actions[1],
     'medium_term_reason': reasons[1],
     'long_term_action': actions[2],
     'long_term_reason': reasons[2],
    }

def parse_result(result):
    """
    解析模型返回的结果字符串，并将其转换为结构化数据。
    """
    # 初始化字段
    rating = None
    sectors = []
    stocks = []

    lines = result.split('\n')
    for line in lines:
        line: str = line.strip()
        if not line:
            continue
        # 提取整体评分
        if line.startswith('整体评分:'):
            try:
                rating = float(line.replace("整体评分:", "").strip())
            except ValueError:
                logger.error("解析评分失败")
                rating = None  # 如果无法解析，保留为 None

        # 提取主要板块
        elif line.startswith('主要板块:'):
            try:
                sector_info = line.replace("主要板块:", "").strip()
                sectors_str = sector_info.split(',')
                for s in sectors_str:
                    s = s.strip()
                    if ':' in s:
                        sector, sentiment = s.split(':')
                        sectors.append({
                            'sector': sector.strip(),
                            'sentiment': sentiment.strip()
                        })
            except Exception as e:
                logger.error(f"解析主要板块出错：{str(e)}")


        # 提取具体股票
        elif line.startswith('具体股票:'):
            try:
                stock_info = line.replace("具体股票:", "").strip()
                stock_strs = stock_info.split(';')
                for s in stock_strs:
                    s = s.strip()
                    if ':' in s:
                        stock_part, reason_part = s.split(':', 1)
                        stock_name_code = stock_part.strip().split('(')
                        if len(stock_name_code) == 2:
                            stock_name = stock_name_code[0].strip()
                            stock_code = stock_name_code[1].replace(')', '').strip()
                        else:
                            stock_name = stock_name_code[0].strip()
                            stock_code = None
                        sentiment_part = reason_part.split(',')[0].strip()
                        reason = ','.join(reason_part.split(',')[1:]).strip() if len(reason_part.split(',')) > 1 else ''
                        stocks.append({
                            'stock_name': stock_name,
                            'stock_code': stock_code,
                            'sentiment': sentiment_part.strip(),
                            'reason': reason
                        })
            except Exception as e:
                logger.error(f"解析具体股票出错：{str(e)}")
    stock_result = ""
    sector_result = ""
    for stock in stocks:
        stock_result += f"{stock['stock_name']}({stock['stock_code']}) {stock['sentiment']} {stock['reason']}\n"
    for sector in sectors:
        sector_result += f"{sector['sector']} {sector['sentiment']}\n"
    return {
        'rating': rating,
        'sectors': sector_result,
        'stocks': stock_result
    }

def get_date_range(n: int=1):
    """
    获取最近n个月的开始结束日期
    """
    # 获取当前日期
    today = datetime.today()

    # 计算两个月前的日期
    two_months_ago = today - relativedelta(months=n)

    # 格式化日期为字符串形式 YYYYMMDD
    start_date = two_months_ago.strftime('%Y%m%d')
    end_date = today.strftime('%Y%m%d')

    # 返回结果元组
    return (start_date, end_date)

def get_today():
    today = datetime.today()
    return today.strftime('%Y年%m月%d日')

def time_now(format: str='%Y-%m-%d %H:%M:%S') -> str:
    now = datetime.now()
    return now.strftime(format)