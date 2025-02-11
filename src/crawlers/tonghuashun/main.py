import logging
from urllib.parse import urlencode
import requests
from crawlers.tonghuashun import headers
import requests

from bs4 import BeautifulSoup
from pprint import pprint
import logging


logger = logging.getLogger(__name__)

def realtime_news(limit):
    """
    爬取同花顺的新闻快讯
    https://news.10jqka.com.cn/realtimenews.html

    Args:
    limit: 一次获取的新闻条数
    """
    base_url = "https://news.10jqka.com.cn/tapp/news/push/stock/"
    params = {
        "track": "website",
        "tag": "",
        "page": 1,
        "pagesize": str(limit)
    }
    url = f"{base_url}?{urlencode(params)}"
    response = requests.get(url, headers=headers())
    return response.text

def fetch_investment_calendar():
    """
    获取投资日历， 如下：
    === 日期: 2025年02月10日 ===
    事件 1:
    标题: 国务院关税税则委员会：对原产于美国的部分进口商品加征10%或15%的关税
    影响板块: 影响板块:自由贸易港


    事件 2:
    标题: 比亚迪召开智能化战略发布会
    影响板块: 影响板块:无人驾驶


    事件 3:
    标题: 法国人工智能峰会t
    影响板块: 影响板块:人工智能


    === 日期: 2025年02月11日 ===
    事件 1:
    标题: 特斯拉上海储能超级工厂举行投产仪式
    影响板块: 影响板块:特斯拉概念储能
    """

    url = 'https://news.10jqka.com.cn/realtimenews.html'

    try:
        response = requests.get(url, headers=headers())
        response.raise_for_status()  # 检查请求是否成功，如果失败则抛出异常
    except requests.exceptions.RequestException as e:
        logger.error(f"无法获取网页内容：{e}")
        return

    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')

    tzrl_lists = soup.find_all('div', class_='tzrlList')

    result = ""

    for tzrl_list in tzrl_lists:
        # 提取日期信息
        date_div = tzrl_list.find('div', class_='tzrlTit')
        if date_div:
            current_date = date_div.get_text().strip()
            result += f"=== 日期: {current_date} ===\n"

        # 提取每个事件的信息
        content_divs = tzrl_list.find_all('div', class_='tzrlContent')
        for idx, content_div in enumerate(content_divs):
            event_info = {}

            # 提取标题
            title_tag = content_div.find('a', class_='aTit')
            if title_tag:
                event_info['标题'] = title_tag.get_text().strip()

            # 提取影响板块
            affect_span = content_div.find('span', class_='affect')
            if affect_span:
                event_info['影响板块'] = affect_span.get_text().strip()

            # 输出当前事件信息
            result += f"事件 {idx + 1}:\n"
            for key, value in event_info.items():
                result += f"{key}: {value}\n"
            result += "\n"
    print(result)