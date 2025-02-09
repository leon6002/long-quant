# Long-Quant 项目

## 项目简介

本项目是一个用于量化分析的Python应用程序，旨在通过爬取金融数据并进行分析，帮助用户做出更明智的投资决策。

## 目录结构

```python
.
├── .gitignore
├── LICENSE
├── README.md
├── requirements.txt
├── myenv/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── ai.py
│   │   ├── base.py
│   │   └── db.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── analysis.py
│   │   └── news.py
│   ├── crawlers/
│   │   ├── __init__.py
│   │   ├── eastmoney.py
│   │   ├── tonghuashun.py
│   │   └── js/
│   │       └── wen.js
│   ├── maintenance/
│   │   └── manual.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── stock.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py
│   │   ├── news_service.py
│   │   └── tushare.py
│   └── utils/
│       ├── __init__.py
│       ├── common.py
│       └── db_utils.py
└── tests/
```

## 安装指南

1. 克隆本仓库：

   ```bash
   git clone https://github.com/yourusername/long-quant.git
   ```

2. 创建虚拟环境（可选）：

   ```bash
   python -m venv myenv
   source myenv/bin/activate
   ```

3. 安装依赖项：

   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

运行主程序：

```bash
python src/main.py
```

## 配置文件

配置文件位于`src/config/`目录下，您可以根据需要修改相关配置。

## 贡献

欢迎贡献代码和提交问题。请确保您的代码符合项目的编码规范，并在提交前进行充分测试。

## 许可证

本项目采用MIT许可证。详情请参阅[LICENSE](LICENSE)文件。
