import numpy as np
import pandas as pd
import backtrader as bt
import datetime as dt
import matplotlib as plt


class MACDStrategy(bt.Strategy):
    params = (
        ('printlog', False),
        ('period', 200),
        ('fast_period', 12),
        ('slow_period', 26),
        ('signal_period', 9),
        ('order_price', None)
    )


    def __init__(self):
        self.close = self.data0.close
        # print(self.data0.getlinealiases())
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # self.breakup = max(self.data0.close[-30:-5]) < max(self.data0.close[-5:0])
        # self.breakdown = min(self.data0.close[-30:-5]) > min(self.data0.close[-5:0])
        self.ema = bt.indicators.EMA(self.close, period=self.params.period)
        self.macd = bt.indicators.MACD(self.close)

    def next(self):
        # print('macd    ', self.macd.lines.macd[0])
        # print('signal  ', self.macd.lines.signal[0])
        macd = self.macd.lines.macd
        signal = self.macd.lines.signal


        if not self.position:
            if self.close[0] < self.ema[0] and macd[0] < 0 and signal[0] < 0 and macd[-1] < signal[-1] and macd[0] > signal[0]:
                self.order = self.buy(exectype=bt.Order.Market)
                # print(self.order)
        else:
            hold_price = self.broker.getposition(self.data).price
            if self.close[0] > 1.5*hold_price or self.close[0] < 0.95*hold_price:
                self.order = self.sell()
            # print(self.close[0] - hold_price)
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
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))


if __name__ == '__main__':
    df = pd.read_csv('BTCUSDT-1h.csv')
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)
    start_date = df.index[0]
    end_date = df.index[-1]

    cerebro = bt.Cerebro()
    data = bt.feeds.PandasData(dataname=df, fromdate=start_date, todate=end_date)
    cerebro.adddata(data)

    cerebro.addstrategy(MACDStrategy)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')

    cerebro.broker.setcash(10000.0)
    # cerebro.broker.setcommission(commission=0.001)

    cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    result = cerebro.run()

    print('Sharpe Ratio: ', result[0].analyzers.SharpeRatio.get_analysis()['sharperatio'])
    print('Draw Down: ', result[0].analyzers.DrawDown.get_analysis()['max']['drawdown'])

    cerebro.plot()