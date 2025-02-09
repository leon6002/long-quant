import schedule
import time
from config.base import logger
from core import main
from services.news_service import stock_analyze_prompt  # 导入测试函数
from core.manual import update_stocks_data

def job():
    logger.info("Scheduled job started")
    main()
    logger.info("Scheduled job completed")

def start_job():
    # 立即运行一次任务
    job()
    # 每2分钟执行一次任务
    schedule.every(10).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(10)

def tmp_test():
    # 测试 stock_analyze_prompt 函数
    test_tick = '300251.SZ'  # 股票代码
    test_name = '光线传媒'  # 股票名称
    test_trade_date = '20250207'  # 交易日期

    prompt_result = stock_analyze_prompt(test_tick, test_name, test_trade_date)
    print("测试结果：\n", prompt_result)

def init_stock_info():
    # 获取所有股票基础数据，存进mongodb
    update_stocks_data()

if __name__ == "__main__":
    start_job()