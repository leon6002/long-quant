import requests
from config.bocha import BOCHA_API_KEY
from models.bocha.search.res import SearchResponse

import trafilatura
from langchain_community.tools import DuckDuckGoSearchResults
import os


headers = {
    'Authorization': f'Bearer {BOCHA_API_KEY}',
    'Content-Type': 'application/json'
}

class SearchResult:
    def __init__(self, items):
        self.items = [SearchResultItem(**item) for item in items]

class SearchResultItem:
    def __init__(self, url: str=None, title: str=None, content: str=None):
        self.url = url
        self.title = title
        self.content = content
        self.cite_index = None

def bocha_search(query: str, count: int = 5) -> SearchResponse | str:
    url = 'https://api.bochaai.com/v1/web-search'
    payload = {
        "query": query,
        "freshness": "noLimit",
        "summary": True,
        "count": count
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    print(f'bocha_search reponse code: {response.status_code}')
    print(f'response text: {response.text}')
    if response.status_code == 200:
        return SearchResponse(**response.json())
    else:
        return response.text

def extract_text_with_trafilatura(url):
    """
    用trafilatura爬取url网页正文
    """
    html = trafilatura.fetch_url(url)
    text = trafilatura.extract(html, include_links=False, include_tables=False)
    return text

class SearchEngine:
    def search(self, query, num_results):
        raise NotImplementedError('子类必须实现此方法')

class DuckDuckGoSearch(SearchEngine):
    def search(self, query: str, num_results: int=5) -> SearchResult:
        search = DuckDuckGoSearchResults(output_format="list", num_results=num_results)
        results = search.run(query)
        search_result = {'items': []}
        for index, result in enumerate(results):
            item = {'url': '', 'content': ''}
            if 'link' in result:
                item['url'] = result['link']
                item['title'] = result['title']
                item['content'] = extract_text_with_trafilatura(result['link'])
            search_result['item'].append(item)
        return SearchResult(**search_result)


class BochaSearch(SearchEngine):
    def search(self, query: str, num_results: int=5) -> SearchResult:
        # 假设 bocha_search 函数已经定义
        results = bocha_search(query, count=num_results)
        search_result = {'items': []}
        for result in results.data.webPages.value:
            item = {
                'url': result.url,
                'content': result.summary,
                'title': result.name
            }
            search_result['items'].append(item)
        return SearchResult(**search_result)

def do_search(query, num_results=5) -> list[SearchResultItem]:
    """
    根据配置选择搜索引擎，然后对每个url进行正文爬取
    """
    search_engine_type = os.getenv('SEARCH_ENGINE', 'duckduckgo')
    if search_engine_type.lower() == 'duckduckgo':
        search = DuckDuckGoSearch()
    elif search_engine_type.lower() == 'bocha':
        search = BochaSearch()
    else:
        raise ValueError(f'不支持的搜索引擎类型: {search_engine_type}')
    search_result = search.search(query, num_results)
    for index, result in enumerate(search_result.items):
        result.cite_index = index + 1
    return search_result.items
