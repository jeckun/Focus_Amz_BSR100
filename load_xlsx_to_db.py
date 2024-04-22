import os
import shutil
import pandas as pd
from sqlalchemy import create_engine

# 指定要搜索的目录和存档目录
directory = 'data/'
archived_directory = 'Archived/'

# 连接到 MySQL 数据库
engine = create_engine('mysql+pymysql://root:Xsk58&9jS@localhost/amazone_goods')

# 遍历目录中所有文件
for file_name in os.listdir(directory):
    # 检查文件是否是 Excel 文件
    if file_name.endswith('.xlsx'):
        file_path = os.path.join(directory, file_name)
        print(f'Load {file_name} to mysql db.')

        try:
            # 从 Excel 文件读取数据到 DataFrame
            df = pd.read_excel(file_path, sheet_name='Sheet1')
            
            # 删除 DataFrame 中数据库中不存在的列
            existing_columns = pd.read_sql_query('SHOW COLUMNS FROM goods', con=engine)['Field']
            df = df[[col for col in df.columns if col in existing_columns.values]]
            
            # 将 ASIN 列转换为字符串类型，并限制长度为 10 位，去除前后空格
            df['ASIN'] = df['ASIN'].astype(str).str[:10].str.strip()
            
            # 将 Collection time 列从文本类型转换为日期时间类型
            df['Collection time'] = pd.to_datetime(df['Collection time'])
            
            # 查询数据库中已有的数据
            existing_data = pd.read_sql_query('SELECT ASIN, `Collection time` FROM goods', con=engine)
            
            # 将新导入的数据与已有数据进行合并，并保留新数据中独有的部分
            new_data = df.merge(existing_data, on=['ASIN', 'Collection time'], how='left', indicator=True)
            new_data = new_data[new_data['_merge'] == 'left_only']
            del new_data['_merge']
            
            # 将新数据写入到数据库
            new_data.to_sql('goods', con=engine, if_exists='append', index=False)
            
            # 移动文件到 'Archived' 目录
            archived_file_path = os.path.join(archived_directory, file_name)
            shutil.move(file_path, archived_file_path)
            
            print("Data imported successfully.")
        except Exception as e:
            print(f"Error importing data from {file_name}: {e}")
            with open('error_log.txt', 'a') as f:
                f.write(f"Error importing data from {file_name}: {e}\n")
