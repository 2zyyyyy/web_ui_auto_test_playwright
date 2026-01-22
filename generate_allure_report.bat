@echo off
chcp 65001 >nul 2>&1
echo ========================
echo 🔧 配置 Java 环境...
echo ========================
:: 替换成你的 Java 路径
set JAVA_HOME=C:\Users\2zyyy\scoop\apps\temurin17-jdk\current
set Path=%JAVA_HOME%\bin;%Path%

echo ========================
echo 📊 生成并打开 Allure 报告...
echo ========================
:: 替换成你的 Allure 和项目路径
D:\project\tool\allure-2.36.0\bin\allure.bat serve D:\project\playwright\web_ui_auto_test_playwright\reports\allure-results

echo ========================
echo ✅ 报告已关闭，按任意键退出...
echo ========================
pause >nul