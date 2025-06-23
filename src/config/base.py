import os
import logging




PAGE_SIZE=int(os.getenv("PAGE_SIZE", 20))
JOB_FREQUENCY=int(os.getenv("JOB_FREQUENCY", 5))
SEARCH_ENGINE=os.getenv("SEARCH_ENGINE", "bocha")

# 集中配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(filename)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)