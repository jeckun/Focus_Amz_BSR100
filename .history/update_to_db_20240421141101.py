import pymysql
import pandas as pd
import numpy as np
from datetime import datetime

def connect_to_database():
    # 连接数据库
    try:
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='Xsk58&9jS',
                                     db='amazone_goods',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def generate_create_table_sql(file_path, table_name):
    try:
        df = pd.read_excel(file_path)
        columns = df.columns
        data_types = df.dtypes

        sql_columns = []
        for col, dtype in zip(columns, data_types):
            if dtype == 'object':
                sql_type = 'VARCHAR(255)'
            elif dtype == 'int64':
                sql_type = 'INT'
            elif dtype == 'float64':
                sql_type = 'FLOAT'
            elif dtype == 'datetime64':
                sql_type = 'DATETIME'
            else:
                sql_type = 'VARCHAR(255)'  # 默认使用 VARCHAR(255)

            sql_columns.append(f"`{col}` {sql_type}")

        sql_statement = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(sql_columns)}, id INT AUTO_INCREMENT PRIMARY KEY)"
        return sql_statement
    except Exception as e:
        print(f"Error generating create table SQL: {e}")
        return None

def create_goods_table(connection, sql):
    # 创建 goods 表
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
        connection.commit()
        print("Table 'goods' created successfully.")
    except Exception as e:
        print(f"Error creating 'goods' table: {e}")

def read_excel(file_path):
    # 读取 Excel 文件
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return None

def process_data(df):
    # 处理数据
    df['Collection time'] = df['Collection time'].apply(lambda x: x.strftime('%Y-%m-%d %H') if isinstance(x, datetime) else x)
    return df

def insert_or_update_data(connection, df):
    # 将 DataFrame 中的空值替换为 None
    df = df.where(pd.notnull(df), None)

    # 插入或更新数据
    try:
        with connection.cursor() as cursor:
            for index, row in df.iterrows():
                asin = row['ASIN']
                collection_time_str = row['Collection time'][:13]
                collection_time = datetime.strptime(collection_time_str, '%Y-%m-%d %H')
                sql_check = "SELECT * FROM goods WHERE ASIN = %s AND `Collection time` = %s"
                cursor.execute(sql_check, (asin, collection_time))
                result = cursor.fetchone()
                
                if result:
                    # 如果存在记录，则更新
                    sql_update = "UPDATE goods SET URL = %s, 主图 = %s, 标题 = %s, 配送 = %s, 品牌 = %s, 卖家 = %s, 国家 = %s, 卖家数 = %s, 上架日期 = %s, 上架天数 = %s, 是否新品 = %s, 大类 = %s, 大类BSR = %s, 子类 = %s, 子类BSR = %s, 评分 = %s, 评分数 = %s, 评分段 = %s, 变体数 = %s, 销售数量 = %s, 价格 = %s, 销售额 = %s, '近30天销量(父体)' = %s, '近30天销量(子体)' = %s, 毛利率 = %s, FBA费用 = %s, 全部流量词 = %s, 自然搜索词 = %s, 广告流量词 = %s, 搜索推荐词 = %s, 重量 = %s, 尺寸 = %s, Color = %s, Style = %s, Coupon = %s, Size = %s, `Pattern Name` = %s WHERE ASIN = %s AND `Collection time` = %s"
                    cursor.execute(sql_update, (row['URL'], row['主图'], row['标题'], row['配送'], row['品牌'], row['卖家'], row['国家'], row['卖家数'], row['上架日期'], row['上架天数'], row['是否新品'], row['大类'], row['大类BSR'], row['子类'], row['子类BSR'], row['评分'], row['评分数'], row['评分段'], row['变体数'], row['销售数量'], row['价格'], row['销售额'], row['近30天销量(父体)'], row['近30天销量(子体)'], row['毛利率'], row['FBA费用'], row['全部流量词'], row['自然搜索词'], row['广告流量词'], row['搜索推荐词'], row['重量'], row['尺寸'], row['Color'], row['Style'], row['Coupon'], row['Size'], row['Pattern Name'], asin, collection_time))
                else:
                    # 如果不存在记录，则插入
                    sql_insert = "INSERT INTO goods (ASIN, URL, 主图, 标题, 配送, 品牌, 卖家, 国家, 卖家数, 上架日期, 上架天数, 是否新品, 大类, 大类BSR, 子类, 子类BSR, 评分, 评分数, 评分段, 变体数, 销售数量, 价格, 销售额, '近30天销量(父体)', '近30天销量(子体)', 毛利率, FBA费用, 全部流量词, 自然搜索词, 广告流量词, 搜索推荐词, 重量, 尺寸, Color, Style, `Collection time`, Coupon, Size, `Pattern Name`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    cursor.execute(sql_insert, (asin, row['URL'], row['主图'], row['标题'], row['配送'], row['品牌'], row['卖家'], row['国家'], row['卖家数'], row['上架日期'], row['上架天数'], row['是否新品'], row['大类'], row['大类BSR'], row['子类'], row['子类BSR'], row['评分'], row['评分数'], row['评分段'], row['变体数'], row['销售数量'], row['价格'], row['销售额'], row['近30天销量(父体)'], row['近30天销量(子体)'], row['毛利率'], row['FBA费用'], row['全部流量词'], row['自然搜索词'], row['广告流量词'], row['搜索推荐词'], row['重量'], row['尺寸'], row['Color'], row['Style'], collection_time, row['Coupon'], row['Size'], row['Pattern Name']))
        connection.commit()
        print("Data inserted or updated successfully.")
    except Exception as e:
        print(f"Error inserting or updating data: {e}")
        with open('error_log.txt', 'a') as f:
            f.write(f"ASIN: {asin}, Collection time: {collection_time}, Error: {e}\n")



if __name__ == "__main__":
    # 设置参数
    input_excel = "input.xlsx"
    sheet_name = "goods"

    # 连接数据库
    connection = connect_to_database()
    if connection:
        # 创建 goods 表
        create_goods_table(connection, generate_create_table_sql(input_excel, sheet_name))

        # 读取 Excel 文件
        df = read_excel(input_excel)
        if df is not None:
            # 插入或更新数据
            insert_or_update_data(connection, df)

        # 关闭数据库连接
        connection.close()
