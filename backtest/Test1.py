import numpy as np
import pandas as pd
import backtrader as bt
import datetime as dt
import matplotlib as plt


class SMAStrategy(bt.Strategy):
    params = (
        ('printlog', False),
        ('period_30', 30),
        ('period', 5),
        ('hold_time', 0),
        ('order_price', None)
    )


    def __init__(self):
        self.dataclose = self.data0.close
        # print(self.data0.getlinealiases())
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # self.breakup = max(self.data0.close[-30:-5]) < max(self.data0.close[-5:0])
        # self.breakdown = min(self.data0.close[-30:-5]) > min(self.data0.close[-5:0])
        self.sma = bt.indicators.MovingAverageSimple(self.data0.close, period=self.params.period)

    def next(self):
        past_30 = self.data0.close.get(size=self.params.period_30)[:-self.params.period]

        if len(past_30) < 2:
            # print(past_30)
            return
        # print(self.sma[0])
        # print('past_30', max(past_30))
        # if self.params.hold_time > 0:
        #     self.params.hold_time -= 1
        if not self.position:
            if self.params.order_price is not None:
                if self.params.order_price < 0.98*self.dataclose[0]:
                    self.order = self.close()
            if 0.9995*self.sma[0] > max(past_30):
                self.params.order_price = self.dataclose[0]
                self.order = self.buy()
        else:
            print(self.position)
            if self.params.order_price is not None:
                if self.params.order_price > 1.02*self.dataclose[0]:
                    self.order = self.close()
            if 1.005*self.sma[0] < min(past_30):
                self.order = self.sell()
                self.params.order_price = self.dataclose[0]
        # if self.params.hold_time == 0:
        #     self.order = self.close()

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

def get_btc1m():
    PATH = 'Binance_BTCUSDT_minute.csv'
    df = pd.read_csv(PATH)
    df['Date'] = pd.to_datetime(df['date'])
    df = df.iloc[::-1]
    df.set_index('Date', inplace=True)
    df = df.rename(columns={'Volume USDT': 'volume'})
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df = df[-10000:]
    return df

def process_btc1m():
    PATH = 'Binance_BTCUSDT_minute.csv'
    df = pd.read_csv(PATH)
    df['Date'] = pd.to_datetime(df['date'])
    df = df.iloc[::-1]
    df.set_index('Date', inplace=True)
    # print(df['Date'])
    df = df.rename(columns={'Volume USDT': 'volume'})
    df = df[['open', 'high', 'low', 'close', 'volume']]
    df = df[-1000:]
    # print(df)
    start = df.index[0]
    end = df.index[-1]
    return df

if __name__ == '__main__':
    data = get_btc1m()
    start_date = data.index[0]
    end_date = data.index[-1]

    cerebro = bt.Cerebro()
    data = bt.feeds.PandasData(dataname=data, fromdate=start_date, todate=end_date)
    cerebro.adddata(data)

    cerebro.addstrategy(SMAStrategy)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='SharpeRatio')
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='DrawDown')

    cerebro.broker.setcash(1000000.0)
    # cerebro.broker.setcommission(commission=0.001)

    # cerebro.addsizer(bt.sizers.PercentSizer, percents=100)
    result = cerebro.run()

    print('Sharpe Ratio: ', result[0].analyzers.SharpeRatio.get_analysis()['sharperatio'])
    print('Draw Down: ', result[0].analyzers.DrawDown.get_analysis()['max']['drawdown'])

    cerebro.plot()