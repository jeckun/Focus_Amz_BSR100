from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 设置代理

proxy = webdriver.Proxy()
proxy.proxy_type = 'HTTP'
proxy.http_proxy = '127.0.0.1:8080'
capabilities = webdriver.DesiredCapabilities.CHROME

proxy.add_to_capabilities(capabilities)
browser = webdriver.Chrome(desired_capabilities=capabilities)
browser.get('http://www.baidu.com')

# 启动 Chrome 浏览器
driver = webdriver.Chrome()

# 访问指定网址
url = "https://www.amazon.com/gp/bestsellers/climate-pledge/21377129011/ref=pd_zg_hrsr_climate-pledge"
driver.get(url)

# 等待 a 标签加载并点击
try:
    location_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "nav-global-location-popover-link"))
    )
    location_link.click()
except Exception as e:
    print("无法找到指定的 a 标签:", e)

# 输入指定的 zip code
try:
    zip_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "GLUXZipUpdateInput"))
    )
    zip_input.clear()
    zip_input.send_keys("90001")
except Exception as e:
    print("无法找到指定的 input 标签:", e)

# 模拟点击按钮
try:
    submit_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "a-button-input"))
    )
    submit_button.click()
except Exception as e:
    print("无法找到指定的按钮:", e)

# 等待一段时间，然后关闭浏览器
driver.quit()
