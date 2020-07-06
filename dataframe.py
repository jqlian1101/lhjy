import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt


df_stockload = web.DataReader('000001.SS', "yahoo", datetime.datetime(2017,1,1), datetime.date.today())

# print(df_stockload.head())

# print(df_stockload.tail())

# print(df_stockload.columns)

# print(df_stockload.index)

# print(df_stockload.shape)

# print(df_stockload.describe())

# print(df_stockload.info())

#绘制收盘价
df_stockload.Close.plot(c='b')
plt.legend(['Close','30ave','60ave'],loc='best')
plt.show()