#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础页面类 - 增强等待和重试逻辑，解决超时问题
"""
import os
import time
from playwright.sync_api import Page, expect
from utils.log_util import log
from config import config


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.timeout = config["timeout"]
        self.screenshot_dir = "screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    def goto(self, url):
        """重写goto方法：降低等待条件，延长超时"""
        try:
            # 关键修改：等待条件改为 domcontent loaded，超时设为15秒
            self.page.goto(
                url,
                wait_until="domcontentloaded",  # 替代 networkidle，DOM加载完成即判定成功
                timeout=self.timeout * 1000  # 15秒超时（默认是30秒，这里显式配置）
            )
            log.info(f"【基础层】成功跳转到：{url}")
        except Exception as e:
            log.error(f"页面跳转失败：{e}")
            self.screenshot("goto_fail")
            raise

    def click(self, locator):
        """点击元素 - 先等待元素可点击"""
        try:
            log.info(f"点击: {locator}")
            # 显式等待元素可点击
            expect(self.page.locator(locator)).to_be_enabled(timeout=self.timeout * 1000)
            self.page.locator(locator).click(timeout=self.timeout * 1000)
        except Exception as e:
            log.error(f"点击失败: {e}")
            self.screenshot()
            raise

    def fill(self, locator, text):
        """输入文本 - 先清空再输入，增加重试"""
        max_retry = 2  # 输入失败重试次数
        retry_count = 0

        while retry_count < max_retry:
            try:
                log.info(f"输入: {text} 到 {locator} (重试{retry_count})")
                # 1. 等待元素可见且可输入
                expect(self.page.locator(locator)).to_be_editable(timeout=self.timeout * 1000)
                # 2. 先清空输入框（避免原有内容干扰）
                self.page.locator(locator).clear(timeout=self.timeout * 1000)
                # 3. 缓慢输入（模拟人类操作，避免反爬）
                self.page.locator(locator).type(text, delay=100, timeout=self.timeout * 1000)
                # 4. 验证输入内容正确
                input_text = self.page.locator(locator).input_value()
                if input_text == text:
                    log.info(f"输入成功: {text}")
                    return
                else:
                    log.warning(f"输入内容不匹配，期望:{text} 实际:{input_text}")
            except Exception as e:
                log.warning(f"输入重试{retry_count}失败: {e}")
                self.page.wait_for_timeout(500)  # 重试前等待

            retry_count += 1

        # 所有重试失败
        log.error(f"输入失败（已重试{max_retry}次）: {text} 到 {locator}")
        self.screenshot()
        raise TimeoutError(f"输入超时，重试{max_retry}次仍失败")

    def screenshot(self, prefix="error"):
        """截图保存 - 增加时间戳"""
        path = os.path.join(self.screenshot_dir, f"{prefix}_{time.strftime('%Y%m%d_%H%M%S')}.png")
        self.page.screenshot(path=path, full_page=True)
        log.info(f"截图保存: {path}")
        return path