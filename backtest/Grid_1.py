import numpy as np
import pandas as pd
import backtrader as bt
import datetime as dt
import matplotlib as plt


class SMAStrategy(bt.Strategy):
    params = (
        ('printlog', False),
        ('period', 200),
        ('dense', 20),
        ('neutral', None)
    )

    def __init__(self):
        self.close = self.data0.close
        # print(self.data0.getlinealiases())
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.last_index = None
        self.highest = bt.indicators.Highest(self.data.high, period=400, subplot=False)
        self.lowest = bt.indicators.Lowest(self.data.low, period=400, subplot=False)
        self.middle = (self.highest + self.lowest) / 2

    def next(self):
        order_range = np.linspace(self.lowest[0], self.highest[0], self.params.dense)
        index = len(order_range[order_range < self.close[0]])

        if self.last_index is None:
            self.last_index = index
        elif index != self.last_index:
            # diff = index - self.last_index
            percent = 1 - 2 * (index / (self.params.dense + 1))
            print('mid  :', self.middle[0])
            print('close:', self.close[0])
            self.order = self.order_target_percent(target=percent)
            self.last_index = index

        # print('当前持仓量', self.broker.getposition(self.data).size)
        # print('当前持仓成本', self.broker.getposition(self.data).price)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm
                     )
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm
                          )
                         )
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))


class CommInfoFractional(bt.CommissionInfo):
    def getsize(self, price, cash):
        return self.p.leverage * (cash / price)


if __name__ == '__main__':
    df = pd.read_csv('BTCUSDT-1h.csv')
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    start_date = df.index[0]
    end_date = df.index[-1]

    cerebro = bt.Cerebro()
    data = bt.feeds.PandasData(dataname=df, fromdate=start_date, todate=end_date)
    cerebro.adddata(data)

    cerebro.addstrategy(SMAStrategy)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')

    cerebro.broker.setcash(10000.0)
    # cerebro.broker.setcommission(commission=0.001)
    commission = 0.001
    comminfo = CommInfoFractional(commission=0.001)
    cerebro.broker.addcommissioninfo(comminfo)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=10)
    result = cerebro.run()

    print('Sharpe Ratio: ', result[0].analyzers.SharpeRatio.get_analysis()['sharperatio'])
    print('Draw Down: ', result[0].analyzers.DrawDown.get_analysis()['max']['drawdown'])

    cerebro.plot()
