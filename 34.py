import pandas_datareader.data as web
import pandas as pd
import numpy as np
import datetime
import talib
import matplotlib.pyplot as plt

import matplotlib.gridspec as gridspec  # 分割子图


df_stockload = web.DataReader("600410.SS", "yahoo", datetime.datetime(
    2018, 10, 1), datetime.datetime(2019, 4, 1))

df_stockload['art14'] = talib.ATR(
    df_stockload.High.values, df_stockload.Low.values, df_stockload.Close.values, timeperiod=14)  # 计算ATR14
df_stockload['art21'] = talib.ATR(
    df_stockload.High.values, df_stockload.Low.values, df_stockload.Close.values, timeperiod=21)  # 计算ATR21

