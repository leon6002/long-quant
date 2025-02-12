from datetime import datetime
import json
import re
from openai import  OpenAI

from config.ai import MODEL_CONFIG, ModelProvider
from crawlers.general import search_engine
import logging

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = "You are a helpful assistant."

def create_client(provider: ModelProvider) -> OpenAI:
    """Create OpenAI client for specified provider"""
    config = MODEL_CONFIG.get(provider)
    if not config:
        raise ValueError(f"Unsupported provider: {provider}")

    return OpenAI(
        api_key=config["api_key"],
        base_url=config["base_url"]
    )

def ai_chat(prompt, system=SYSTEM_PROMPT, provider: ModelProvider = ModelProvider.ALIYUN) -> str:
    client = create_client(provider)
    config = MODEL_CONFIG[provider]
    response = client.chat.completions.create(
            model=config['model'],
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
    return response.choices[0].message.content

def ai_chat_json(prompt, response_format, system=SYSTEM_PROMPT, provider: ModelProvider = ModelProvider.ALIYUN):
    client = create_client(provider)
    config = MODEL_CONFIG[provider]
    response = client.beta.chat.completions.parse(
            model=config['model'],
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ],
            response_format=response_format
        )
    return response.choices[0].message.content

def ai_search(query):
    now = datetime.now()
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')
    prompt_search_keyword = f'现在时间是：{time_str}，用户提出了下面这个问题，请你把这个问题转换成两组搜索词用于搜索需要的相关信息，每行一组词，总共两行。用户的问题是：\n{query}'
    keywords_str = ai_chat(prompt_search_keyword, provider=ModelProvider.ALIYUN)

    results_group = []
    for keyword in keywords_str.split('\n'):
        logger.info(f'搜索关键词： {keyword}')
        results = search_engine(keyword, 5)
        results_group += results
    seen = set()
    unique_web = []
    for item in results_group:
        # 假设item是字典，使用item['link']；若是对象，改为item.link
        link = item['link']
        if link not in seen:
            seen.add(link)
            unique_web.append(item)
    for index, result in enumerate(unique_web):
        result['cite_index'] = index + 1
    result_integrate_prompt = f'''
    现在时间是：{time_str}，请结合下面给出的网页搜索结果，回答一下用户的问题。
    如果引用了搜索结果，请标注来源cite_index,比如[cite_1][ciite_2]。
    用户的问题是：{query}
    网页搜索结果如下：
    {json.dumps(unique_web, ensure_ascii=False)}
    '''
    logger.info(f'result_integrate_prompt: {result_integrate_prompt}')
    answer = ai_chat(result_integrate_prompt, provider=ModelProvider.SILICONFLOW)
    # Extract the citation numbers into a list
    citation_numbers = [int(match.group(1)) for match in re.finditer(r'\[cite_(\d+)\]', answer)]
    
    # Replace the citation markers with the corresponding formatted strings
    answer = re.sub(r'\[cite_(\d+)\]', lambda match: f'[来源{match.group(1)}]', answer)

    source_mark = '\n\n'

    for num in citation_numbers:
        source_mark += f'搜索来源{num}: [{unique_web[num-1]['title']}]({unique_web[num-1]['link']})\n'
    answer += source_mark
    return answer

