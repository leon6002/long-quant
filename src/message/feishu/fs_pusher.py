
import os
import json
from datetime import datetime, timezone, timedelta

import lark_oapi as lark
from lark_oapi.api.im.v1 import *
from lark_oapi.api.application.v6 import *
from lark_oapi.event.callback.model.p2_card_action_trigger import (
    P2CardActionTrigger,
    P2CardActionTriggerResponse,
)
NEWS_CARD_ID = "AAqdnSk0lPq0v"
def send_news_card(open_id, news):

    card_news = []
    for item in news:
        card_news_item = {}
        card_news_item["title"] = f"**{item['title']}**"
        card_news_item["content"] = f"{item['content']}"
        card_news_item["publish_time"] = f"{item['publish_time']}"
        card_news_item['stocks'] = f"<font color='grey'>{item['stocks']}</font>"
        card_news.append(card_news_item)
    content = json.dumps(
        {
            "type": "template",
            "data": {
                "template_id":  NEWS_CARD_ID,
                "template_variable": {"news": card_news},
            },
        }
    )
    return send_message("open_id", open_id, "interactive", content)
def send_message(receive_id_type, receive_id, msg_type, content):
    request = (
        CreateMessageRequest.builder()
        .receive_id_type(receive_id_type)
        .request_body(
            CreateMessageRequestBody.builder()
            .receive_id(receive_id)
            .msg_type(msg_type)
            .content(content)
            .build()
        )
        .build()
    )

    # 使用发送OpenAPI发送通知卡片，你可以在API接口中打开 API 调试台，快速复制调用示例代码
    # Use send OpenAPI to send notice card. You can open the API debugging console in the API interface and quickly copy the sample code for API calls.
    # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
    response = client.im.v1.message.create(request)
    if not response.success():
        raise Exception(
            f"client.im.v1.message.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )
    return response


if __name__ == "__main__":
    open_id = ""
    news = [{
        "title": "沪深两市成交额破1万亿元大资金进场？新增非银存款十年新高！",
        "content": "近日，央行公布的5月金融数据显示，非银存款单月增加1.19万亿元。这一数据是2016年以来同比的最高值。其实4月份，非银存款单月增加额是1.57万亿元，也是近十年同比的最高值。也就是说，今年4月、5月连续2个月非银存款的单月增加额，都是十年来同比的最高点。",
        "publish_time": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M"),
        "stocks": "中信证券(600030) 0.90 资金流入利好\n中国平安(601318) 0.82 非银存款增加提升投资预期\n招商银行(600036) 0.70 金融数据改善支撑股价\n"
    }]
    send_news_card(open_id, news)