import time
import schedule
from extract import run_daily_collection
from trend_builder import build_history_table


def daily_job():
    print("开始执行每日采集任务...")
    run_daily_collection(topic="llm", per_page=20)
    build_history_table()
    print("每日任务执行完成")


def main():
    # 每天早上 08:00 执行
    schedule.every().day.at("08:00").do(daily_job)

    print("定时任务已启动：每天 08:00 自动执行")
    print("按 Ctrl+C 可停止任务")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()