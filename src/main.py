import multiprocessing
import threading
import schedule
import time
from config.base import logger
import config.base
import core
from message.feishu.fs_listener import start_listen_fs
from concurrent.futures import ThreadPoolExecutor
import config


def job():
    logger.info("Scheduled job started")
    try:
        core.main()
    except Exception as e:
        logger.error("unknown exception", e)
    logger.info("Scheduled job completed")

def start_job():
    # 立即运行一次任务
    job()
    # 每2分钟执行一次任务
    schedule.every(config.base.JOB_FREQUENCY).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(10)

def main():
    # Start start_job in a separate thread
    job_thread = threading.Thread(target=start_job, daemon=True)
    job_thread.start()

    # To avoid event loop conflict, use multi-processing instead of threading:
    fs_process = multiprocessing.Process(target=start_listen_fs)
    fs_process.start()

    # Keep main thread alive
    try:
        job_thread.join()
        fs_process.join()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        fs_process.terminate()
        fs_process.join()



if __name__ == "__main__":
    main()
    # start_listen_fs()