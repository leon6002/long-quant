from datetime import datetime
from dotenv import load_dotenv
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import json

from message.feishu.fs_handler import handle_command
from services.tushare import news_collection_name
from utils.db_utils import find_collection_data
from message.feishu.fs_msg_format import plain_text
from config.fs_config import APP_ID, APP_SECRET

# 注册接收消息事件，处理接收到的消息。
# Register event handler to handle received messages.
# https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/events/receive
def do_p2_im_message_receive_v1(data: P2ImMessageReceiveV1) -> None:
    result = {}
    if data.event.message.message_type == "text":
        command: str = json.loads(data.event.message.content)["text"]
        print(f'command comes: {command}')
        result = handle_command(command)
    else:
        result = plain_text('解析消息失败，请发送文本消息')

    msg_type = result['msg_type']
    content = result['content']

    print(f'chat_type: {data.event.message.chat_type}')
    print(f'message_type: {data.event.message.message_type}')

    if data.event.message.chat_type == "p2p":
        p2p_req(data.event.message.chat_id, msg_type, content)
    else:
        reply_req(data.event.message.message_id, msg_type, content)


# 注册事件回调
# Register event handler.
event_handler = (
    lark.EventDispatcherHandler.builder("", "")
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1)
    .build()
)


# 创建 LarkClient 对象，用于请求OpenAPI, 并创建 LarkWSClient 对象，用于使用长连接接收事件。
# Create LarkClient object for requesting OpenAPI, and create LarkWSClient object for receiving events using long connection.
lark.APP_ID = APP_ID
lark.APP_SECRET = APP_SECRET
client = lark.Client.builder().app_id(lark.APP_ID).app_secret(lark.APP_SECRET).build()
wsClient = lark.ws.Client(
    lark.APP_ID,
    lark.APP_SECRET,
    event_handler=event_handler,
    log_level=lark.LogLevel.DEBUG,
)

def p2p_req(chat_id: str, msg_type: str, content: str) -> None:
    request = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(chat_id)
                .msg_type(msg_type)
                .content(content)
                .build()
            )
            .build()
        )
    # 使用OpenAPI发送消息
    # Use send OpenAPI to send messages
    # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create
    response = client.im.v1.chat.create(request)

    if not response.success():
        raise Exception(
            f"client.im.v1.chat.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )
def reply_req(message_id: str, msg_type: str, content: str):
    request: ReplyMessageRequest = (
            ReplyMessageRequest.builder()
            .message_id(message_id)
            .request_body(
                ReplyMessageRequestBody.builder()
                .msg_type(msg_type)
                .content(content)
                .build()
            )
            .build()
        )
        # 使用OpenAPI回复消息
        # Reply to messages using send OpenAPI
        # https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/reply
    response: ReplyMessageResponse = client.im.v1.message.reply(request)
    if not response.success():
        raise Exception(
            f"client.im.v1.message.reply failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        )


def start_listen_fs():
    #  启动长连接，并注册事件处理器。
    #  Start long connection and register event handler.
    wsClient.start()


if __name__ == "__main__":
    start_listen_fs()
