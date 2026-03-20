@echo off
cd /d C:\公司资料\github-trend-analysis

echo [%03/20/2026 Fri% %10:08:29.55%] 开始执行每日任务...

call .venv\Scripts\activate.bat
python src\extract.py
python src\trend_builder.py

echo [%03/20/2026 Fri% %10:08:29.55%] 每日任务执行完成
pause
