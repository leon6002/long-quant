from crawlers.eastmoney import EastMoneyCrawler
from .news import save_news_to_db, ai_analysis, stock_rank
import logging
log = logging.getLogger(__name__)

def main():
    # 1. 爬取东方财富新闻
    crawler = EastMoneyCrawler()
    log.info('start crawler')
    news_list = crawler.get_news(limit=5)
    # 存进mongods
    news_dfs = save_news_to_db(news_list)
    # AI分析并存储结果
    for k, v in news_dfs.items():
        if len(v) == 0:
            continue
        ai_analysis(k, v)
        stock_rank(news_collection=k)