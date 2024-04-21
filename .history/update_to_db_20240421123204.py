import pymysql
import pandas as pd
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
        # 修改表结构，在表格创建成功后增加自增长的 id 字段
        alter_sql = "ALTER TABLE goods ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY"
        with connection.cursor() as cursor:
            cursor.execute(alter_sql)
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
    # 插入或更新数据
    try:
        with connection.cursor() as cursor:
            for index, row in df.iterrows():
                asin = row['ASIN']
                collection_time = row['Collection time'].strftime('%Y-%m-%d %H')
                sql_check = f"SELECT * FROM goods WHERE ASIN = '{asin}' AND `Collection time` = '{collection_time}'"
                cursor.execute(sql_check)
                result = cursor.fetchone()
                
                if result:
                    # 如果存在记录，则更新
                    sql_update = f"UPDATE goods SET URL = '{row['URL']}', \
                                                    主图 = '{row['主图']}', \
                                                    标题 = '{row['标题']}', \
                                                    配送 = '{row['配送']}', \
                                                    品牌 = '{row['品牌']}', \
                                                    卖家 = '{row['卖家']}', \
                                                    国家 = '{row['国家']}', \
                                                    卖家数 = '{row['卖家数']}', \
                                                    上架日期 = '{row['上架日期']}', \
                                                    上架天数 = '{row['上架天数']}', \
                                                    是否新品 = '{row['是否新品']}', \
                                                    大类 = '{row['大类']}', \
                                                    大类BSR = '{row['大类BSR']}', \
                                                    子类 = '{row['子类']}', \
                                                    子类BSR = '{row['子类BSR']}', \
                                                    评分 = '{row['评分']}', \
                                                    评分数 = '{row['评分数']}', \
                                                    评分段 = '{row['评分段']}', \
                                                    变体数 = '{row['变体数']}', \
                                                    销售数量 = '{row['销售数量']}', \
                                                    价格 = '{row['价格']}', \
                                                    销售额 = '{row['销售额']}', \
                                                    近30天销量_父体 = '{row['近30天销量(父体)']}', \
                                                    近30天销量_子体 = '{row['近30天销量(子体)']}', \
                                                    毛利率 = '{row['毛利率']}', \
                                                    FBA费用 = '{row['FBA费用']}', \
                                                    全部流量词 = '{row['全部流量词']}', \
                                                    自然搜索词 = '{row['自然搜索词']}', \
                                                    广告流量词 = '{row['广告流量词']}', \
                                                    搜索推荐词 = '{row['搜索推荐词']}', \
                                                    重量 = '{row['重量']}', \
                                                    尺寸 = '{row['尺寸']}', \
                                                    Color = '{row['Color']}', \
                                                    Style = '{row['Style']}', \
                                                    Coupon = '{row['Coupon']}', \
                                                    Size = '{row['Size']}', \
                                                    Pattern_Name = '{row['Pattern Name']}' \
                                  WHERE ASIN = '{asin}' AND `Collection time` = '{collection_time}'"
                    cursor.execute(sql_update)
                else:
                    # 如果不存在记录，则插入
                    sql_insert = f"INSERT INTO goods (ASIN, URL, 主图, 标题, 配送, 品牌, 卖家, 国家, 卖家数, 上架日期, 上架天数, 是否新品, \
                                                       大类, 大类BSR, 子类, 子类BSR, 评分, 评分数, 评分段, 变体数, 销售数量, 价格, 销售额, \
                                                       近30天销量_父体, 近30天销量_子体, 毛利率, FBA费用, 全部流量词, 自然搜索词, \
                                                       广告流量词, 搜索推荐词, 重量, 尺寸, Color, Style, `Collection time`, Coupon, Size, \
                                                       `Pattern Name`) \
                                  VALUES ('{asin}', '{row['URL']}', '{row['主图']}', '{row['标题']}', '{row['配送']}', \
                                          '{row['品牌']}', '{row['卖家']}', '{row['国家']}', '{row['卖家数']}', \
                                          '{row['上架日期']}', '{row['上架天数']}', '{row['是否新品']}', '{row['大类']}', \
                                          '{row['大类BSR']}', '{row['子类']}', '{row['子类BSR']}', '{row['评分']}', \
                                          '{row['评分数']}', '{row['评分段']}', '{row['变体数']}', '{row['销售数量']}', \
                                          '{row['价格']}', '{row['销售额']}', '{row['近30天销量(父体)']}', \
                                          '{row['近30天销量(子体)']}', '{row['毛利率']}', '{row['FBA费用']}', \
                                          '{row['全部流量词']}', '{row['自然搜索词']}', '{row['广告流量词']}', \
                                          '{row['搜索推荐词']}', '{row['重量']}', '{row['尺寸']}', '{row['Color']}', \
                                          '{row['Style']}', '{collection_time}', '{row['Coupon']}', '{row['Size']}', \
                                          '{row['Pattern Name']}')"
                    cursor.execute(sql_insert)
        connection.commit()
        print("Data inserted or updated successfully.")
    except Exception as e:
        print(f"Error inserting or updating data: {e}")
        with open('error_log.txt', 'a') as f:
            f.write(f"ASIN: {asin}, Collection time: {collection_time}, Error: {e}\n")


if __name__ == "__main__":
    # 设置参数
    input_excel = "input.xlsx"
    sheet_name = ""

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
