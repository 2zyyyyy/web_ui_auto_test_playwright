#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
conftest.py - Pytest核心配置文件（全局夹具/钩子函数）
作用：
1. 全局复用的浏览器夹具（反爬配置、启动参数）
2. 测试前后置钩子
3. 自定义命令行参数
4. 测试数据预处理
"""
import pytest
import os
from utils.log_util import log
from playwright.sync_api import sync_playwright, ViewportSize  # 导入ViewportSize类型

# ======================== 全局夹具（核心）========================
@pytest.fixture(scope="session", autouse=True)
def global_session_setup_teardown():
    """全局会话前置/后置（整个测试只执行一次）"""
    log.info("="*50)
    log.info("【全局前置】测试会话开始，初始化环境")
    # 1. 确保必要目录存在
    for dir_name in ["logs", "reports/allure-results", "screenshots"]:
        os.makedirs(dir_name, exist_ok=True)
    # 2. 清理旧的allure报告
    if os.path.exists("reports/allure-report"):
        import shutil
        shutil.rmtree("reports/allure-report")
    yield  # 测试执行阶段
    log.info("【全局后置】测试会话结束，清理环境")
    log.info("="*50)

@pytest.fixture(scope="session")
def browser_page():
    """全局浏览器页面对象（session级别，一次启动，所有用例复用）"""
    log.info("【夹具】启动Playwright浏览器（含反爬配置）")
    # 1. 启动Playwright
    pw = sync_playwright().start()
    # 2. 浏览器启动参数（反爬+稳定性）
    browser = pw.chromium.launch(
        headless=False,          # 可视化运行
        slow_mo=100,             # 模拟人类操作速度
        args=[
            "--disable-blink-features=AutomationControlled",  # 禁用自动化标识
            "--no-sandbox",                                  # 解决沙箱限制
            "--disable-dev-shm-usage"                        # 解决内存不足
            "--disable-images"                               # 可选：禁用图片加载，加速页面
        ]
    )
    # 3. 浏览器上下文配置（反爬核心）
    viewport_size: ViewportSize = {"width": 1920, "height": 1080}
    context = browser.new_context(
        # 用ViewportSize类型定义视口
        viewport=viewport_size,  # 适配主流显示器的最大化尺寸
        # 模拟真实浏览器UA
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        locale="zh-CN",  # 中文环境
        timezone_id="Asia/Shanghai"  # 上海时区
    )

    # 新增：拦截百度的冗余请求（广告/埋点/推荐）
    def block_unnecessary_requests(route, request):
        # 拦截的请求类型：广告、埋点、视频、图片（可根据需要调整）
        blocked_urls = [
            "baidu.com/ads",
            "baidu.com/trace",
            "baidu.com/recommend",
            "google-analytics.com",
            "doubleclick.net"
        ]
        if any(url in request.url for url in blocked_urls):
            route.abort()  # 拦截请求
        else:
            route.continue_()  # 允许正常请求

    # 启用请求拦截
    context.route("**/*", block_unnecessary_requests)

    # 4. 禁用webdriver标识（反爬关键）
    context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'chrome', {get: () => ({runtime: {}})});
        window.navigator.languages = ['zh-CN', 'zh'];
    """)
    # 5. 创建页面对象
    page = context.new_page()
    # 通过 page.evaluate 执行JS最大化窗口,原理：在页面中执行JavaScript，强制浏览器窗口最大化（适配所有浏览器/版本）
    page.evaluate("""() => {
            window.moveTo(0, 0);
            window.resizeTo(screen.width, screen.height);
        }""")

    yield page  # 返回页面对象给测试用例
    # 6. 测试结束后清理资源
    log.info("【夹具】关闭Playwright浏览器")
    page.close()
    context.close()
    browser.close()
    pw.stop()


@pytest.fixture(scope="function")
def case_setup_teardown(browser_page, request):  # 新增request夹具（Pytest原生）
    """
    每个测试用例的前置/后置
    - 使用request.fixture name/request.node获取用例信息，替代自定义属性
    """
    # 获取当前测试用例的名称（核心修复：用request替代pytest.current_test_name）
    current_case_name = request.node.nodeid  # 完整用例路径（如testcases/test_baidu_search.py::TestBaiduSearch::test_search_3rd_result）

    # 用例前置
    log.info(f"【用例前置】开始执行用例：{current_case_name}")
    browser_page.reload()  # 每次用例前刷新页面
    yield  # 执行用例逻辑

    # 用例后置
    log.info(f"【用例后置】结束执行用例：{current_case_name}")

# ======================== Pytest钩子函数（扩展）========================
# 在 conftest.py 中注册 smoke 标记
def pytest_configure(config):
    # smoke标记
    config.addinivalue_line("markers", "smoke: 冒烟测试用例")  # 注册冒烟标记

# 其他钩子函数（删除pytest_runtest_setup，无需再自定义current_test_name）
def pytest_collection_modifyitems(items):
    """解决中文用例名乱码（不变）"""
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeId = item.nodeid.encode("utf-8").decode("unicode_escape")

def pytest_runtest_setup(item):
    """钩子函数：每个用例执行前记录用例名"""
    pytest.current_test_name = item.nodeid

def pytest_addoption(parser):
    """钩子函数：自定义命令行参数（比如指定测试环境）"""
    parser.addoption(
        "--env",
        action="store",
        default="test",
        help="指定测试环境：test（测试）/prod（生产）"
    )

@pytest.fixture(scope="session")
def env(request):
    """夹具：获取自定义的--env参数"""
    return request.config.getoption("--env")