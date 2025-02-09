import os
from dotenv import load_dotenv
from enum import Enum
from typing import Dict, Any

# Load environment variables from .env file
load_dotenv()

TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN')
SILICONFLOW_TOKEN = os.getenv('SILICONFLOW_TOKEN')
ALI_AI_TOKEN= os.getenv("ALI_AI_TOKEN")
DEERAPI_TOKEN= os.getenv("DEERAPI_TOKEN")

class ModelProvider(Enum):
    ALIYUN = "aliyun"
    SILICONFLOW = "siliconflow"
    DEERAPI = "deerapi"
    OLLAMA_REASON = "ollama_reason"
    OLLAMA_FAST = "ollama_fast"

MODEL_CONFIG: Dict[ModelProvider, Dict[str, str]] = {
    ModelProvider.SILICONFLOW: {
        "model": "Pro/deepseek-ai/DeepSeek-R1",
        "base_url": "https://api.siliconflow.cn/v1",
        "api_key": SILICONFLOW_TOKEN
    },
    ModelProvider.ALIYUN: {
        "model": "qwen-max-2025-01-25",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key": ALI_AI_TOKEN
    },
    ModelProvider.DEERAPI: {
        "model": "deepseek-reasoner",
        "base_url": "https://api.deerapi.com/v1",
        "api_key": DEERAPI_TOKEN
    },
    ModelProvider.OLLAMA_FAST: {
        "model": "qwen2.5:latest",
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama"
    },
    ModelProvider.OLLAMA_REASON: {
        "model": "deepseek-r1:32b",
        "base_url": "https://sgym.guliucang.com:3090/v1",
        "api_key": "ollama"
    }
}

# 默认的ai服务商
DEFAULT_MODEL_PROVIDER = ModelProvider.ALIYUN