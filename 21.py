import tushare as ts
import pandas as pd



# 获取个股以往交易历史的分笔数据明细
# df_tick = ts.get_tick_data('002372', date='2020-01-23', src='tt')

# df_tick.index = pd.to_datetime(df_tick.time)
# df_tick.drop(axis = 1, columns = 'time', inplace = True)

# # print(df_tick[2000:2010])

# df_min_ohlc = df_tick.price.resample('1min', closed='left', label='left').ohlc()
# df_min_ohlc = df_min_ohlc.dropna(axis = 0, how = 'all')

# # print(df_tick.amount.sum())
# # print(df_tick['amount'].groupby(df_tick['type']).sum())

# # threshold = 100000
# # print(df_tick[df_tick["amount"]>threshold].amount.groupby(df_tick["type"]).sum())


# 获取大单交易数据,默认为大于等于400手,数据来源于新浪财经。
data = ts.get_sina_dd('600797', date = '2020-07-08')
print(data.head())



