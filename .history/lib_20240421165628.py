import re
import pandas as pd
from sqlalchemy import create_engine

from datetime import datetime
from collections import OrderedDict

# 从 Excel 文件读取数据到 DataFrame
def load_xlsx_to_db(file_name, ps, sheet_name='Sheet1'):
    print(f'Import file {file_name} to mysql db.')
    try:
        df = pd.read_excel(file_name, sheet_name='Sheet1')

        # 连接到 MySQL 数据库
        engine = create_engine(f'mysql+pymysql://root:{ps}@localhost/amazone_goods')

        # 将 DataFrame 中的数据写入到 MySQL 数据库的 goods 表中
        df.to_sql('goods', con=engine, if_exists='append', index=False)
        print("Data imported successfully.")
    except Exception as e:
        print("Data import failed.")

# 解析类目排名字符串
def parse_string(input_string):
    result = {}
    # 首先检查是否有 "#"，如果有则按 "#" 拆分字符串
    if "#" in input_string:
        parts = input_string.strip().split("#")
        # 解析每个拆分后的字符串
        for index, part in enumerate(parts[1:]):
            sub_parts = part.strip().split(" in ")
            n1 = '大类' if index == 0 else '子类'
            n2 = '大类BSR' if index == 0 else '子类BSR'
            result[n1] = sub_parts[1].strip()
            result[n2] = int(sub_parts[0].replace(",", "").replace('N/A','0'))
    return result

# 解析评分字符串
def parse_rating_string(rating_string):
    # 定义正则表达式模式
    pattern = r'(\d+\.\d+)\((\d+)\)'
    # pattern = r'评分\(评分数\):(\d+\.\d+)\((\d+)\)'

    # 使用正则表达式匹配字符串
    match = re.match(pattern, rating_string.replace(',',''))

    # 如果匹配成功，提取评分和评分数
    if match:
        rating = float(match.group(1))
        rating_count = int(match.group(2))
        rating_level = '4.5 以上' if rating >= 4.5 else '3.5 - 4.5' if rating >= 3.5 else '0 分' if rating == 0 else '3.5 以下'

        # 返回解析结果字典
        result = {"评分": rating, "评分数": rating_count, "评分段": rating_level}
        return result
    else:
        return {"评分": 0, "评分数": 0}

# 解析上架天数
def parse_shelf_string(shelf_string):
    # 定义正则表达式模式
    pattern = r'(\d{4}-\d{2}-\d{2})\((\d+)天\)'

    # 使用正则表达式匹配字符串
    match = re.match(pattern, shelf_string.replace(',', '').replace('N/A', '0'))

    # 如果匹配成功,提取上架日期和上架天数
    if match:
        shelf_date_str = match.group(1)
        shelf_days = int(match.group(2))

        # 计算上架天数
        today = datetime.now().date()
        shelf_date = datetime.strptime(shelf_date_str, '%Y-%m-%d').date()
        shelf_days = (today - shelf_date).days

        # 判断是否为新品
        is_new_product = shelf_days <= 90

        # 返回解析结果字典
        result = {
            "上架日期": shelf_date_str,
            "上架天数": shelf_days,
            "是否新品": "Yes" if is_new_product else "No"
        }
        return result
    else:
        return None

# 解析字符串内容为需要的数据
def parse_string_to_dict(data_string):
    # 初始化一个字典来存储属性和值
    data_dict = {}
    sell_num = 0
    a = data_string.find('卖家')
    if a>0:
        a = data_string.find('卖家', a+1)
        data_string = data_string[:a]+'卖家数'+data_string[a+2:]

    # 定义字符串中关键字段名
    keys = ['ASIN', '品牌', '卖家', '配送', '卖家数', '加入产品库', '近30天销量(父体)', '近30天销量(子体)', '销售额', 'FBA费用', '毛利率', '变体数', '价格', 'Coupon', '评分(评分数)', 'Color', 'Pattern Name', 'Style', 'Model', 'Number of Items', 'Size', 'Material Type', 'Item Package Quantity', '重量', '尺寸', '上架时间', '全部流量词', '自然搜索词', '广告流量词', '搜索推荐词', '关键词反查', '国家', '标题']

    # 处理关键字段出现顺序的问题
    positions = {key: data_string.find(key) for key in keys} # 找出每个数组元素在字符串中的位置
    sorted_keys = sorted(keys, key=lambda key: positions[key])  # 按位置对数组进行排序
    keys = [key for key in sorted_keys if positions[key] != -1] # 删除没有找到的数组元素
    keys.append('Collection time')

    # 循环提取关键字段的值
    for index, key in enumerate(keys):
        # 检查字符串中是否存在当前键名称
        if key in data_string:
            # 判断是否为"加入产品库"键
            if key == "加入产品库":
                data_string = data_string.replace(key + "#", "", 1).replace(key, "", 1)
            else:
                data_string = data_string.replace(key + ": ", "", 1)
            
            # 初始化下一个键的索引
            next_key_index = None

            # 寻找下一个键的名称
            for next_key in keys[index + 1:]:
                if next_key in data_string:
                    next_key_index = data_string.find(next_key)
                    break

            # 如果找到下一个键的索引，则将两个键名称之间的内容作为当前键的值
            if next_key_index is not None:
                value = data_string[:next_key_index]
                # 增加大类和子类排名
                if key == "ASIN":
                    data_dict[key] = value.strip()
                    data_dict["URL"] = "https://www.amazon.com/dp/" + value.strip()
                elif key == "加入产品库":
                    result = parse_string(value)
                    del result['子类BSR']
                    data_dict.update(result)
                elif key == "评分(评分数)": 
                    pass
                elif key == "上架时间": 
                    result = parse_shelf_string(value)
                    data_dict.update(result)
                elif key in ("卖家数", "销售额", "近30天销量(父体)", "近30天销量(子体)", "变体数", "全部流量词", "自然搜索词", "广告流量词", "搜索推荐词", "FBA费用"): 
                    data_dict[key.replace('(','').replace(')','')] = float(value.strip().replace(',','').replace('+','').replace('N/A','0').replace('<','').replace(' ','').replace('-', '0').replace('$',''))
                elif key in ("关键词反查", "价格", "ASIN"):
                    pass
                else:
                    data_dict[key] = value.strip()
                data_string = data_string[next_key_index:]
            else:
                data_dict[key] = data_string.strip()
        elif key == "Collection time":
            current_datetime = datetime.now()
            data_dict["Collection time"] = current_datetime.strftime("%Y-%m-%d %H:00:00")

    if "销售数量" in data_dict:
        data_dict["销售数量"] = data_dict["近30天销量父体"] if data_dict["近30天销量父体"] > data_dict["近30天销量子体"] else data_dict["近30天销量子体"]
    
    return data_dict

# 给字段进行排序
def sort_dict(data, keys):
    match_keys = []
    keys_name = [key for key, value in data.items()]
    for key in keys:
        if key in keys_name:
            match_keys.append(key)
    ordered_data = OrderedDict((key, data[key]) for key in match_keys)
    return ordered_data

def parse_file(input_file, output_file, keys):
    # 读取指定的文本文件并解析每一行
    parsed_data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            parsed_data.append(sort_dict(parse_string_to_dict(line.strip()), keys))

    # 将解析结果写入Excel表格
    df = pd.DataFrame(parsed_data)
    df.to_excel(output_file, index=False)

    print("解析完成，并已将结果写入到Excel表格:", output_file)

# 数据清理
def check_data(parsed_data):
    # ASIN 为空的删除
    
    pass

# 测试代码
if __name__ == "__main__":
    input_file = "input.txt"
    output_file = "output.xlsx"
    keys = ["ASIN", "标题", "品牌", "卖家", "国家", "上架日期", "上架天数", "是否新品", "大类", "大类BSR", "子类", "子类BSR", "评分", "评分数", "评分段", "近30天销量(父体)", "近30天销量(子体)", "销售数量", "变体数", "价格", "销售额", "毛利率", "FBA费用", "配送", "卖家数", "全部流量词", "自然搜索词", "广告流量词", "搜索推荐词", "URL", "重量", "尺寸", "Size", "Color", "Style", "Coupon", "Material Type", "Pattern Name", "Model", "Item Package Quantity", "Number of Items"]
    
    # 调用函数解析文件
    parse_file(input_file, output_file, keys)
