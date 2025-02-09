listed_stocks_collection = "listed_stocks"

def news_collection_name():
    """
    获取新闻collection名称，格式是news_0207这种
    """
    from datetime import datetime
    now = datetime.now()
    date = now.strftime('%m%d')
    news_collection = f"news_{date}"
    return news_collection