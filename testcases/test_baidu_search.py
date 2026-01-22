#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
业务测试层：仅验证业务逻辑，调用夹具和POM，无任何底层配置
"""
import pytest
import yaml
import allure
import os
from pages.baidu_page import BaiduPage
from utils.log_util import log


# 加载测试数据（纯业务数据，无配置）
def load_test_data():
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "baidu_test_data.yaml")
    with open(data_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["test_data"]


test_data = load_test_data()


@allure.epic("百度搜索测试")
class TestBaiduSearch:
    # 仅调用夹具，不关心浏览器如何启动/配置
    @pytest.mark.parametrize("data", test_data)
    def test_search_3rd_result(self, browser_page, data):
        """
        职责：仅验证“百度搜索第三条结果”的业务逻辑
        无任何浏览器配置、反爬代码，完全解耦
        """
        try:
            baidu = BaiduPage(browser_page)  # 传入夹具的页面对象

            with allure.step("打开百度首页"):
                baidu.open()  # 调用POM的业务方法

            with allure.step(f"搜索关键词：{data['keyword']}"):
                baidu.search(data["keyword"])  # 调用POM的业务方法
                assert browser_page.locator(baidu.SEARCH_INPUT).first.input_value() == data["keyword"]

            with allure.step(f"点击第{data['index']}条结果"):
                result_count = browser_page.locator("//div[@id='content_left']//h3/a").count()
                assert result_count >= data["index"]
                baidu.click_result(data["index"])

            log.info(f"【业务测试层】测试通过：{data['keyword']}")
        except Exception as e:
            log.error(f"【业务测试层】测试失败：{e}")
            raise