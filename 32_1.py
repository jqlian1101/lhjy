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


# N日突破买卖信号区间显示
skip_days = 0

df_stockload = GetStockDatApi("600410.SS", datetime.datetime(
    2018, 10, 1), datetime.datetime(2019, 4, 1))

df_stockload.Close.plot()

for kl_index, today in df_stockload.iterrows():
    if today.signal == 1 and skip_days == 0:  # 买入
        skip_days = -1
        start = df_stockload.index.get_loc(kl_index)
        plt.annotate('买入', xy=(kl_index, df_stockload.Close.asof(kl_index)), xytext=(kl_index, df_stockload.Close.asof(
            kl_index)+2), arrowprops=dict(facecolor='r', shrink=0.1), horizontalalignment='left', verticalalignment='top')
        print("buy:", kl_index)

    elif today.signal == 0 and skip_days == -1:  # 卖出
        skip_days = 0
        end = df_stockload.index.get_loc(kl_index)

        if df_stockload.Close[end] < df_stockload.Close[start]:  # 赔钱显示绿色
            plt.fill_between(
                df_stockload.index[start:end], 0, df_stockload.Close[start:end], color='green', alpha=0.38)

        else:  # 赚钱显示红色
            plt.fill_between(
                df_stockload.index[start:end], 0, df_stockload.Close[start:end], color='red', alpha=0.38)

        plt.annotate('卖出', xy=(kl_index, df_stockload.Close.asof(kl_index)), xytext=(kl_index+datetime.timedelta(days=5),
                                                                                     df_stockload.Close.asof(kl_index)+2), arrowprops=dict(facecolor='g', shrink=0.1), horizontalalignment='left', verticalalignment='top')
        print("sell:", kl_index)

plt.legend(loc='best')
plt.title(u"华胜天成 N日突破择时")
plt.show()
