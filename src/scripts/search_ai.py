from datetime import datetime
from message.feishu.fs_msg_format import plain_text
from services.ai_service import ai_search

import logging
from services.search import SearchResultItem

log = logging.getLogger(__name__)
log.info('imports loaded')


def run(args: list[str]):
    query = args[0]
    content = ai_search(query)
    return plain_text(content)

def ai_search_workflow(query):
    res_json = ai_search(query, 1, 3)
    references_content = ''
    save_content = f"**问题：** {res_json['query']}\n\n"
    save_content += f"{res_json['answer']}"
    search_result = res_json['search_result']
    references_content = ''
    for s in search_result:
           references_content += f"### 搜索词：{s['keyword']}\n\n"
           for r in s['results']:
                r: SearchResultItem
                references_content += f"标题: {r.title}\n\n"
                references_content += f"来源链接: {r.url}\n\n"
                references_content += f"内容: {r.content}\n\n"
    return references_content
