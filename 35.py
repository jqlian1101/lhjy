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



class ST_Account:

    def __init__(
            self,
            init_hold={},
            init_cash=1000000,
            commission_coeff=0,
            tax_coeff=0):
        """
        :param [dict] init_hold         初始化时的股票资产
        :param [float] init_cash:         初始化资金
        :param [float] commission_coeff:  交易佣金 :默认 万2.5(float类型 0.00025) 此处例程设定为0
        :param [float] tax_coeff:         印花税   :默认 千1.5(float类型 0.001) 此处例程设定为0
        """
        self.hold = init_hold
        self.cash = init_cash

    def hold_available(self, code=None):
        """可用持仓"""
        if code in self.hold:
            return self.hold[code]

    def cash_available(self):
        """可用资金"""
        return self.cash

    def latest_assets(self, price):
        # return the lastest hold 总资产
        assets_val = 0
        for code_hold in self.hold.values():
            assets_val += code_hold * price
        assets_val += self.cash
        return assets_val

    def send_order(self, code=None, amount=None, price=None, order_type=None):
        if order_type == 'buy':
            self.cash = self.cash - amount * price
            self.hold[code] = amount
        else:
            self.cash = self.cash + amount * price
            self.hold[code] -= amount
            if self.hold[code] == 0:
                del self.hold[code]  # 删除该股票


class draw_graph:

    def __init__(self, draw_obj, stock_obj):

        self.fig = draw_obj
        self.stockdat = stock_obj
        # 创建子图表
        gs = gridspec.GridSpec(3, 1, left=0.05, bottom=0.1, right=0.96, top=0.96, wspace=None, hspace=0.05,
                               height_ratios=[4, 2, 2])
        self.gtrade = self.fig.add_subplot(gs[0, :])
        self.gtotal = self.fig.add_subplot(gs[1, :])
        self.gprofit = self.fig.add_subplot(gs[2, :])

        # 初始化变量
        self.skip_days = 0
        self.account_a = ST_Account(dict(), 100000)  # 账户A 持股数目和初始资金

        self.account_b = ST_Account(dict(), 100000)  # 账户B 持股数目和初始资金

    def draw_trade(self):
        self.stockdat['max_close'] = df_stockload['Close'].expanding().max()
        self.stockdat[['max_close', 'Close']].plot(grid=True, ax=self.gtrade)

        for kl_index, today in self.stockdat.iterrows():
            # 买入/卖出执行代码
            if today.signal == 1 and self.skip_days == 0:  # 买入
                start = self.stockdat.index.get_loc(kl_index)
                print("buy", kl_index)
                self.skip_days = -1

                self.account_a.send_order(code="600410.SS",
                                          amount=int(
                                              self.account_a.cash_available() / today.Close),
                                          price=today.Close, order_type='buy')
                self.account_b.send_order(code="600410.SS",
                                          amount=int(
                                              self.account_b.cash_available() * 0.01 / today.atr14),
                                          price=today.Close, order_type='buy')

                self.gtrade.annotate('买入', xy=(kl_index, self.stockdat.Close.asof(kl_index)),
                                     xytext=(kl_index, self.stockdat.Close.asof(
                                         kl_index) + 2),
                                     arrowprops=dict(facecolor='r', shrink=0.1), horizontalalignment='left',
                                     verticalalignment='top')

            elif today.signal == 0 and self.skip_days == -1:  # 卖出 避免未买先卖
                end = self.stockdat.index.get_loc(kl_index)
                print("sell", kl_index)
                self.skip_days = 0

                self.account_a.send_order(code="600410.SS",
                                          amount=self.account_a.hold_available(
                                              code="600410.SS"),
                                          price=today.Close, order_type='sell')
                self.account_b.send_order(code="600410.SS",
                                          amount=self.account_b.hold_available(
                                              code="600410.SS"),
                                          price=today.Close, order_type='sell')

                if self.stockdat.Close[end] < self.stockdat.Close[start]:  # 赔钱显示绿色
                    self.gtrade.fill_between(self.stockdat.index[start:end], 0, self.stockdat.Close[start:end], color='green',
                                             alpha=0.38)
                else:  # 赚钱显示红色
                    self.gtrade.fill_between(self.stockdat.index[start:end], 0, self.stockdat.Close[start:end], color='red',
                                             alpha=0.38)
                self.gtrade.annotate('卖出', xy=(kl_index, self.stockdat.Close.asof(kl_index)),
                                     xytext=(kl_index + datetime.timedelta(days=5),
                                             self.stockdat.Close.asof(kl_index) + 2),
                                     arrowprops=dict(facecolor='g', shrink=0.1), horizontalalignment='left',
                                     verticalalignment='top')
            # 账户A 资产曲线
            # 账户B 资产曲线
            self.stockdat.loc[kl_index, 'total_a'] = self.account_a.latest_assets(
                today.Close)
            self.stockdat.loc[kl_index, 'total_b'] = self.account_b.latest_assets(
                today.Close)

    def draw_total(self):

        # 计算资金曲线当前的滚动最高值
        self.stockdat[['total_a', 'total_b']].plot(grid=True, ax=self.gtotal)

    def draw_profit(self):
        # 计算基准收益/趋势突破策略收益
        self.stockdat['benchmark_profit'] = np.log(
            self.stockdat.Close / self.stockdat.Close.shift(1))
        self.stockdat['trend_profit'] = self.stockdat.signal * \
            self.stockdat.benchmark_profit
        self.stockdat[['benchmark_profit', 'trend_profit']
                      ].cumsum().plot(grid=True, ax=self.gprofit)

    def draw_config(self):
        self.draw_trade()
        self.draw_total()
        self.draw_profit()
        # 图表显示参数配置
        for label in self.gtrade.xaxis.get_ticklabels():
            label.set_visible(False)
        for label in self.gtotal.xaxis.get_ticklabels():
            label.set_visible(False)
        for label in self.gprofit.xaxis.get_ticklabels():
            label.set_rotation(45)
            label.set_fontsize(10)  # 设置标签字体
        self.gtrade.set_xlabel("")
        self.gtrade.set_title(u'华胜天成 收益与风险度量')
        self.gtotal.set_xlabel("")


df_stockload = GetStockDatApi("600410.SS", datetime.datetime(
    2018, 1, 1), datetime.datetime(2019, 4, 1))  # 华胜天成

fig = plt.figure(figsize=(16, 8), dpi=100, facecolor="white")  # 创建fig对象
app_graph_a = draw_graph(fig, df_stockload)
app_graph_a.draw_config()
plt.show()
