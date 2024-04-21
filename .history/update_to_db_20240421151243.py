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
    
import pandas as pd
from sqlalchemy import create_engine

# 从 Excel 文件读取数据到 DataFrame
df = pd.read_excel('input.xlsx', sheet_name='Sheet1')

# 连接到 MySQL 数据库
engine = create_engine('mysql+pymysql://root:Xsk58&9jS@localhost/amazone_goods')

# 将 DataFrame 中的数据写入到 MySQL 数据库的 goods 表中
df.to_sql('goods', con=engine, if_exists='append', index=False)

print("Data imported successfully.")
