import schedule
import time
from config.base import logger
from core import main

def job():
    logger.info("Scheduled job started")
    main()
    logger.info("Scheduled job completed")

def start_job():
    # 立即运行一次任务
    job()
    # 每2分钟执行一次任务
    schedule.every(2).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(5)

if __name__ == "__main__":
    start_job()