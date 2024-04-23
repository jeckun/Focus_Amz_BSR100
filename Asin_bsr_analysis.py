import os
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

ASIN = 'B0CYLCGL31'

# 连接到MySQL数据库
connection = pymysql.connect(host='127.0.0.1', user='root', password='Xsk58&9jS', db='amazone_goods')

try:
    # 执行查询
    query = f"SELECT ASIN, `子类BSR`, `collection time` FROM goods WHERE ASIN = '{ASIN}'"
    df = pd.read_sql(query, connection)
finally:
    connection.close()
    
# 提取`collection time`标签的月日和小时部分
df['collection time'] = df['collection time'].dt.strftime('%m-%d %H:%M')

# 设置图形大小
plt.figure(figsize=(12, 6))

# 设置X轴刻度间隔
plt.xticks(rotation=45)
plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))  # 设置X轴显示10个时间点

# 设置Y轴范围
plt.ylim(0, 100)

# 绘制折线图
plt.plot(df['collection time'], df['子类BSR'], marker='o')
plt.xlabel('Collection Time')
plt.ylabel('Subclass BSR')
plt.title('Subclass BSR Variation for ASIN B0CYLCGL31')
plt.grid(True)
plt.tight_layout()
# 保存图像到文件夹，文件名包含当前日期时间
current_time = datetime.now().strftime("%Y-%m-%d_%H")
plt.savefig(f'img/{ASIN}_bsr_{current_time}.png', bbox_inches='tight')
plt.show()