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

def generate_keywords(query: str, num: int) -> list:
    now = datetime.now()
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')
    prompt = f"""
    现在时间是：{time_str}，用户提出了下面这个问题：{query}
    请你把这个问题转换成{num}组搜索词用于搜索需要的相关信息，每行一组词，总共{num}行。
    """
    keywords_str = ai_chat(prompt, provider=ModelProvider.ALIYUN)
    keywords = keywords_str.split('\n')
    return keywords

def search_result_clean(results_group: list):
    seen = set()
    unique_results = []
    for item in results_group:
        link = item['link']
        if link not in seen:
            seen.add(link)
            unique_results.append(item)
    # 添加引用下标
    for index, result in enumerate(unique_results):
        result['cite_index'] = index + 1
    return unique_results

def cite_update(text):
    # 提取所有原始引用标签
    orig_labels = re.findall(r'\[\^(\d+)\]', text)

    cite_change = []
    for label in orig_labels:
        if int(label) not in cite_change:
            cite_change.append(int(label))

    # 定义替换函数
    def _replacer(match):
        orig_label = match.group(1)
        return f"[^{cite_change.index(int(orig_label))+1}]"

    return (cite_change, re.sub(r'\[\^(\d+)\]', _replacer, text))

def add_reference(text: str, reference_list: list) -> str:
    '''
    在文本脚注部分添加文献引用

    实现流程：
    1. 更新原文本的引用索引值
    2. 把在reference_list里用到的网页标题和链接添加到文本末尾

    :param text: str - 文本内容
    :param reference_list: list - 引用的文献列表

    :return: str -  原始文本内容和文献合并之后的字符串
    '''
    if not reference_list or not text:
        return text
    references = '\n\n'
    cite_list, text = cite_update(text)
    for index, num in enumerate(cite_list):
        references += f"[^{index+1}]: [{reference_list[num-1]['title']}]({reference_list[num-1]['link']})\n"
    text += references
    return text

def ai_search(query: str, num_keyword: int=2, num_result: int=3):
    '''
    基于AI增强的搜索引擎问答系统

    实现流程：
    1. 关键词生成：通过AI根据query生成{num_keyword}组搜索关键词
    2. 并行搜索：对每个关键词执行网络搜索，获取前{num_result}条结果
    3. 结果整合：清洗合并搜索结果后生成最终prompt，通过AI生成结构化答案
    4. 引用标注：自动添加引用标注并生成参考链接索引

    :param query: str - 待解决的自然语言问题（需保证问题描述的完整性）
    :param num_keyword: int - 生成的关键词组数（建议范围1-5，默认2）
    :param num_result: int - 每组关键词的搜索结果数量（建议范围3-10，默认5）

    :return: dict - 结构化返回结果，包含：
        {
            "query": 原始问题文本,
            "search_result": [
                {
                    "index": 搜索序列号,
                    "keyword": 搜索关键词,
                    "results": [
                        {
                            "title": 结果标题,
                            "link": 来源链接,
                            "snippet": 摘要文本,
                            "date": 发布时间（可选）
                        },...
                    ]
                },...
            ],
            "answer": 带引用标注的完整答案文本（示例格式见Note）
        }

    :raises:
        ValueError - 当num_keyword或num_result为负数时
        SearchEngineError - 依赖的搜索引擎服务异常时

    Note:
        1. 搜索结果会进行去重清洗处理（相同域名过滤）
        2. 引用标注格式为[^n]，参考链接统一添加在答案尾部
        3. 严重依赖 generate_keywords() 和 search_engine() 的实现质量
        4. 时间戳会嵌入prompt中用于时效性判断

    示例输出结构：
        >>> ai_search("量子计算最新进展", 2)
        {
            "query": "量子计算最新进展",
            "search_result": [...],
            "answer": "根据2023年Nature研究[^1]...IBM近日宣布...[^2]。\n\n[^1]: https://...\n[^2]: https://..."
        }
    '''
    now = datetime.now()
    time_str = now.strftime('%Y-%m-%d %H:%M:%S')
    keywords = generate_keywords(query, num_keyword)
    # 最终返回的数据体
    return_json = {'query': query, 'search_result': [], 'answer': ''}
    search_results = []
    for index, keyword in enumerate(keywords):
        keyword: str = keyword.strip()
        logger.info(f"搜索关键词： {keyword}")
        if keyword:
            result_list = search_engine(keyword, num_result)
            return_json['search_result'].append({'index': index, 'keyword': keyword, 'results': result_list})
            search_results += result_list
    unique_results = search_result_clean(search_results)
    final_prompt = f"""
    现在时间是：{time_str}，请结合下面给出的网页搜索结果（注意权衡新闻的时效性），回答一下用户的问题。
    如果引用了搜索结果，请在引用的地方标注来源cite_index,比如[^1][^2]， 注意无需在尾部添加来源。
    用户的问题是：{query}
    网页搜索结果如下：
    {json.dumps(unique_results, ensure_ascii=False)}
    """
    answer = ai_chat(final_prompt, provider=ModelProvider.SILICONFLOW)
    answer = add_reference(answer, unique_results)
    return_json['answer'] = answer
    return return_json

