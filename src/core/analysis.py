import re
from typing import Dict, Any
from services.ai_service import ai_chat
from services.news_service import stock_analyze_prompt
from utils.common import parse_result, parse_stock_suggesion
from config.ai import DEFAULT_MODEL_PROVIDER, ModelProvider
import logging


logger = logging.getLogger(__name__)

def analyze_news(
    title: str,
    content: str,
    time: str,
    provider: ModelProvider=DEFAULT_MODEL_PROVIDER
) -> Dict[str, Any]:
    """分析新闻对股票市场的影响

    Args:
        title: 新闻标题
        content: 新闻内容
        time: 发布时间
        provider: 模型提供商 (默认: 阿里云)

    Returns:
        解析后的情感分析结果

    Raises:
        ValueError: 输入参数无效时
        APIError: API调用失败时
    """
    # 输入验证
    if not all([title, content, time]):
        raise ValueError("Missing required parameters")


    system = "你是一个专业的股票分析师"
    prompt = f"""请严格按照以下格式分析新闻对A股的影响，并仅返回结果部分（无需任何额外解释）：
                1. 整体影响评分（-1到1，保留两位小数）；
                2. 受影响的主要股票板块（最多列出3个，标明评分， -1到1，保留两位小数）；
                3. 具体受影响股票（每只股票后标明评分， -1到1，保留两位小数，标明理由，最多5只）。

                新闻信息：
                标题: {title}
                内容: {content}
                发布时间: {time}

                请按以下格式输出结果:
                整体评分: [数字]
                主要板块: [板块1: 数字], [板块2: 数字], ...
                具体股票: [股票名称(代码): 数字, 理由], ...

                示例输出:
                整体评分: 0.67
                主要板块: 消费电子: 0.66, 新能源汽车: 0.73
                具体股票: 宁德时代(300750): 0.89, 预计需求增长; 比亚迪(002594): 0.78, 市场份额提升...
                """

    res_text = ai_chat(prompt, system, provider)
    res_text = re.sub(r'<think>.*?</think>', '', res_text, flags=re.DOTALL)
    return parse_result(res_text)

def analyze_stock(ts_code, provider: ModelProvider):
    prompt = stock_analyze_prompt(ts_code)
    res_text = ai_chat(prompt, provider=provider)
    res_text = re.sub(r'<think>.*?</think>', '', res_text, flags=re.DOTALL)
    logger.info(res_text)
    return (prompt, parse_stock_suggesion(res_text))

def summary(content: str) -> str:
    """
    AI根据内容生成标题
    使用本地ollama模型
    """
    prompt = f'请为以下内容生成一个简短且精准的标题。要求仅返回标题内容，不需要其他解释或修饰。\n\n示例：\n输入：如何制作一杯美味的卡布奇诺咖啡\n输出：制作卡布奇诺咖啡的方法\n\n当前内容：{content}'
    res_text = ai_chat(prompt, provider=ModelProvider.OLLAMA_FAST)
    res_text = re.sub(r'<think>.*?</think>', '', res_text, flags=re.DOTALL)
    res_text = res_text.strip()
    return res_text