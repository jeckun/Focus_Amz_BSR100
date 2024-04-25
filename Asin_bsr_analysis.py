import os
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# 连接到MySQL数据库
connection = pymysql.connect(host='127.0.0.1', user='root', password='Xsk58&9jS', db='amazone_goods')

# 定义要绘制的ASIN列表
asins = ['B0CN95MSRN', 'B0CX52R2T6', 'B0BZYC7VCM', 'B0CYLCGL31', 'B0CW59TK11', 'B0CYSJPNZB', 'B0D25F8PVG','B0C68Q85D2']

try:
    plt.figure(figsize=(12, 6))

    for asin in asins:
        # 执行查询
        query = "SELECT `子类BSR`, `collection time` FROM goods WHERE ASIN = %s"
        df = pd.read_sql(query, connection, params=(asin,))

        # 提取`collection time`标签的月日和小时部分
        df['collection time'] = df['collection time'].dt.strftime('%m-%d %H:%M')

        # 设置X轴刻度间隔
        plt.xticks(rotation=45)
        plt.gca().xaxis.set_major_locator(plt.MaxNLocator(18))  # 设置X轴显示10个时间点

        # 设置Y轴范围
        plt.ylim(0, 100)

        # 绘制折线图，并为每个折线图添加标签
        plt.plot(df['collection time'], df['子类BSR'], marker='.', label=asin)

    plt.xlabel('Collection Time')
    plt.ylabel('Subclass BSR')
    plt.title('Subclass BSR Variation for ASINs')
    plt.grid(True)
    plt.tight_layout()

    # 添加图例
    plt.legend()

    # 保存图像到文件夹，文件名包含当前日期时间
    current_time = datetime.now().strftime("%Y-%m-%d_%H")
    plt.savefig(f'img/bsr_{current_time}.png', bbox_inches='tight')
    plt.show()
finally:
    connection.close()
