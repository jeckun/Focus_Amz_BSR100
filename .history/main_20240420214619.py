import re
import time
import platform
import subprocess
import configparser
import pandas as pd
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from Collating_Best_Sellers_ranking_data import parse_string_to_dict, sort_dict

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
            element = self.find_element_by_id("glow-ingress-line2")
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
            location_link = self.find_element_by_id("nav-global-location-popover-link")
            location_link.click()
            time.sleep(5)
        except Exception as e:
            print("I can't find the specified A tag. error:", e)
            return None

        try:
            zip_input = self.find_element_by_id("GLUXZipUpdateInput")
            if not zip_input:
                change = self.find_element_by_id("GLUXChangePostalCodeLink")
                change.click()
                zip_input = self.find_element_by_id("GLUXZipUpdateInput")
            zip_input.clear()
            zip_input.send_keys(zipcode)
            time.sleep(5)
        except Exception as e:
            print("I can't find the specified Input tag. error:", e)
            return None

        try:
            submit_button = self.find_element_by_id("GLUXZipUpdate")
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
    
    def load_page(self, url):
        self.driver.get(url)
        print("Loading page：", url)
        time.sleep(5)

    def webpage_scroll_to_bottom(self):
        # 模拟向下滚动网页
        scroll_distance = 800

        while True:
            new_height, last_height = (scroll_distance, self.driver.execute_script("return document.body.scrollHeight"))

            # 执行向下滚动的 JavaScript 代码
            self.driver.execute_script(f"window.scrollTo(0, {scroll_distance});")
            time.sleep(1)

            if new_height > last_height:
                break
            scroll_distance += 600
        
        time.sleep(5)
        return
    
    def find_element_by_id(self, id=""):
        try:
            element = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, id))
            )
            return element
        except Exception as e:
            return None

    @staticmethod
    def find_element_by_classname(es, class_name="", attribute="innerText"):
        try:
            element = es.find_element(By.CLASS_NAME, class_name)
            return element.get_attribute(attribute)
        except Exception as e:
            return None

    @staticmethod
    def find_element_by_xpath(es, xpath="", attribute="innerText"):
        try:
            element = es.find_element(By.XPATH, xpath)
            return element.get_attribute(attribute)
        except Exception as e:
            return None
    
    def parse_asin(self, grid_item):
        return self.find_element_by_xpath(grid_item, ".//div[@data-asin]", "data-asin")
    
    def parse_bsr(self, grid_item):
        # 获取BSR信息的文本内容
        bsr_text = self.find_element_by_classname(grid_item, "zg-bdg-text")
        if bsr_text:
            bsr_value = re.search(r'#(\d+(,\d+)*)', bsr_text).group(1)
        else:
            bsr_value = ''
        return bsr_value
    
    def parse_title(self, grid_item):
        title = self.find_element_by_classname(grid_item, "_cDEzb_p13n-sc-css-line-clamp-3_g3dy1")
        if title:
            return title
        else:
            return self.find_element_by_classname(grid_item, "_cDEzb_p13n-sc-css-line-clamp-4_2q2cc")

    @staticmethod
    def parse_main_img(grid_item):
        try:
            # 查找具有class="a-section a-spacing-mini _cDEzb_noop_3Xbw5"的div元素
            div_with_class = grid_item.find_element(By.CSS_SELECTOR, ".a-section.a-spacing-mini._cDEzb_noop_3Xbw5")
            # 查找div元素下的img标签
            img_tag = div_with_class.find_element(By.TAG_NAME, "img")
            # 获取img标签的src属性值
            main_img_src = img_tag.get_attribute("src")
            return main_img_src
        except Exception as e:
            return None
    
    def parse_score(self, grid_item):
        match = None
        score_text = self.find_element_by_classname(grid_item, "a-icon-alt")
        if score_text:
            match = re.search(r"(\d+\.\d+)", score_text)
        if match:
            score = match.group(1)
            return score
        else:
            return None

    def parse_number(self, grid_item):
        number_text = self.find_element_by_classname(grid_item, "a-size-small")
        if number_text:
            number = int(re.sub(',', '', number_text))
        else:
            number = 0
        return number

    def parse_price(self, grid_item):
        price_text = self.find_element_by_classname(grid_item, "_cDEzb_p13n-sc-price_3mJ9Z")
        if price_text:
            price = float(re.sub(r'[^\d.]', '', price_text))
        else:
            price = 0
        return price

    @staticmethod
    def find_mjjl_element(grid_item):
        # 查找卖家精灵数据
        try:
            element = grid_item.find_element(By.XPATH, ".//div[@data-v-app]")
            return element
        except Exception as e:
            return None

    def parse_gj(self, element):
        try:
            # 执行 JavaScript 脚本来获取国家信息
            country = self.driver.execute_script('''
                var flagIconUsElements = arguments[0].querySelectorAll('.flag-icon-us');
                var flagIconCnElements = arguments[0].querySelectorAll('.flag-icon-cn');

                if (flagIconUsElements.length > 0) {
                    return "美国";
                } else if (flagIconCnElements.length > 0) {
                    return "中国";
                } else {
                    return "其他";
                }
            ''', element)
            return country
        except Exception as e:
            print("An error occurred while parsing country:", e)
            return None

    def click_last_link(self):
        # 获取下一页数据
        try:
            # 使用 CSS 选择器定位具有特定类名的元素
            last_link = self.driver.find_element(By.CSS_SELECTOR, ".a-last")
            # 点击该元素
            last_link.find_element(By.TAG_NAME, 'a').click()
            print("Clicked the last link successfully.")
            time.sleep(5)
            return True
        except Exception as e:
            print("An error occurred while clicking the last link:", e)
            return False


    def get_grid_items(self):
        try:
            grid_items = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, "//div[@id='gridItemRoot']"))
            )
            return grid_items
        except TimeoutException:
            print("Timed out waiting for grid items to load.")
            return []

    def get_all_pro_info(self):
        # 定义一个字典用于存储商品信息
        goods_list = []

        # 定位所有id为"gridItemRoot"的div元素
        grid_items = self.get_grid_items()
        for grid_item in grid_items:
            goods_dict = {}
            asin = self.parse_asin(grid_item)
            bsr = self.parse_bsr(grid_item)
            title = self.parse_title(grid_item)
            main_img = self.parse_main_img(grid_item)
            score = self.parse_score(grid_item) #
            number = self.parse_number(grid_item)
            price = self.parse_price(grid_item)
            if asin:
                goods_dict['ASIN'] = asin
            if bsr:
                goods_dict['子类BSR'] = bsr
            if title:
                goods_dict['标题'] = title
            if main_img:
                goods_dict['主图'] = main_img
            if score:
                goods_dict['评分'] = score
            if number:
                goods_dict['评分数'] = number
            if price:
                goods_dict['价格'] = price
            mjjl_data = self.find_mjjl_element(grid_item)
            if mjjl_data:
                data = mjjl_data.text.replace('\n', ' ')
                gj = self.parse_gj(mjjl_data)
                if gj:
                    data += f"国家: {gj}"
                goods_dict.update(parse_string_to_dict(data))
                pass

            goods_list.append(goods_dict)
        return goods_list


def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config['Parameters']

def main():
    config = read_config('config.ini')
    ZIP = config.get('ZIP')
    HOMEPAGE = config.get('HOMEPAGE')
    BSR_URL = config.get('BSR_URL')
    current_datetime = datetime.now()
    OUTPUT_FILE = config.get('BSR') + current_datetime.strftime("_%Y%m%d%H%M") + '.xlsx'

    # ZIP = "90001"
    # HOMEPAGE = "https://www.amazon.com"
    # BSR_URL = "automotive/15707241/ref=pd_zg_hrsr_automotive"
    # output_file = "automotive_20240420.xlsx"

    amazon_browser = AmazonBrowser(HOMEPAGE)
    amazon_browser.set_zip_code(ZIP)
    goods_info = []
    keys = ["ASIN", "URL", "主图", "标题", "配送", "品牌", "卖家", "国家", "卖家数", "上架日期", "上架天数", "是否新品", "大类", "大类BSR", "子类", "子类BSR", "评分", "评分数", "评分段", "变体数", "销售数量",  "价格", "销售额",  "近30天销量(父体)", "近30天销量(子体)", "毛利率", "FBA费用", "全部流量词", "自然搜索词", "广告流量词", "搜索推荐词",  "重量", "尺寸", "Size", "Color", "Style", "Coupon", "Material Type", "Pattern Name", "Model", "Item Package Quantity", "Number of Items", "Collection time"]

    # 访问指定网址
    if amazon_browser.driver:
        url = f"{HOMEPAGE}/gp/bestsellers/{BSR_URL}"
        amazon_browser.load_page(url)
        amazon_browser.webpage_scroll_to_bottom()
        goods_info = amazon_browser.get_all_pro_info()

        while True:
            if amazon_browser.click_last_link():
                amazon_browser.webpage_scroll_to_bottom()
                next_data = amazon_browser.get_all_pro_info()
                goods_info += next_data
            else:
                break

    # 数据整理
    parsed_data = []
    for row in goods_info:
        parsed_data.append(sort_dict(row, keys))
    # 将解析结果写入Excel表格
    df = pd.DataFrame(parsed_data)
    df.to_excel(OUTPUT_FILE, index=False)

    print("解析完成，并已将结果写入到Excel表格:", OUTPUT_FILE)

    pass

    # 关闭浏览器
    amazon_browser.quit_browser()

if __name__ == "__main__":
    main()
    print("App exited.")
