# Web UI 自动化测试脚手架

## 项目介绍
基于 Python+pytest+playwright+allure 的 Web UI 自动化测试脚手架，采用 POM 设计模式 + YAML 数据驱动。

## 技术栈
- Python 3.8+
- pytest
- playwright
- allure-pytest
- PyYAML
- POM 设计模式

## 项目结构
```
web_ui_auto_test_scaffold/
├── config/                # 配置目录
│   ├── __init__.py
│   └── config.yaml        # 全局配置文件
├── data/                  # 测试数据目录
│   └── baidu_test_data.yaml  # 测试数据
├── logs/                  # 日志目录
├── pages/                 # POM页面对象
│   ├── __init__.py
│   ├── base_page.py       # 基础页面类
│   └── baidu_page.py      # 百度页面类
├── reports/               # 测试报告
├── screenshots/           # 截图目录
├── testcases/             # 测试用例
│   ├── __init__.py
│   └── test_baidu_search.py
├── utils/                 # 工具类
│   ├── __init__.py
│   └── log_util.py        # 日志工具
├── .gitignore
├── pytest.ini             # pytest配置
├── requirements.txt       # 依赖
├── run_tests.py           # 运行入口
└── README.md              # 说明文档
```

## 快速开始
### 1. 安装依赖
```bash
pip install -r requirements.txt
python -m playwright install
```

### 2. 运行测试
```bash
python run_tests.py
```