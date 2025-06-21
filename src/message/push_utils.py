import datetime

import time
import wx_push



headers = {"Content-Type": "application/json"}

def push_news(news_list):
    for news in news_list:
        wx_push.push_template(news['title'], news['content'], datetime.strftime(news['datetime'], '%Y-%m-%d %H:%M:%S'))
        time.sleep(4)



if __name__ == '__main__':
    pass