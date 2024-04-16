import platform
import subprocess
import time
import re

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# 启动 Chrome 浏览器
def star_Browser(url):
    print("Start the sniffer.")

    # 检测当前操作系统，在命令行中启动 Chrome 浏览器
    current_system = platform.system()
    if current_system == 'Darwin':  # macOS
        chrome_command = 'open -n -a "Google Chrome" --args --remote-debugging-port=9222'
        subprocess.Popen(chrome_command, shell=True)
    elif current_system == 'Windows':  # Windows
        chrome_command = 'start chrome --new-window --remote-debugging-port=9222'
        subprocess.Popen(chrome_command, shell=True)
    else:
        print("Can't launch Chrome browser from the command line on this system.")
        return None
    time.sleep(3)

    # 使用 Selenium 连接到已经打开的 Chrome 浏览器实例
    chrome_options = webdriver.ChromeOptions()
    chrome_options.debugger_address = "127.0.0.1:9222"
    driver = webdriver.Chrome(options=chrome_options)

    # 控制浏览器打开 Amazon 网站
    print("Opening website：", url)
    driver.get(url)
    time.sleep(5)
    return driver

# 设置 Zip Code
def set_Zip_code(driver, zipcode):
    print("Change Zip Code to：", zipcode)
    # 检测 Zip Code 是否正确
    try:
        element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "glow-ingress-line2"))
        )
        text = element.text
        currentZipcode = re.search(r'\b\d{5}\b', text).group(0)
        if currentZipcode == zipcode:
            print("Don't Change Zip Code.")
            return driver
    except Exception as e:
        print("I can't find the specified span tag.", e)
        return None
    
    # 等待 a 标签加载并点击
    try:
        location_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "nav-global-location-popover-link"))
        )
        location_link.click()
        time.sleep(1)
    except Exception as e:
        print("无法找到指定的 a 标签:", e)
        return None

    # 输入指定的 zip code
    try:
        zip_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "GLUXZipUpdateInput"))
        )
        zip_input.clear()
        zip_input.send_keys(zipcode)
        time.sleep(1)
    except Exception as e:
        print("无法找到指定的 input 标签:", e)
        return None

    # 模拟点击应用按钮
    try:
        submit_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "GLUXZipUpdate"))
        )
        submit_button.click()
        time.sleep(1)
        driver.refresh()
        time.sleep(5)
        return driver
    except Exception as e:
        print("无法找到指定的按钮:", e)
        return None


def main():
    driver = star_Browser("https://www.amazon.com")
    driver = set_Zip_code(driver, '10001')

    # 访问指定网址
    if driver:
        url = "https://www.amazon.com/gp/bestsellers/climate-pledge/21377129011/ref=pd_zg_hrsr_climate-pledge"
        driver.get(url)

        # 等待一段时间，然后关闭浏览器
        driver.quit()

if __name__ == "__main__":
    main()

