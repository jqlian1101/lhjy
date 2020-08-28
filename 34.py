import pandas_datareader.data as web
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import talib

import matplotlib.gridspec as gridspec  # 分割子图


#股票数据获取及处理接口
def GetStockDatApi(stockName=None, stockTimeS=None, stockTimeE=None, N1=15, N2=5, n_loss=0.8, n_win=2):

    stockdata = web.DataReader(stockName, "yahoo", stockTimeS, stockTimeE)

    stockdata['N1_High'] = stockdata.High.rolling(
        window=N1).max()  # 计算最近N1个交易日最高价
    stockdata['N1_High'] = stockdata.N1_High.shift(1)
    expan_max = stockdata.Close.expanding().max()
    stockdata['N1_High'].fillna(
        value=expan_max, inplace=True)  # 目前出现过的最大值填充前N1个nan

    stockdata['N2_Low'] = stockdata.Low.rolling(
        window=N2).min()  # 计算最近N2个交易日最低价
    stockdata['N2_Low'] = stockdata.N2_Low.shift(1)
    expan_min = stockdata.Close.expanding().min()
    stockdata['N2_Low'].fillna(
        value=expan_min, inplace=True)  # 目前出现过的最小值填充前N2个nan

    stockdata['atr14'] = talib.ATR(
        stockdata.High.values, stockdata.Low.values, stockdata.Close.values, timeperiod=14)  # 计算ATR14
        
    buy_price = 0
    for kl_index, today in stockdata.iterrows():
        if today.Close > today.N1_High:
            print('N_day_buy', kl_index, today.Close)
            buy_price = today.Close
            stockdata.loc[kl_index, 'signal'] = 1
        #到达收盘价少于买入价后触发卖出
        elif (buy_price != 0) and (buy_price > today.Close) and ((buy_price - today.Close) > n_loss * today.atr14):
            print('stop_loss_n', kl_index, today.Close, buy_price)
            stockdata.loc[kl_index, 'signal'] = 0
            buy_price = 0
        #到达收盘价多于买入价后触发卖出
        elif (buy_price != 0) and (buy_price < today.Close) and ((today.Close - buy_price) > n_win * today.atr14):
            print('stop_win_n', kl_index, today.Close, buy_price)
            stockdata.loc[kl_index, 'signal'] = 0
            buy_price = 0
        elif today.Close < today.N2_Low:
            print('N_day_sell', kl_index, today.Close, buy_price)
            stockdata.loc[kl_index, 'signal'] = 0
            buy_price = 0
        else:
            pass

    stockdata['signal'].fillna(method='ffill', inplace=True)
    stockdata['signal'] = stockdata.signal.shift(1)
    stockdata['signal'].fillna(method='bfill', inplace=True)

    return stockdata



# 初始化变量
skip_days = 0
cash_hold = 100000  # 初始资金
posit_num = 0  # 持股数目
market_total = 0  # 持股市值

# 创建图表
fig = plt.figure(figsize=(10, 8), dpi=100, facecolor="white")  # 创建fig对象
gs = gridspec.GridSpec(3, 1, left=0.05, bottom=0.1, right=0.96,
                       top=0.96, wspace=None, hspace=0.05, height_ratios=[4, 2, 2])
graph_trade = fig.add_subplot(gs[0, :])
graph_total = fig.add_subplot(gs[1, :])
graph_profit = fig.add_subplot(gs[2, :])

# 获取股票交易数据
df_stockload = GetStockDatApi("600410.SS", datetime.datetime(
    2018, 10, 1), datetime.datetime(2019, 4, 1))

for kl_index, today in df_stockload.iterrows():
    # 买入/卖出执行代码
    if today.signal == 1 and skip_days == 0:  # 买入
        start = df_stockload.index.get_loc(kl_index)
        skip_days = -1
        posit_num = int(cash_hold / today.Close)  # 资金转化为股票
        cash_hold = 0
        graph_trade.annotate('买入', xy=(kl_index, df_stockload.Close.asof(kl_index)), xytext=(kl_index, df_stockload.Close.asof(
            kl_index)+2), arrowprops=dict(facecolor='r', shrink=0.1), horizontalalignment='left', verticalalignment='top')

    elif today.signal == 0 and skip_days == -1:  # 卖出 避免未买先卖
        end = df_stockload.index.get_loc(kl_index)
        skip_days = 0
        cash_hold = int(posit_num * today.Close)  # 股票转化为资金
        market_total = 0

        if df_stockload.Close[end] < df_stockload.Close[start]:  # 赔钱显示绿色
            graph_trade.fill_between(
                df_stockload.index[start:end], 0, df_stockload.Close[start:end], color='green', alpha=0.38)
        else:  # 赚钱显示红色
            graph_trade.fill_between(
                df_stockload.index[start:end], 0, df_stockload.Close[start:end], color='red', alpha=0.38)
        graph_trade.annotate('卖出', xy=(kl_index, df_stockload.Close.asof(kl_index)), xytext=(kl_index+datetime.timedelta(days=5),
                                                                                             df_stockload.Close.asof(kl_index)+2), arrowprops=dict(facecolor='g', shrink=0.1), horizontalalignment='left', verticalalignment='top')

    if skip_days == -1:  # 持股
        market_total = int(posit_num * today.Close)
        df_stockload.loc[kl_index, 'total'] = market_total
    else:  # 空仓
        df_stockload.loc[kl_index, 'total'] = cash_hold

# 计算基准收益/趋势突破策略收益
df_stockload['benchmark_profit'] = np.log(
    df_stockload.Close/df_stockload.Close.shift(1))
df_stockload['trend_profit'] = df_stockload.signal * \
    df_stockload.benchmark_profit
df_stockload[['benchmark_profit', 'trend_profit']
             ].cumsum().plot(grid=True, ax=graph_profit)

# 计算收盘价曲线当前的滚动最高值
df_stockload['max_close'] = df_stockload['Close'].expanding().max()
df_stockload[['max_close', 'Close']].plot(grid=True, ax=graph_trade)

# 计算资金曲线当前的滚动最高值
df_stockload['max_total'] = df_stockload['total'].expanding().max()
df_stockload[['max_total', 'total']].plot(grid=True, ax=graph_total)

# 计算资金曲线在滚动最高值之后所回撤的百分比
df_stockload['per_total'] = df_stockload['total'] / df_stockload['max_total']
min_point_total = df_stockload.sort_values(
    by=['per_total']).iloc[[0], df_stockload.columns.get_loc('per_total')]
max_point_total = df_stockload[df_stockload.index <= min_point_total.index[0]].sort_values(
    by=['total'], ascending=False).iloc[[0], df_stockload.columns.get_loc('total')]

# 标注滚动最大点及最大回撤点
graph_total.annotate('滚动最大点',
                     xy=(max_point_total.index[0], df_stockload.total.asof(
                         max_point_total.index[0])),
                     xytext=(max_point_total.index[0], df_stockload.total.asof(
                         max_point_total.index[0]) + 4),
                     arrowprops=dict(facecolor='yellow', shrink=0.1), horizontalalignment='left',
                     verticalalignment='top')
graph_total.annotate('最大回撤点',
                     xy=(min_point_total.index[0], df_stockload.total.asof(
                         min_point_total.index[0])),
                     xytext=(min_point_total.index[0], df_stockload.total.asof(
                         min_point_total.index[0]) + 4),
                     arrowprops=dict(facecolor='yellow', shrink=0.1), horizontalalignment='left',
                     verticalalignment='top')

# 图表显示参数配置
for label in graph_trade.xaxis.get_ticklabels():
    label.set_visible(False)
for label in graph_total.xaxis.get_ticklabels():
    label.set_visible(False)
for label in graph_profit.xaxis.get_ticklabels():
    label.set_rotation(45)
    label.set_fontsize(10)  # 设置标签字体
graph_trade.set_xlabel("")
graph_trade.set_title(u'华胜天成 收益与风险度量')
graph_total.set_xlabel("")

plt.show()
