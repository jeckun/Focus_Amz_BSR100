
import pandas as pd
import matplotlib.pyplot as plt
import pymysql
import os
from datetime import datetime


# 连接到MySQL数据库
conn = pymysql.connect(host='127.0.0.1', user='root', password='Xsk58&9jS', db='amazone_goods')


query = "SELECT ASIN, `collection time`, 子类BSR FROM goods ORDER BY ASIN, `collection time`"
df = pd.read_sql(query, conn)

# 找出统计时间段内子类BSR减少最多的5款产品的ASIN
top_5_asin = df.groupby('ASIN')['子类BSR'].apply(lambda x: x.iloc[-1] - x.iloc[0]).nsmallest(5).index

# 提取统计时间段内子类BSR减少最多的5款产品的子类BSR数据
top_5_data = df[df['ASIN'].isin(top_5_asin)]

# 制作折线图
plt.figure(figsize=(10, 6))
for asin in top_5_asin:
    plt.plot(top_5_data[top_5_data['ASIN'] == asin]['collection time'],
             top_5_data[top_5_data['ASIN'] == asin]['子类BSR'],
             label=asin)
plt.xlabel('Collection Time')
plt.ylabel('子类BSR')
plt.title('Top 5 Products with Largest BSR Decrease')
plt.legend(title='ASIN')

# 将Y轴坐标倒置并设置区间为1-100
plt.gca().invert_yaxis()
plt.ylim(1, 100)

# 确保文件夹存在
if not os.path.exists('img'):
    os.makedirs('img')

# 生成当前日期时间字符串，精确到小时
current_time = datetime.now().strftime("%Y-%m-%d_%H")

# 保存图像到文件夹，文件名包含当前日期时间
plt.savefig(f'img/top_5_bsr_decrease_{current_time}.png', bbox_inches='tight')

# 显示图像
plt.show()

# 关闭数据库连接
conn.close()
