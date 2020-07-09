# -*- coding:UTF-8 -*-

import pandas_datareader.data as web
import datetime

# 获取上证指数交易数据 pandas-datareade模块data.DataReader()方法
df_stockload = web.DataReader("000001.SS", "yahoo", datetime.datetime(2020, 6, 1), datetime.datetime(2020, 7, 1))

# print(df_stockload.head(10))    # 查看前几行
# print(df_stockload.index)    # 查看索引
# print(df_stockload.columns)  # 查看列名

# print(df_stockload.axes)  # 查看行和列的轴标签 等价于df_stockload.index和df_stockload.columns

# print(df_stockload.values)  # 访问全部元素数值

# print(df_stockload['Open'])   # 访问Open列
# print(type(df_stockload['Open']))   # 查看列类型

# print(df_stockload[0:1])
# print(type(df_stockload[0:1])) #查看行类型

# print(df_stockload.loc['2020-06-02'])
# print(df_stockload.loc['2020-06-02', ['High', 'Low']])

# print(df_stockload.iloc[0:2, 0:1])
# print(df_stockload.iloc[[0,2],[0,1]])
# print(df_stockload.iloc[0:2])

