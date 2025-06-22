import os
import logging




PAGE_SIZE=os.getenv("PAGE_SIZE", 20)
JOB_FREQUENCY=os.getenv("JOB_FREQUENCY", 5)

# 集中配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(filename)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)