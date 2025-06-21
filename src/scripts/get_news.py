from datetime import datetime
from services.tushare import news_collection_name
from utils.db_utils import find_collection_latest_data
from message.feishu.fs_msg_format import interactive_card, interactive_card_webhook
import os

def run(command: list) -> None:
    """获取mongodb中最新的新闻记录
    commnad 格式为: 10
    mongodb_latest_news 3
    """
    limit = 3
    # 如果字符串为空
    if len(command) > 0:
        print("command in run is: ", command)
        try:
            limit = int(command[0])
        except ValueError:
            limit = 3
    return gen_news_content(limit)

def gen_news_content(limit: int) -> dict:
    collection_name = news_collection_name()
    print(f'collection_name is {collection_name}')
    news = find_collection_latest_data(collection_name=collection_name, limit=limit)

    card_news = []
    for item in news:
        card_item = gen_news_param(item['title'], item['content'], item['datetime'], item['stocks'], item['hot'] > 0)
        card_news.append(card_item)
    template_param = {"news": card_news}
    return interactive_card(os.getenv("FS_NEWS_CARD_ID"), template_param)

def gen_batch_news_content_webhook(limit: int=3) -> dict:
    collection_name = news_collection_name()
    print(f'collection_name is {collection_name}')
    news = find_collection_latest_data(collection_name=collection_name, limit=limit)

    card_news = []
    for item in news:
        card_item = gen_news_param(item['title'], item['content'], item['datetime'], item['stocks'], item['hot'] > 0)
        card_news.append(card_item)
    template_param = {"news": card_news}
    return interactive_card_webhook(os.getenv("FS_NEWS_CARD_ID"), template_param)

def gen_news_content_webhook(title: str, content: str, publish_time: datetime, stocks: str, hot: bool=False) -> dict:
    card_news = [gen_news_param(title, content, publish_time, stocks, hot)]
    template_param = {"news": card_news}
    return interactive_card_webhook(os.getenv("FS_NEWS_CARD_ID"), template_param)

def gen_news_param(title: str, content: str, publish_time: datetime, stocks: str, hot: bool=False) -> dict:
    if hot:
        title = f"<text_tag color='wathet'>最热</text_tag> **{title}**"
    else:
        title = f"**{title}**"
    card_news_item = {}
    card_news_item["title"] = f"**{title}**"
    card_news_item["content"] = f"{content}"
    card_news_item["publish_time"] = f"{datetime.strftime(publish_time,'%Y-%m-%d %H:%M')}"
    card_news_item['stocks'] = f"<font color='grey'>{stocks}</font>"
    return card_news_item
