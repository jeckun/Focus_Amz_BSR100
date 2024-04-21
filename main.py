import os
import configparser
import pandas as pd
from datetime import datetime
from scr.brower import AmazonBrowser
from scr.lib import sort_dict, load_xlsx_to_db

def read_config(filename):
    config = configparser.ConfigParser()
    config.read(filename)
    return config['Parameters']

def main():
    config = read_config('config.ini')
    ZIP = config.get('ZIP')
    HOMEPAGE = config.get('HOMEPAGE')
    BSR_URL = config.get('BSR_URL')
    RPS = config.get('RPS')
    current_datetime = datetime.now()
    OUTPUT_FILE = config.get('BSR') + current_datetime.strftime("_%Y%m%d%H%M") + '.xlsx'
    OUTPUT_FILE = os.path.join('data', OUTPUT_FILE)

    amazon_browser = AmazonBrowser(HOMEPAGE)
    amazon_browser.set_zip_code(ZIP)
    goods_info = []
    
    # 访问指定类目网址
    if amazon_browser.driver:
        url = f"{HOMEPAGE}/gp/bestsellers/{BSR_URL}"
        amazon_browser.load_page(url)
        amazon_browser.webpage_scroll_to_bottom()
        # 获取前50名商品信息
        goods_info = amazon_browser.get_all_pro_info()

        while True:
            if amazon_browser.click_last_link():
                amazon_browser.webpage_scroll_to_bottom()
                next_data = amazon_browser.get_all_pro_info()
                goods_info += next_data
            else:
                break

    # 对输出字段进行排序
    # keys = ["ASIN", "URL", "主图", "标题", "配送", "品牌", "卖家", "国家", "卖家数", "上架日期", "上架天数", "是否新品", "大类", "大类BSR", "子类", "子类BSR", "评分", "评分数", "评分段", "变体数", "销售数量",  "价格", "销售额",  "近30天销量父体", "近30天销量子体", "毛利率", "FBA费用", "全部流量词", "自然搜索词", "广告流量词", "搜索推荐词",  "重量", "尺寸", "Size", "Color", "Style", "Coupon", "Material Type", "Pattern Name", "Model", "Item Package Quantity", "Number of Items", "Collection time"]
    keys = ["ASIN", "URL", "主图", "标题", "配送", "品牌", "卖家", "国家", "卖家数", "上架日期", "上架天数", "是否新品", "大类", "大类BSR", "子类", "子类BSR", "评分", "评分数", "评分段", "变体数", "销售数量",  "价格", "销售额",  "近30天销量父体", "近30天销量子体", "毛利率", "FBA费用", "全部流量词", "自然搜索词", "广告流量词", "搜索推荐词",  "重量", "尺寸", "Size", "Color", "Style", "Coupon", "Material Type", "Pattern Name", "Model", "Item Package Quantity", "Collection time"]
    # 数据整理
    parsed_data = []
    for row in goods_info:
        parsed_data.append(sort_dict(row, keys))
    # 将解析结果写入Excel表格
    df = pd.DataFrame(parsed_data)
    df.to_excel(OUTPUT_FILE, index=False)

    print("Save data to Excel: ", OUTPUT_FILE)

    # load_xlsx_to_db(OUTPUT_FILE, RPS)

    # 关闭浏览器
    amazon_browser.quit_browser()

if __name__ == "__main__":
    main()
    print("App exited.")
