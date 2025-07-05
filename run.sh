#!/bin/bash

# 切换到目标目录
cd /data/project/long-quant || { echo "目录不存在"; exit 1; }

# 拉取最新代码
git pull
if [ $? -ne 0 ]; then
    echo "拉取代码失败"
    exit 1
fi

# 激活虚拟环境
source ./venv/bin/activate
if [ $? -ne 0 ]; then
    echo "激活虚拟环境失败"
    exit 1
fi

# 安装依赖
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "安装依赖失败"
    exit 1
fi

# 运行Python脚本
python3 ./src/main.py
if [ $? -ne 0 ]; then
    echo "Python脚本运行失败"
    exit 1
fi
