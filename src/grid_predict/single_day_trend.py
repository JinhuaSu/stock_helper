# 获取历史分钟数据接口
# 目前三十数据
# （可以存储下来，当日的数据）
# 不需要全天的预测，即预测10点之后的大致区间 可以直接数学平移
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
# 整体高的
# 用df_morning 去预测整体的df_stock每天的最高值和最低值（要有区间和置信度）
# 根据聚类结果预测最高点和最低点
# 两步走，先预测是什么聚类形态，再基于这个聚类的flag作为一个输入变量去预测最高点和最低点
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
plot_high_series = df_morning[df_morning['high'] == predicted_high]['datetime']
plot_low_series = df_morning[df_morning['low'] == predicted_low]['datetime']
plt.scatter(plot_high_series, [predicted_high] * len(plot_high_series), color='red', label='Predicted High')
plt.scatter(plot_low_series, [predicted_low] * len(plot_low_series), color='green', label='Predicted Low')
plt.xlabel('Date')
plt.ylabel('Close Price')
plt.title('Stock Price Waveform with Predicted High and Low Points')
plt.legend()
plt.show()

# %%
import scipy.stats as stats
# 根据聚类结果预测整体的df_stock每天的最高值和最低值
df_stock['date'] = df_stock['datetime'].dt.date
daily_highs = df_stock.groupby('date')['high'].max()
daily_lows = df_stock.groupby('date')['low'].min()

# 计算置信区间和置信度
def calculate_confidence_interval(data, confidence=0.95):
    n = len(data)
    mean = np.mean(data)
    std_err = stats.sem(data)
    margin_of_error = std_err * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean, mean - margin_of_error, mean + margin_of_error

# 预测每天的最高值和最低值及置信区间
predicted_highs = []
predicted_lows = []

for date, group in df_stock.groupby('date'):
    morning_data = df_morning[df_morning['datetime'].dt.date == date]
    if not morning_data.empty:
        high_mean, high_ci_low, high_ci_high = calculate_confidence_interval(morning_data['high'])
        low_mean, low_ci_low, low_ci_high = calculate_confidence_interval(morning_data['low'])
        predicted_highs.append((date, high_mean, high_ci_low, high_ci_high))
        predicted_lows.append((date, low_mean, low_ci_low, low_ci_high))

# 转换为DataFrame以便可视化
df_predicted_highs = pd.DataFrame(predicted_highs, columns=['date', 'predicted_high', 'ci_low', 'ci_high'])
df_predicted_lows = pd.DataFrame(predicted_lows, columns=['date', 'predicted_low', 'ci_low', 'ci_high'])

# 可视化预测的最高值和最低值及置信区间
plt.figure(figsize=(14, 7))

# 预测的最高值
plt.plot(df_stock['datetime'], df_stock['high'], label='Actual High', alpha=0.5)
plt.errorbar(df_predicted_highs['date'], df_predicted_highs['predicted_high'], 
             yerr=[df_predicted_highs['predicted_high'] - df_predicted_highs['ci_low'], 
                   df_predicted_highs['ci_high'] - df_predicted_highs['predicted_high']], 
             fmt='o', label='Predicted High with CI', capsize=5)

# 预测的最低值
plt.plot(df_stock['datetime'], df_stock['low'], label='Actual Low', alpha=0.5)
plt.errorbar(df_predicted_lows['date'], df_predicted_lows['predicted_low'], 
             yerr=[df_predicted_lows['predicted_low'] - df_predicted_lows['ci_low'], 
                   df_predicted_lows['ci_high'] - df_predicted_lows['predicted_low']], 
             fmt='o', label='Predicted Low with CI', capsize=5)

plt.xlabel('Date')
plt.ylabel('Price')
plt.title('Predicted Highs and Lows with Confidence Intervals')
plt.legend()
plt.show()
# %%
