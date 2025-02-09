import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

TUSHARE_TOKEN = os.getenv('TUSHARE_TOKEN')
SILICONFLOW_TOKEN = os.getenv('SILICONFLOW_TOKEN')
ALI_AI_TOKEN= os.getenv("ALI_AI_TOKEN")
DEERAPI_TOKEN= os.getenv("DEERAPI_TOKEN")

# 集中配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)