import pymysql
import pandas as pd
from datetime import datetime

def connect_to_database():
    # 连接数据库
    try:
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='233224',
                                     db='amazone_goods',
                                     charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def create_goods_table(connection, columns):
    # 创建 goods 表
    try:
        with connection.cursor() as cursor:
            sql = f"CREATE TABLE IF NOT EXISTS goods ({', '.join(columns)}, \
                                                      id INT AUTO_INCREMENT PRIMARY KEY)"
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
    # 插入或更新数据
    try:
        with connection.cursor() as cursor:
            for index, row in df.iterrows():
                asin = row['ASIN']
                collection_time = row['Collection time']
                sql_check = f"SELECT * FROM goods WHERE ASIN = '{asin}' AND `Collection time` = '{collection_time}'"
                cursor.execute(sql_check)
                result = cursor.fetchone()
                
                if result:
                    # 如果存在记录，则更新
                    sql_update = f"UPDATE goods SET `Title` = '{row['Title']}', \
                                                    `Price` = '{row['Price']}', \
                                                    `Rating` = '{row['Rating']}', \
                                                    `Reviews` = '{row['Reviews']}' \
                                  WHERE ASIN = '{asin}' AND `Collection time` = '{collection_time}'"
                    cursor.execute(sql_update)
                else:
                    # 如果不存在记录，则插入
                    sql_insert = f"INSERT INTO goods (ASIN, `Collection time`, `Title`, `Price`, `Rating`, `Reviews`) \
                                  VALUES ('{asin}', '{collection_time}', '{row['Title']}', '{row['Price']}', '{row['Rating']}', '{row['Reviews']}')"
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

    # 连接数据库
    connection = connect_to_database()
    if connection:
        # 读取 Excel 文件
        df = read_excel(input_excel)
        if df is not None:
            # 处理数据
            df = process_data(df)

            # 获取列名和数据类型
            columns = [f"`{col}` VARCHAR(255)" for col in df.columns]

            # 创建 goods 表
            create_goods_table(connection, columns)

            # 插入或更新数据
            insert_or_update_data(connection, df)

        # 关闭数据库连接
        connection.close()
