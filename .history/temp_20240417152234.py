import re
import time
import platform
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class AmazonBrowser:
    def __init__(self, url):
        # 启动 Chrome 浏览器
        self.driver = self._start_browser(url)

    def _start_browser(self, url):
        print("Start the sniffer.")
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

    def set_zip_code(self, zipcode):
        print("Change Zip Code to:", zipcode)
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "glow-ingress-line2"))
            )
            text = element.text
            current_zipcode = re.search(r'\b\d{5}\b', text).group(0)
            if current_zipcode == zipcode:
                print("Don't Change Zip Code.")
                return self.driver
        except Exception as e:
            print("I can't find the specified span tag. error:", e)
            return None
        
        try:
            location_link = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "nav-global-location-popover-link"))
            )
            location_link.click()
            time.sleep(1)
        except Exception as e:
            print("I can't find the specified A tag. error:", e)
            return None

        try:
            zip_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "GLUXZipUpdateInput"))
            )
            zip_input.clear()
            zip_input.send_keys(zipcode)
            time.sleep(1)
        except Exception as e:
            print("I can't find the specified Input tag. error:", e)
            return None

        try:
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "GLUXZipUpdate"))
            )
            submit_button.click()
            time.sleep(1)
            self.driver.refresh()
            time.sleep(5)
            return self.driver
        except Exception as e:
            print("I can't find the specified button. error:", e)
            return None

    def quit_browser(self):
        if self.driver:
            self.driver.quit()
            print("Browser closed.")

def main():
    amazon_browser = AmazonBrowser()
    amazon_browser.set_zip_code("10001")

    # 访问指定网址
    if amazon_browser.driver:
        HOMEPAGE = "https://www.amazon.com"
        BSR_URL = "climate-pledge/21377129011/ref=pd_zg_hrsr_climate-pledge"
        url = f"{HOMEPAGE}/gp/bestsellers/{BSR_URL}"
        amazon_browser.driver.get(url)
        time.sleep(5)

        # 关闭浏览器
        amazon_browser.quit_browser()

if __name__ == "__main__":
    main()
