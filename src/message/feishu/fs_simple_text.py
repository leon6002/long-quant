import requests
import json
import os
import time
import hashlib
import hmac
import base64
from datetime import datetime
from config.fs_config import WEBHOOK_FS,WEBHOOK_FS_TOKEN

from scripts.get_news import gen_batch_news_content_webhook, gen_news_content, gen_news_content_webhook

"""
飞书webhook机器人推送文本
"""

headers = {"Content-Type": "application/json"}
def push_text_fs(text):
    msg = get_fs_body()
    msg['msg_type'] = "text"
    msg['content'] = {"text": text}
    res = requests.post(WEBHOOK_FS, data=json.dumps(msg, ensure_ascii=False), headers=headers)
    print(res.status_code)
    print(res.text)
    return res.text

def push_card():
    msg = get_fs_body()
    result = gen_batch_news_content_webhook(2)
    #合并这两个dict
    msg = {**msg, **result}
    print(json.dumps(msg, ensure_ascii=False, indent=4))
    res = requests.post(WEBHOOK_FS, data=json.dumps(msg, ensure_ascii=False), headers=headers)
    print(res.status_code)
    print(res.text)
    return res.text

def push_sigle_message_card(title: str, content: str, publish_time: datetime, stocks: str, hot: bool=False):
    msg = get_fs_body()
    result = gen_news_content_webhook(title, content, publish_time, stocks, hot)
    msg = {**msg, **result}
    res = requests.post(WEBHOOK_FS, data=json.dumps(msg, ensure_ascii=False), headers=headers)
    return res.text
def get_fs_body() -> dict:
    timestamp = get_timestamp()
    msg = {"timestamp": timestamp, "sign": gen_sign(timestamp, WEBHOOK_FS_TOKEN)}
    return msg

def get_timestamp():
    # 生成1599360473这种格式的时间戳字符串
    return str(int(time.time()))
def gen_sign(timestamp, secret):
    # 拼接timestamp和secret
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode('utf-8')
    return sign


