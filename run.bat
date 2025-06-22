@echo off
REM 切换到目标目录
cd /d E:\projects\long-quant

REM 环境变量
set HTTP_PROXY=http://127.0.0.1:7897
set HTTPS_PROXY=http://127.0.0.1:7897

REM 拉取最新代码
git pull
if %errorlevel% neq 0 (
    echo Failed to pull latest code.
    exit /b %errorlevel%
)

REM 激活虚拟环境
call .\venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Failed to activate virtual environment.
    exit /b %errorlevel%
)

REM 安装依赖
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    exit /b %errorlevel%
)

REM 删除前面设置的代理变量
set HTTP_PROXY=
set HTTPS_PROXY=

REM 运行 Python 脚本
python .\src\main.py
if %errorlevel% neq 0 (
    echo Python script failed.
    exit /b %errorlevel%
)

REM 保持窗口打开以便查看输出（可选）
pause