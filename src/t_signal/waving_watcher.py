#%%
import os
import sys
import numpy as np
from sklearn.preprocessing import StandardScaler
#%%

sys.path.append("../")

from toolBox.Ashare import *
#%%
scaler = StandardScaler()
# 需要设置开始时间，比如自动在10点开始，过去半小时，基本上进入股市日内波动的周期中
# 分析和提示目前有1m一次似乎就够用了，能有用才会提升到3s的接口，这个就要花钱了
df_stock=get_price('sz002739',frequency='1m',count=240)
# print('万达日线\n',df_stock)
df_stock["index_time"] = df_stock.index
df_stock['close_std'] = scaler.fit_transform(df_stock[['close']])

# 计算前后两分钟的价格变化百分比
df_stock['pct_change'] = df_stock['close'].pct_change()

# 设定涨跌区间阈值(有些许问题，涨0.01其实已经算长了，但是除以一个过小的基数会导致要求涨两个点)
threshold = 0.01 / 10  # 1%

# 标记涨跌区间
conditions = [
    (df_stock['pct_change'] > threshold),
    (df_stock['pct_change'] < -threshold)
]
choices = [1, -1]
df_stock['trend'] = np.select(conditions, choices, default=0)
# 通过10min时间窗口里 up down stable的比例 来识别信号
# 士气系统： 连续出现3个up为顶峰信号 down比例出现40%以上时为底部（stable比例占30%以上为特殊信号）
# 通过数学特性的一些来简化二阶导数的性质，比如一阶导数为正，即比例下降的瞬间
# print(df_stock)
# 深圳指数的线
# df_market=get_price('sz000001',frequency='1m',count=60)
# 文化传媒(深圳影视ETF)的线
df_concept=get_price('sz159855',frequency='1m',count=240)
# print('影视ETF\n',df_concept)
df_concept["index_time"] = df_concept.index
df_concept['close_std'] = scaler.fit_transform(df_concept[['close']])

# 使用滚动窗口计算信号比例
window_size = 10  # 10分钟时间窗口
#%%
# 定义函数来计算滚动窗口内的信号数量
def count_trend(trend_series, trend_value):
    return (trend_series == trend_value).sum()

def calculate_signal(trend_series):
    # trend_series.index = range(len(trend_series))
    # print(trend_series[-3:])
    # 这个方案可能导致一两分钟内信号反复出现，即信号出现的前三分钟不能有信号出现才发邮箱
    if trend_series[-3:].sum() == 3:
        return 1
    elif(trend_series[-1] == -1 and (trend_series[-7:] == -1).sum() == 4) :
        return -1
    else:
        return 0

# 计算滚动窗口内的信号数量
df_stock['up_count'] = df_stock['trend'].rolling(window_size).apply(lambda x: count_trend(x, 1), raw=False)
df_stock['down_count'] = df_stock['trend'].rolling(window_size).apply(lambda x: count_trend(x, -1), raw=False)
df_stock['stable_count'] = df_stock['trend'].rolling(window_size).apply(lambda x: count_trend(x, 0), raw=False)
df_stock["temp_signal"]= df_stock['trend'].rolling(window_size).apply(lambda x: calculate_signal(x), raw=False)
# 计算比例
df_stock['up_ratio'] = df_stock['up_count'] / window_size
df_stock['down_ratio'] = df_stock['down_count'] / window_size
df_stock['stable_ratio'] = df_stock['stable_count'] / window_size

# 识别顶峰和底部信号
df_stock['turn_signal'] = 'none'
df_stock.loc[df_stock['up_count'] >= 3, 'turn_signal'] = 'peak'
df_stock.loc[df_stock['down_count'] >= 4, 'turn_signal'] = 'bottom'
# df_stock.loc[df_stock['stable_ratio'] >= 0.3, 'turn_signal'] = 'special'
df_stock
#%%
# 合并数据
merged_df = pd.merge(df_stock, df_concept, on="index_time", suffixes=('_stock', '_market'))

# print(merged_df)
#%%
# 计算偏离度
merged_df['deviation'] = (merged_df['close_std_stock'] - merged_df['close_std_market']) / merged_df['close_market']

# 计算拐点，发现拐点

# 标识合适的高位和低位
# 这里假设一个简单的策略，即当偏离度大于某个阈值时认为是高位，低于某个阈值时认为是低位
high_threshold = 0.025  # 2.5%
low_threshold = -0.025  # -2.5%

merged_df['signal'] = 'hold'
merged_df.loc[merged_df['deviation'] > high_threshold, 'signal'] = 'sell'
merged_df.loc[merged_df['deviation'] < low_threshold, 'signal'] = 'buy'

# 计算信号与收益
# 这里只是一个简单的示例，实际策略需要根据您的需求进行调整
capital_per_trade = 10000  # 每次交易的资本
commission = 30  # 手续费

merged_df['profit'] = 0
for i in range(1, len(merged_df)):
    if merged_df.at[i-1, 'signal'] == 'buy' and merged_df.at[i, 'signal'] == 'sell':
        price_diff = merged_df.at[i, 'close_stock'] - merged_df.at[i-1, 'close_stock']
        profit = (price_diff * capital_per_trade / merged_df.at[i-1, 'close_stock']) - commission
        merged_df.at[i, 'profit'] = profit
# print(merged_df.columns)
# 打印结果
# print(merged_df[['index_time', 'close_stock', 'close_market', 'deviation', 'signal','trend',"turn_signal", 'profit']])
# %%
merged_df.to_csv("../../data/merge.csv")
# if merged_df.loc[merged_df.index[-1], "trend"]
# %%
# 信号出现的前三分钟不能有信号出现才发邮箱
if merged_df.loc[merged_df.index[-1], "temp_signal"] != 0 and merged_df.loc[merged_df.index[-2], "temp_signal"] == 0 and merged_df.loc[merged_df.index[-3], "temp_signal"] == 0:
    from toolBox import EmailBot
    content_str = "即将达到顶峰，建议卖出" if merged_df.loc[merged_df.index[-1], "temp_signal"] > 0  else "即将达到谷底，建议买入" + " 当前价位"+ str(merged_df.loc[merged_df.index[-1], "close_stock"])
    emailbot = EmailBot('../../data/settings.json')
    emailbot.sendOne({"content": content_str})
    emailbot2 = EmailBot('../../data/settings2.json')
    emailbot2.sendOne({"content": content_str})
