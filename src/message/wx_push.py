import asyncio
from datetime import datetime
import requests
from dotenv import load_dotenv
import os
import json
import time
load_dotenv()
url = os.getenv("WEBHOOK_WX")

example_template = {"msgtype":"template_card",
                     "template_card":{
                        "card_type":"text_notice",
                        "source":{
                            "icon_url":"https://wework.qpic.cn/wwpic/252813_jOfDHtcISzuodLa_1629280209/0",
                            "desc":"企业微信",
                            "desc_color":0
                        },
                        "main_title":{
                            "title":"欢迎使用企业微信",
                            "desc":"您的好友正在邀请您加入企业微信"
                        },
                        "emphasis_content":{
                            "title":"100",
                            "desc":"数据含义"
                        },
                        "quote_area":{
                            "type":1,
                            "url":"https://work.weixin.qq.com/?from=openApi",
                            "appid":"APPID",
                            "pagepath":"PAGEPATH",
                            "title":"引用文本标题",
                            "quote_text":"Jack：企业微信真的很好用~\nBalian：超级好的一款软件！"
                        },
                        "sub_title_text":"下载企业微信还能抢红包！",
                        "horizontal_content_list":[
                            {
                                "keyname":"邀请人",
                                "value":"张三"
                            },
                            {
                                "keyname":"企微官网",
                                "value":"点击访问",
                                "type":1,
                                "url":"https://work.weixin.qq.com/?from=openApi"
                            }
                        ],
                        "jump_list":[
                            {
                                "type":1,
                                "url":"https://work.weixin.qq.com/?from=openApi",
                                "title":"企业微信官网"
                            }
                        ],
                        "card_action": {
                            "type": 1,
                            "url": "https://baidu.com"
                        }
                    }
                }
def push_text(text):
    msg_type = "text"
    msg =  {"msgtype": msg_type, "text": {"content": text}}
    headers = {"Content-Type": "application/json"}
    res = requests.post(url, data=json.dumps(msg, ensure_ascii=False), headers=headers)
    print(res.status_code)
    print(res.text)
    return res.text

def push_template(title, desc, timestr):
    template_json = {"msgtype":"template_card",
                     "template_card":{
                        "card_type":"text_notice",
                        "main_title":{
                            "title":title,
                            "desc": timestr
                        },
                        "sub_title_text": desc,
                        "jump_list":[
                            {
                                "type":1,
                                "url":"https://work.weixin.qq.com/?from=openApi",
                                "title":"查看该新闻"
                            }
                        ],
                        "card_action": {
                            "type": 1,
                            "url": "https://baidu.com"
                        }
                    }
                }
    headers = {"Content-Type": "application/json"}

    res = requests.post(url, data=json.dumps(template_json, ensure_ascii=False), headers=headers)
    print(res.status_code)
    print(res.text)
    return res.text

import aiohttp

def push_news(news_list):
    # 按照news['datetime']排序
    news_list = sorted(news_list, key=lambda x: x['datetime'])
    for news in news_list:
        # Asynchronous sleep instead of time.sleep (which is blocking)
        time.sleep(4)  # Reduced slightly since async is non-blocking
        # Call the async version of push_template (assumed to be modified)
        push_template(news['title'], news['content'], datetime.strftime(news['datetime'], '%Y-%m-%d %H:%M:%S'))




if __name__ == "__main__":
    # push_text("你好吗")
    pass