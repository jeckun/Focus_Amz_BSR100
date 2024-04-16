from selenium import webdriver

# 设置代理
proxy_address = "http://127.0.0.1:8080"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--proxy-server=%s' % proxy_address)

# 设置请求头
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36'
chrome_options.add_argument(f'user-agent={user_agent}')

# 启动 Chrome 浏览器，并配置代理和请求头
driver = webdriver.Chrome(options=chrome_options)

# 访问指定网址
url = "https://www.amazon.com/gp/bestsellers/climate-pledge/21377129011/ref=pd_zg_hrsr_climate-pledge"
driver.get(url)

# 这里继续执行后续的操作，比如模拟点击按钮、输入内容等

# 关闭浏览器
driver.quit()
