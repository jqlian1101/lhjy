# -*- coding:UTF-8 -*-

# pyecharts 移动平均线
from pyecharts import Line
import pandas_datareader.data as web
import datetime

# example1 Line
line = Line("移动平均线图示例")

# df_stockload = web.DataReader("000001.SS", "yahoo", datetime.datetime(2018, 1, 1), datetime.date.today())
df_stockload = web.DataReader("000001.SS", "yahoo", datetime.datetime(2018, 1, 1), datetime.datetime(2019, 1, 1))
df_stockload['Ma20'] = df_stockload.Close.rolling(window=20).mean()  # pd.rolling_mean(df_stockload.Close,window=20)
df_stockload['Ma30'] = df_stockload.Close.rolling(window=30).mean()  # pd.rolling_mean(df_stockload.Close,window=30)
df_stockload['Ma60'] = df_stockload.Close.rolling(window=60).mean()  # pd.rolling_mean(df_stockload.Close,window=60)

dates = df_stockload.index.strftime('%Y-%m-%d')

indic_name_list = ['Ma20','Ma30','Ma60']
for indic_ma in indic_name_list:
      line.add(indic_ma, dates, df_stockload[indic_ma].tolist(), is_smooth=True, yaxis_min=0.9*min(df_stockload["Low"]))#is_smooth 平滑曲线显示

line.show_config()
line.render(r'average.html')