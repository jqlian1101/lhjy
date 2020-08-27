# -*- coding:UTF-8 -*-

import pandas_datareader.data as web
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt


# 股票数据获取及处理接口
def GetStockDatApi(stockName=None, stockTimeS=None, stockTimeE=None, N1=15, N2=5):

    stockdata = web.DataReader(stockName, "yahoo", stockTimeS, stockTimeE)

    # 计算最近N1个交易日最高价
    stockdata['N1_High'] = stockdata.High.rolling(
        window=N1).max()
    expan_max = stockdata.Close.expanding().max()

    # 目前出现过的最大值填充前N1个nan
    stockdata['N1_High'].fillna(
        value=expan_max, inplace=True)

    # 计算最近N2个交易日最低价
    stockdata['N2_Low'] = stockdata.Low.rolling(
        window=N2).min()
    expan_min = stockdata.Close.expanding().min()

    # 目前出现过的最小值填充前N2个nan
    stockdata['N2_Low'].fillna(
        value=expan_min, inplace=True)

    # 收盘价超过N1最高价 买入股票持有
    buy_index = stockdata[stockdata.Close > stockdata.N1_High.shift(1)].index
    stockdata.loc[buy_index, 'signal'] = 1

    # 收盘价超过N2最低价 卖出股票持有
    sell_index = stockdata[stockdata.Close < stockdata.N2_Low.shift(1)].index
    stockdata.loc[sell_index, 'signal'] = 0
    stockdata['signal'].fillna(method='ffill', inplace=True)
    stockdata['signal'] = stockdata.signal.shift(1)
    stockdata['signal'].fillna(method='bfill', inplace=True)

    return stockdata


cash_hold = 100000  # 初始资金
posit_num = 0  # 持股数目
market_total = 0  # 持股市值
skip_days = 0  # 持股/持币状态


df_stockload = GetStockDatApi("600410.SS", datetime.datetime(
    2018, 10, 1), datetime.datetime(2019, 4, 1))

df_stockload.Close.plot()

for kl_index, today in df_stockload.iterrows():
    if today.signal == 1 and skip_days == 0:  # 买入
        start = df_stockload.index.get_loc(kl_index)
        skip_days = -1
        posit_num = int(cash_hold / today.Close)  # 资金转化为股票
        cash_hold = 0

    elif today.signal == 0 and skip_days == -1:  # 卖出 避免未买先卖
        end = df_stockload.index.get_loc(kl_index)
        skip_days = 0
        cash_hold = int(posit_num * today.Close)  # 股票转化为资金
        market_total = 0

    if skip_days == -1:  # 持股
        market_total = int(posit_num * today.Close)
        df_stockload.loc[kl_index, 'total'] = market_total
    else:  # 空仓
        df_stockload.loc[kl_index, 'total'] = cash_hold

    print(df_stockload.total)

# df_stockload.total.plot(grid=True)
# plt.show()

# 计算基准收益
df_stockload['benchmark_profit'] = np.log(
    df_stockload.Close/df_stockload.Close.shift(1))

# 计算趋势突破策略收益
df_stockload['trend_profit'] = df_stockload.signal * \
    df_stockload.benchmark_profit
# print(df_stockload['trend_profit'])

# 使用cumsum()方法将序列值累加形成基准收益曲线和策略收益曲线，然后使用DataFrame格式数据自带的plot()方法绘制这两条曲线
# df_stockload[['benchmark_profit', 'trend_profit']].cumsum().plot(grid=True)
# plt.show()

# 股票收盘价最大回撤率
# expanding()计算收盘价曲线当前的滚动最高值
df_stockload['max_close'] = df_stockload['Close'].expanding().max()
# df_stockload['max_close'].plot(grid=True)


# 计算收盘价曲线对于滚动最高值后所占的百分比
df_stockload['per_close'] = df_stockload['Close'] / df_stockload['max_close']

min_point_close = df_stockload.sort_values(
    by=['per_close']).iloc[[0], df_stockload.columns.get_loc('per_close')]

print("最大股价回撤%5.2f%%" % (1 - min_point_close.values))

# 寻找出最大回撤率所对应的最高价交易日和最大回撤交易日
max_point_close = df_stockload[df_stockload.index <= min_point_close.index[0]].sort_values(
    by=['Close'], ascending=False).iloc[[0], df_stockload.columns.get_loc('Close')]

print("从%s开始至%s结束" % (max_point_close.index[0], min_point_close.index[0]))


# expanding()计算资金曲线当前的滚动最高值
df_stockload['max_total'] = df_stockload['total'].expanding().max()

plt.show()
