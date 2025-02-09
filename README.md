# AI选股

## 项目目录结构

```python
src/
  __init__.py
  config/
    __init__.py
    base.py      # 基础配置
    db.py        # 数据库配置
    ai.py        # AI服务配置

  core/         # 核心业务逻辑
    __init__.py
    news.py     # 新闻处理
    stock.py    # 股票分析
    analysis.py # 数据分析

  services/     # 外部服务接口
    __init__.py
    tushare.py  # Tushare API
    tonghuashun.py # 同花顺API

  utils/        # 工具函数
    __init__.py
    db_utils.py # 数据库工具
    ai_utils.py # AI工具
    common.py   # 通用工具

  crawlers/     # 爬虫模块
    __init__.py
    eastmoney.py # 东方财富爬虫

  models/       # 数据模型
    __init__.py
    stock.py    # 股票模型
    news.py     # 新闻模型

tests/          # 单元测试
  __init__.py
  test_core.py
  test_services.py
  test_utils.py
```
