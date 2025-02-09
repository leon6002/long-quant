import logging
from urllib.parse import urlencode
import execjs
import requests


logger = logging.getLogger(__name__)

def hexin():
    #获取hexin-v
    with open("src/crawlers/js/wen.js", "r", encoding="utf-8") as f:
        js = f.read()
    JS = execjs.compile(js)  # 读取时间拼接进入js代码中
    hexin = JS.call("rt.update")
    return hexin

def fecth_tonghuashun(limit):
    """
    爬取同花顺的新闻快讯
    https://news.10jqka.com.cn/realtimenews.html

    Args:
    limit: 一次获取的新闻条数
    """
    # Base URL and parameters
    base_url = "https://news.10jqka.com.cn/tapp/news/push/stock/"
    params = {
        "track": "website",
        "tag": "",
        "page": 1,
        "pagesize": str(limit)
    }
    hexin_v = hexin()
    print(f'hexin_v: {hexin_v}')
    logger.info(f'hexin_v: {hexin_v}')
    # Construct the full URL with query string
    url = f"{base_url}?{urlencode(params)}"

    cookie = f"log=; Hm_lvt_722143063e4892925903024537075d0d=1738981661; Hm_lpvt_722143063e4892925903024537075d0d=1738981661; HMACCOUNT=D0C66494CA745296; Hm_lvt_929f8b362150b1f77b477230541dbbc2=1738981661; Hm_lpvt_929f8b362150b1f77b477230541dbbc2=1738981661; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1738981661; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1738981661; v={hexin_v}"
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9",
        "hexin-v": hexin_v,
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "cookie": cookie
    }

    response = requests.get(url, headers=headers, params=None)
    return response.text


"""
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "referrer": "https://news.10jqka.com.cn/realtimenews.html",
        "referrerPolicy": "strict-origin-when-cross-origin",
"""

res = fecth_tonghuashun(10)
print(res)