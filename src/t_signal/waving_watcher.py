import os
import sys

sys.path.append("../")

from toolBox.Ashare import *

# 分析和提示目前有1m一次似乎就够用了，能有用才会提升到3s的接口，这个就要花钱了
df_stock=get_price('sz002739',frequency='1m',count=60)
print('万达日线\n',df_stock)
df_stock["index_time"] = df_stock.index
# 深圳指数的线
# df_market=get_price('sz000001',frequency='1m',count=60)
# 文化传媒(深圳影视ETF)的线
df_concept=get_price('sz159855',frequency='1m',count=60)
print('影视ETF\n',df_concept)
df_concept["index_time"] = df_concept.index


# 合并数据
merged_df = pd.merge(df_stock, df_concept, on="index_time", suffixes=('_stock', '_market'))

print(merged_df)
# 计算偏离度
merged_df['deviation'] = (merged_df['close_stock'] - merged_df['close_market']) / merged_df['close_market']

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

# 打印结果
print(merged_df[['index_time', 'close_stock', 'close_market', 'deviation', 'signal', 'profit']])