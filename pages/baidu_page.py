#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pages.base_page import BasePage
from config import config
from utils.log_util import log
from playwright.sync_api import expect


class BaiduPage(BasePage):
    # 适配最新百度搜索框（textarea标签）
    SEARCH_INPUT = '//textarea[@id="chat-textarea"]'  # 新搜索框核心定位器
    SEARCH_BTN = '//@id="chat-submit-button"]'  # 新搜索按钮
    SEARCH_RESULT_TITLE = "//div[@id='content_left']//h3/a"

    def __init__(self, page):
        super().__init__(page)
        self.url = config["base_url"]
        self.timeout = 10  # 从3秒改为10秒，适配百度动态加载

    def open(self):
        """打开百度首页，激活新的textarea搜索框"""
        self.goto(self.url)  # 调用BasePage的goto（domcontentloaded+15秒超时）

        # 等待新搜索框DOM出现
        self.page.wait_for_selector(self.SEARCH_INPUT, timeout=self.timeout * 1000)

        # 激活新搜索框（textarea和input操作逻辑一致）
        search_box = self.page.locator(self.SEARCH_INPUT)
        search_box.scroll_into_view_if_needed()
        search_box.click()  # 强制激活，触发显隐逻辑
        expect(search_box).to_be_editable(timeout=self.timeout * 1000)  # 断言可编辑
        log.info("【核心层】百度首页加载完成，新搜索框已激活")

    def search(self, keyword):
        """执行关键词搜索（适配textarea）"""
        try:
            search_box = self.page.locator(self.SEARCH_INPUT)
            # 二次激活+输入
            search_box.click()
            search_box.clear()  # textarea支持clear方法
            search_box.type(keyword, delay=200)  # 放慢输入，适配反爬

            # 优先按回车搜索（避免按钮定位失效）
            search_box.press("Enter")

            # 等待搜索结果加载
            expect(self.page.locator("#content_left")).to_be_visible(timeout=self.timeout * 1000)
            log.info(f"【核心层】完成关键词搜索：{keyword}")
        except Exception as e:
            log.error(f"搜索失败：{e}")
            self.screenshot("search_fail")
            raise

    def click_result(self, index):
        """点击指定索引的搜索结果（逻辑不变）"""
        try:
            result_count = self.page.locator(self.SEARCH_RESULT_TITLE).count()
            if result_count < index:
                raise ValueError(f"搜索结果数量不足：仅找到{result_count}条，需点击第{index}条")

            target_locator = f"({self.SEARCH_RESULT_TITLE})[{index}]"
            expect(self.page.locator(target_locator)).to_be_visible(timeout=self.timeout * 1000)
            self.page.locator(target_locator).scroll_into_view_if_needed()
            self.page.wait_for_timeout(500)
            self.click(target_locator)
            log.info(f"【核心层】成功点击第{index}条搜索结果")
            self.page.wait_for_load_state("networkidle")
        except Exception as e:
            log.error(f"点击结果失败：{e}")
            self.screenshot(f"click_result_{index}_fail")
            raise