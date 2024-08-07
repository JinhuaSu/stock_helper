# 获取历史分钟数据接口
# 目前三十数据
# （可以存储下来，当日的数据）
#%%
#%%
import os
import sys
import numpy as np
from sklearn.preprocessing import StandardScaler
#%%

sys.path.append("../")

from toolBox.Ashare import *
# 约一个月的数据与波形图
df_stock=get_price('sz002739',frequency='5m',count=48 * 25)
# 仅仅有9点30-10点的数据时（5分钟一条数据，每天仅靠6条数据来推测以下内容：
# 最高点预测 与最低点预测
# 聚类图形以及预测
#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from datetime import datetime, timedelta
df_stock["datetime"] = df_stock.index
#%%
# 仅选择每天的9:30-10:00数据
df_morning = df_stock[df_stock['datetime'].dt.time.between(datetime.strptime('09:30', '%H:%M').time(), datetime.strptime('10:00', '%H:%M').time())]

# 选择特征
features = df_morning[['open', 'close', 'high', 'low', 'volume']]

# 使用 KMeans 进行聚类
kmeans = KMeans(n_clusters=3, random_state=42).fit(features)
df_morning['cluster'] = kmeans.labels_

# 可视化聚类结果
plt.figure(figsize=(14, 7))
plt.scatter(df_morning['datetime'], df_morning['close'], c=df_morning['cluster'], cmap='viridis', label='Close Price')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.title('Clustered Stock Data')
plt.legend()
plt.show()


#%%
# 根据聚类结果预测最高点和最低点
highest_cluster = df_morning.groupby('cluster')['high'].mean().idxmax()
lowest_cluster = df_morning.groupby('cluster')['low'].mean().idxmin()

# 预测最高点和最低点
predicted_high = df_morning[df_morning['cluster'] == highest_cluster]['high'].max()
predicted_low = df_morning[df_morning['cluster'] == lowest_cluster]['low'].min()

print(f"Predicted Highest Point: {predicted_high}")
print(f"Predicted Lowest Point: {predicted_low}")
#%%
# 可视化波形图
plt.figure(figsize=(14, 7))
plt.plot(df_stock['datetime'], df_stock['close'], label='Close Price')
plt.scatter(df_morning[df_morning['high'] == predicted_high]['datetime'], [predicted_high], color='red', label='Predicted High')
plt.scatter(df_morning[df_morning['low'] == predicted_low]['datetime'], [predicted_low], color='green', label='Predicted Low')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.title('Stock Price Waveform with Predicted High and Low Points')
plt.legend()
plt.show()

# %%
