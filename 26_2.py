# -*- coding:UTF-8 -*-

# pyecharts 柱状图
from pyecharts import Bar
import pandas_datareader.data as web
import datetime

# example1 Bar
bar = Bar('柱状图表渲染', '成交量显示')

df_stockload = web.DataReader("000001.SS", "yahoo", datetime.datetime(2018, 1, 1), datetime.datetime(2019, 1, 1))

# 数据转换
dates = df_stockload.index.strftime('%Y-%m-%d')

volume_rise=[df_stockload.Volume[x] if df_stockload.Close[x] > df_stockload.Open[x] else "0" for x in range(0, len(df_stockload.index))]
volume_drop=[df_stockload.Volume[x] if df_stockload.Close[x] <= df_stockload.Open[x] else "0" for x in range(0, len(df_stockload.index))]

bar.add("rvolume", dates, volume_rise, is_stack=True, label_color=["#218868"], is_datazoom_show=True)
bar.add("dvolume", dates, volume_drop, is_stack=True, label_color=["#FA8072"], is_datazoom_show=True)

bar.show_config()
bar.render(r'volume.html')#渲染图表，指定生成volume.html文件