#%%
import scipy.stats as stats
import numpy as np
import sys
sys.path.append("../")

from toolBox.Ashare import *
from datetime import datetime, timedelta
# 计算置信区间和置信度
def calculate_confidence_interval(data, confidence=0.99):
    n = len(data)
    mean = np.mean(data)
    std_err = stats.sem(data)
    margin_of_error = std_err * stats.t.ppf((1 + confidence) / 2, n - 1)
    return mean, mean - margin_of_error, mean + margin_of_error

df_stock=get_price('sz002739',frequency='1m',count=240)
df_stock["datetime"] = df_stock.index
df_stock['date'] = df_stock['datetime'].dt.date
df_morning = df_stock[df_stock['datetime'].dt.time.between(datetime.strptime('09:30', '%H:%M').time(), datetime.strptime('10:30', '%H:%M').time())]

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

# %%
predicted_highs

# %%
predicted_lows
# %%
# 只要搞清楚他的波动幅度是多大比如波峰波谷的1% 起步 和价格比较沾边的
# 做一个线性预测

from prophet import Prophet
import matplotlib.pyplot as plt
# 生成模拟股票数据
# 选择当天的数据进行时间序列预测
today_date = '2023-01-02'
df_today = df_stock[df_stock['datetime'].dt.time.between(datetime.strptime('09:30', '%H:%M').time(), datetime.strptime('14:00', '%H:%M').time())]

# 准备数据格式供 Prophet 使用
df_prophet = df_today[['datetime', 'close']].rename(columns={'datetime': 'ds', 'close': 'y'})

# 初始化 Prophet 模型
model = Prophet()

# 拟合数据
model.fit(df_prophet)

# 预测未来数据点（例如，预测接下来的12小时）
future = model.make_future_dataframe(periods=30, freq='1min')
forecast = model.predict(future)

# 绘制预测结果和置信区域
fig, ax = plt.subplots(figsize=(14, 7))

# 实际数据
ax.plot(df_today['datetime'], df_today['close'], label='Actual')

# 预测数据
ax.plot(forecast['ds'], forecast['yhat'], label='Predicted')

# 置信区域
ax.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], color='gray', alpha=0.2, label='Confidence Interval')

# 图表美化
ax.set_xlabel('Time')
ax.set_ylabel('Price')
ax.set_title(f'Price Prediction for {today_date} with Confidence Interval')
ax.legend()

plt.show()
# %%
