# -*- coding:UTF-8 -*-

import pandas_datareader.data as web
import pandas as pd
import numpy as np
import datetime
import statsmodels.api as sm
from statsmodels import regression
import matplotlib.pyplot as plt

df_stockload = web.DataReader("600410.SS", "yahoo", datetime.datetime(2018,10,1), datetime.datetime(2019,4,1))
# print(df_stockload.describe())

N1 = 15
df_stockload['N1_High'] = df_stockload.High.rolling(window=N1).max() # 计算最近N1个交易日最高价
# print(df_stockload.info())

# 由于从第N1天开始滚动计算该周期内最大值，因此前N1个数值都为NaN，此处从收盘价序列第一个数据开始依次寻找当前为止的最大值来填充前N1个NaN，
expan_max = df_stockload.Close.expanding().max()
df_stockload['N1_High'].fillna(value=expan_max,inplace=True)  # 目前出现过的最大值填充前N1个nan
# print(df_stockload.head())


N2 = 5
df_stockload['N2_Low'] = df_stockload.Low.rolling(window=N2).min()#计算最近N2个交易日最低价
expan_min = df_stockload.Close.expanding().min()
df_stockload['N2_Low'].fillna(value=expan_min,inplace=True)#目前出现过的最小值填充前N2个nan
# print(df_stockload.head())


"""收盘价超过N1最高价 买入股票持有"""
buy_index = df_stockload[df_stockload.Close > df_stockload.N1_High.shift(1)].index
# print(buy_index)


""" 收盘价超过N2最低价 卖出股票持有"""
sell_index = df_stockload[df_stockload.Close < df_stockload.N2_Low.shift(1)].index
# print(sell_index)

# 寻找到符合买入/卖出条件的时间序列后，以该时间序列构建signal序列，将买入当天的signal值设置为1，代表买入，同理将signal设置为0，代表卖出。
df_stockload.loc[buy_index,'signal'] = 1 
df_stockload.loc[sell_index,'signal'] = 0
# print(df_stockload.signal)

# 使用fillna()方法将所有NaN值与前面元素值保持一致，这样符合一旦状态被设置为1（买入持有），只有遇到0（卖出空仓）时signal状态才会改变，
df_stockload['signal'].fillna(method = 'ffill',inplace = True)
# print(df_stockload.signal)

# 由于收盘价格是在收盘后才确定，那么第二天才能执行给出的买卖操作，此处将signal序列使用shift(1)方法右移更接近真实情况，
df_stockload['signal'] = df_stockload.signal.shift(1)
# print(df_stockload.signal)

# 使用fillna()方法，选择用0值填充序列最前面几个NaN值
df_stockload['signal'].fillna(value=0, inplace=True)
print(df_stockload.signal)