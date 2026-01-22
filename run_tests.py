#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行入口
"""
import os
import sys
import shutil
import subprocess
import importlib


# 校验Python版本（单独校验，不通过pip）
def check_python_version():
    """校验Python版本是否>=3.8"""
    py_version = sys.version_info
    if py_version < (3, 8):
        print(f"❌ Python版本过低: {py_version.major}.{py_version.minor}.{py_version.micro}")
        print("⚠️ 要求Python 3.8及以上版本，请升级Python")
        sys.exit(1)
    else:
        print(f"✅ Python版本符合要求: {py_version.major}.{py_version.minor}.{py_version.micro}")


# 校验核心依赖（跳过python，只校验真正的包）
def check_dependencies():
    """校验关键依赖是否安装"""
    # 移除pytest_rerunfailures，先保证基础运行，后续可选安装
    required_modules = [
        "pytest", "playwright", "yaml", "allure_pytest", "loguru"
    ]
    missing_modules = []

    for module in required_modules:
        try:
            importlib.import_module(module)
        except ImportError:
            missing_modules.append(module)

    if missing_modules:
        print(f"❌ 缺少必要依赖: {', '.join(missing_modules)}")
        print("📦 正在自动安装缺失依赖...")
        try:
            # 使用--user参数解决权限问题，适配Windows
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"],
                check=True,
                capture_output=True,
                text=True
            )
            print("✅ 依赖安装完成")
            # 安装后重新导入
            for module in missing_modules:
                importlib.import_module(module)
        except Exception as e:
            print(f"❌ 依赖安装失败: {e}")
            print("💡 建议手动执行: pip install --user -r requirements.txt")
            sys.exit(1)


# 清理旧报告
def clean_reports():
    """清理旧的测试报告和截图"""
    print("🧹 清理旧报告...")
    # 清理allure报告
    if os.path.exists("reports/allure-results"):
        shutil.rmtree("reports/allure-results")
    if os.path.exists("reports/allure-report"):
        shutil.rmtree("reports/allure-report")
    # 确保目录存在
    os.makedirs("reports/allure-results", exist_ok=True)
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("logs", exist_ok=True)


# 安装playwright浏览器
def install_playwright_browsers():
    """确保playwright浏览器已安装"""
    print("🌐 检查Playwright浏览器...")
    try:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install"],
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ Playwright浏览器已就绪")
    except Exception as e:
        print(f"⚠️ Playwright浏览器安装警告: {e}")
        print("可忽略此警告，后续运行时会自动安装")


# 运行测试（完全移除--reruns依赖）
def run_tests():
    """执行测试用例 - 不依赖rerunfailures插件"""
    print("🚀 开始执行测试用例...")
    # 纯基础pytest命令，不依赖任何插件
    pytest_cmd = [
        sys.executable, "-m", "pytest",
        "-v", "-s",  # 显示详细输出
        "--alluredir=reports/allure-results",  # allure报告
        "testcases/"  # 指定测试目录
    ]

    try:
        # 执行测试
        result = subprocess.run(
            pytest_cmd,
            check=True,
            text=True
        )
        print("✅ 测试用例执行完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 测试执行失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        return False


# 生成allure报告（可选）
def generate_allure_report():
    """生成并打开allure报告"""
    print("📊 生成Allure报告...")
    try:
        # 生成报告
        subprocess.run(
            ["allure", "generate", "reports/allure-results", "-o", "reports/allure-report", "--clean"],
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✅ 报告已生成: {os.path.abspath('reports/allure-report/index.html')}")

        # 尝试打开报告（可选）
        try:
            subprocess.run(["allure", "open", "reports/allure-report"], check=False)
        except:
            print("💡 可手动打开报告: allure open reports/allure-report")
    except FileNotFoundError:
        print("⚠️ 未找到allure命令，跳过报告生成（不影响测试结果）")
        print("💡 安装allure: https://github.com/allure-framework/allure2/releases")
    except Exception as e:
        print(f"⚠️ 报告生成失败: {e}")


if __name__ == "__main__":
    # 切换到脚本所在目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    try:
        # 1. 先校验Python版本
        check_python_version()

        # 2. 校验并安装依赖
        check_dependencies()

        # 3. 清理旧报告
        clean_reports()

        # 4. 安装playwright浏览器
        install_playwright_browsers()

        # 5. 运行测试
        test_success = run_tests()

        # 6. 生成报告（仅当测试执行完成时）
        if test_success:
            generate_allure_report()

        print("\n🎉 测试流程执行结束")

    except KeyboardInterrupt:
        print("\n🛑 用户中断执行")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        sys.exit(1)