import time
import requests
import json
import re
from urllib.parse import urlencode
from datetime import datetime


class EastMoneyCrawler:
    """
    东方财富新闻爬虫
    """

    BASE_URL = "https://np-weblist.eastmoney.com/comm/web/getFastNewsList"

    HEADERS = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "script",
        "sec-fetch-mode": "no-cors",
        "sec-fetch-site": "same-site",
        "Referer": "https://kuaixun.eastmoney.com/7_24.html"
    }

    def __init__(self):
        pass

    def fetch_news(self, limit: int) -> str:
        """
        获取东方财富新闻数据
        """
        timestamp = str(int(time.time() * 1000))
        params = {
            "client": "web",
            "biz": "web_724",
            "fastColumn": "102",
            "sortEnd": "",
            "pageSize": str(limit),
            "req_trace": timestamp,
            "_": timestamp
        }

        url = f"{self.BASE_URL}?{urlencode(params)}"
        response = requests.get(url, headers=self.HEADERS)
        return response.text

    def parse_response(self, text: str) -> list:
        """
        解析返回的JSONP格式数据
        """
        # 处理JSONP包装
        match = re.search(r'\((\{.*\})\)', text)
        if match:
            json_data = json.loads(match.group(1))
        else:
            json_data = json.loads(text)

        # 提取新闻数据
        news_list = []
        for item in json_data['data']['fastNewsList']:
            news_item = {
                "id": item["code"],
                "title": item["title"],
                "content": self.clean_content(item["summary"]),
                "datetime": item["showTime"],
                "src": "eastmoney",
                "hot": item["titleColor"]  # 0表示普通新闻，3表示焦点新闻
            }
            news_list.append(news_item)
        return news_list

    def clean_content(self, content: str) -> str:
        """
        清洗新闻内容
        """
        if content.startswith('【'):
            try:
                pos = content.index('】')
                return content[pos+1:]
            except ValueError:
                pass
        return content

    def get_today_news(self, limit: int = 50) -> list:
        """
        获取当天新闻
        """
        raw_data = self.fetch_news(limit)
        news_list = self.parse_response(raw_data)

        # 过滤当天新闻
        today = datetime.now().strftime("%Y-%m-%d")
        return [news for news in news_list if news.get("datetime", "").startswith(today)]