
import trafilatura
from langchain_community.tools import DuckDuckGoSearchResults

def extract_text_with_trafilatura(url):
    """
    用trafilatura爬取url网页正文
    """
    html = trafilatura.fetch_url(url)
    text = trafilatura.extract(html, include_links=False, include_tables=False)
    return text

def search_engine(query, num_results=5) -> list:
    """
    duckduckgo搜素, 然后对每个url进行正文爬取
    """
    search = DuckDuckGoSearchResults(output_format="list", num_results=num_results)
    results = search.invoke(query)
    for index, result in enumerate(results):
        if 'link' in result:
            url = result['link']
            text_content = extract_text_with_trafilatura(url)
        else:
            text_content = ''
        result['content'] = text_content
        result['cite_index'] = index + 1
    return results
