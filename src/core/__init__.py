from crawlers.eastmoney import EastMoneyCrawler
from .news import save_news_to_db, ai_analysis, stock_rank


def main():
    # 1. 爬取东方财富新闻
    crawler = EastMoneyCrawler()
    news_list = crawler.get_today_news(limit=50)
    # 存进mongods
    news_df = save_news_to_db(news_list)
    # AI分析并存储结果
    ai_analysis(news_df)
    # 更新股票排名
    stock_rank()
