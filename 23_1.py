import tushare as ts
import pandas as pd

# 获取个股以往交易历史的分笔数据明细
df_tick = ts.get_tick_data('002372', date='2020-01-23', src='tt')

# 1
df_tick.index = pd.to_datetime(df_tick.time)
df_tick.drop(axis = 1, columns = 'time', inplace = True)

# print(df_tick[2000:2010])

df_min_ohlc = df_tick.price.resample('1min', closed='left', label='left').ohlc()
# print(df_min_ohlc)
# 清除NaN数据
df_min_ohlc = df_min_ohlc.dropna(axis = 0, how = 'all')
print(df_min_ohlc)

# 2
# 当天的成交额
# print(df_tick.amount.sum())

# 3
# 计算资金流入和流出的
# print(df_tick['amount'].groupby(df_tick['type']).sum())

# 4
# 设置主力交易成交额阈值即可，当天所有大于该阈值的买盘的总成交额，即为主力资金流入，当天所有大于该阈值的卖盘的总成交额，即为主力资金流出
# threshold = 100000
# print(df_tick[df_tick["amount"]>threshold].amount.groupby(df_tick["type"]).sum())

# 5
# 获取大单交易数据,默认为大于等于400手,数据来源于新浪财经。
# data = ts.get_sina_dd('600797', date = '2020-07-08')
# print(data.head())


