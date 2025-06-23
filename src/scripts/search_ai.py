from datetime import datetime
from config.fs_config import AI_SEARCH_CARD_ID
from message.feishu.fs_msg_format import plain_text, interactive_card
from services.ai_service import ai_search

import logging
from services.search import SearchResultItem

log = logging.getLogger(__name__)
log.info('imports loaded')


def run(args: list[str]):
    query = args[0]
    res = ai_search(query, 1, 3)
    template_param = {'question': res['query'], 'answer':  res['answer']}
    return interactive_card(AI_SEARCH_CARD_ID, template_param)
