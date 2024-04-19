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
        # 更新 zip code
        print("Change Zip Code to:", zipcode)
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "glow-ingress-line2"))
            )
            text = element.text
            if text != "Update location":
                current_zipcode = re.search(r'\b\d{5}\b', text).group(0)
                if current_zipcode == zipcode :
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
            time.sleep(5)
        except Exception as e:
            print("I can't find the specified A tag. error:", e)
            return None

        try:
            zip_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "GLUXZipUpdateInput"))
            )
            zip_input.clear()
            zip_input.send_keys(zipcode)
            time.sleep(5)
        except Exception as e:
            print("I can't find the specified Input tag. error:", e)
            return None

        try:
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "GLUXZipUpdate"))
            )
            submit_button.click()
            time.sleep(5)
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

    def load_all_scroll_to_bottom(self, url):
        # 模拟向下滚动网页
        self.driver.get(url)
        print("Loading page：", url)
        time.sleep(5)

        scroll_distance = 600

        while True:
            new_height, last_height = (scroll_distance, self.driver.execute_script("return document.body.scrollHeight"))

            # 执行向下滚动的 JavaScript 代码
            self.driver.execute_script(f"window.scrollTo(0, {scroll_distance});")
            time.sleep(3)

            if new_height > last_height:
                break
            scroll_distance += 600
        
        return

    def get_all_pro_info(self):
        # 执行 javascript 脚本获取商品信息
        div_info = ''
        
        div_elements = self.driver.find_elements_by_class_name("a-declarative")

        # 遍历所有找到的元素
        for div_element in div_elements:
            # 查找当前元素下属性为 name 或者 data-cy 的子元素
            name_elements = div_element.find_elements_by_css_selector('[name]')
            data_cy_elements = div_element.find_elements_by_css_selector('[data-cy="title-recipe"]')

            # 遍历所有属性为 name 或者 data-cy 的子元素
            for name_element in name_elements:
                div_info += name_element.text.strip()

                # 查找国家：查找当前元素下的所有 i 标签
                i_elements = name_element.find_elements_by_tag_name('i')

                # 遍历所有 i 标签
                for i_element in i_elements:
                    # 检查 i 标签的 class 值
                    class_list = i_element.get_attribute("class")

                    # 如果 class 值包含 "flag-icon-cn"，则国家为中国
                    if "flag-icon-cn" in class_list:
                        div_info += '国家: 中国'
                    # 如果 class 值包含 "flag-icon-us"，则国家为美国
                    elif "flag-icon-us" in class_list:
                        div_info += '国家: 美国'
                    # 其他情况，国家为其他
                    else:
                        div_info += '国家: 其他'

            # 查找标题
            for data_cy_element in data_cy_elements:
                h2_elements = data_cy_element.find_elements_by_tag_name('h2')
                for h2_element in h2_elements:
                    a_element = h2_element.find_element_by_tag_name('a')
                    if a_element:
                        div_info += "标题: " + a_element.text.strip() + "\n"
        return div_info

def main():
    HOMEPAGE = "https://www.amazon.com"
    ZIP = "10001"

    amazon_browser = AmazonBrowser(HOMEPAGE)
    amazon_browser.set_zip_code(ZIP)

    # 访问指定网址
    if amazon_browser.driver:
        BSR_URL = "automotive/15707241/ref=pd_zg_hrsr_automotive"
        url = f"{HOMEPAGE}/gp/bestsellers/{BSR_URL}"
        amazon_browser.load_all_scroll_to_bottom(url)

        # 关闭浏览器
        amazon_browser.quit_browser()

if __name__ == "__main__":
    main()
