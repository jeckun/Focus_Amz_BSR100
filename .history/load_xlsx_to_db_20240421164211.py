import pandas as pd
from sqlalchemy import create_engine

file_name = 'input.xlsx'

print(f'Load {file_name} to mysql db.')

# 从 Excel 文件读取数据到 DataFrame
df = pd.read_excel(file_name, sheet_name='Sheet1')

# 连接到 MySQL 数据库
engine = create_engine('mysql+pymysql://root:Xsk58&9jS@localhost/amazone_goods')

# 将 DataFrame 中的数据写入到 MySQL 数据库的 goods 表中
df.to_sql('goods', con=engine, if_exists='append', index=False)

print("Data imported successfully.")
