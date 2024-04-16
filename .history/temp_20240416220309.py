import subprocess
import time
from selenium import webdriver

# 在命令行中启动 Chrome 浏览器
chrome_command = 'open -a "Google Chrome" --args --remote-debugging-port=9222'
subprocess.Popen(chrome_command, shell=True)

# 等待一段时间确保 Chrome 浏览器已经完全打开
time.sleep(5)

# 使用 Selenium 连接到已经打开的 Chrome 浏览器实例
chrome_options = webdriver.ChromeOptions()
chrome_options.debugger_address = "127.0.0.1:9222"
driver = webdriver.Chrome(options=chrome_options)

# 控制浏览器打开 Amazon 网站
driver.get("https://www.amazon.com")

# 在这里可以继续添加其他操作，对已经打开的浏览器进行控制

# 最后关闭浏览器
# driver.quit()
