# -*- coding:UTF-8 -*-

# pyecharts

#Overlap+Grid方法绘制交易行情界面
import pandas_datareader.data as web
import datetime
from pyecharts import Grid,Overlap,Line,Bar,EffectScatter,Kline

# example1 senior quotations
df_stockload = web.DataReader("000001.SS", "yahoo", datetime.datetime(2018, 1, 1), datetime.date.today())
df_stockload['Ma20'] = df_stockload.Close.rolling(window=20).mean()  
df_stockload['Ma30'] = df_stockload.Close.rolling(window=30).mean()  
df_stockload['Ma60'] = df_stockload.Close.rolling(window=60).mean()  

# python3.7打印
print(df_stockload.tail())  # 查看前几行
print(df_stockload.columns)  # 查看列名
print(df_stockload.index)  # 查看索引
print(df_stockload.describe())  # 查看各列数据描述性统计

kline = Kline("行情显示图",title_pos="40%")
ohlc = list(zip(df_stockload.Open,df_stockload.Close,df_stockload.Low,df_stockload.High))
dates = df_stockload.index.strftime('%Y-%m-%d')
print(type(dates))
print(type(df_stockload.index))

#is_datazoom_show=True 图表数据缩放  指定 markLine 位于开盘或者收盘上
kline.add("日K", dates, ohlc, is_datazoom_show=True,is_xaxis_show=False, \
        legend_pos="85%",legend_orient="vertical",legend_top="45%",mark_line=["max"], mark_point=["max"])
line = Line()
indic_name_list = ['Ma20','Ma30','Ma60']
for indic_ma in indic_name_list:
      line.add(indic_ma, dates, df_stockload[indic_ma].tolist(),is_smooth=True)

bar = Bar()

volume_rise=[df_stockload.Volume[x] if df_stockload.Close[x] > df_stockload.Open[x] else "0" for x in range(0, len(df_stockload.index))]
volume_drop=[df_stockload.Volume[x] if df_stockload.Close[x] <= df_stockload.Open[x] else "0" for x in range(0, len(df_stockload.index))]
#is_yaxis_show=True 显示y坐标轴
#datazoom_xaxis_index=[0, 1] 设置dataZoom控制索引为 0,1两个x 轴
bar.add("rvolume", dates, volume_rise, is_stack=True)
bar.add("dvolume", dates, volume_drop, is_stack=True,legend_pos="85%",legend_orient="vertical",legend_top="30%", \
        is_datazoom_show=True,tooltip_tragger="axis", is_legend_show=True, is_yaxis_show=True, datazoom_xaxis_index=[0, 1])

# buy and sell
v1 = dates[50]
v2 = df_stockload['Low'].iloc[50]
es = EffectScatter("buy")
es.add("buy", [v1], [v2])
v1 = dates[88]
v2 = df_stockload['High'].iloc[88]
es.add( "sell", [v1], [v2], symbol="pin",)

overlap = Overlap()
overlap.add(kline)
overlap.add(line)
overlap.add(es)

grid = Grid()
grid.add(bar, grid_top="70%",grid_right="15%")
grid.add(overlap, grid_bottom="30%",grid_right="15%")

grid.show_config()
grid.render(r'total.html')