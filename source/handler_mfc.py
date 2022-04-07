import pandas as pd
import numpy as np
import os


class Handler(object):
    def __init__(self, info):
        self.info = info
        if info['message'] == 'Success':
            self._checker()
        elif info['message'] == 'Connected':
            print('WebSocketApp is connected!')
        elif info['message'] == 'Subscribed':
            print('Channels are subscribed!')
        elif info['message'] == 'Unsubscribed':
            print('Channels are unsubscribed!')
        else:
            print('Hanlder error!')

    def _checker(self):
        topic = self.info['topic'].split(':')[0]
        if topic == 'ticker':
            result = self._ticker()
        elif topic == 'price':
            result = self._price()
        elif topic == 'orderbook':
            result = self._orderbook()
        else:
            print('Topic checker error!')
            return
        self._to_csv(result)

    def _to_csv(self, result):
        name = self.info['topic'].replace(':', '_')
        if os.path.isfile(name+'.csv'):
            result.to_csv(name+'.csv', mode='a', index=False, header=False)
        else:
            result.to_csv(name+'.csv', index=False)

    def _ticker(self):
        return pd.DataFrame(self.info['data'], index=[0])[['T', 'c', 'b', 'a', 's']]

    def _price(self):
        return pd.DataFrame(self.info['data'], index=[0])

    def _orderbook(self):
        data = self.info['data']
        t = np.full(len(data['a']), data['T'])
        ap = np.array(data['a'])[:, 0]
        av = np.array(data['a'])[:, 1]
        bp = np.array(data['b'])[:, 0]
        bv = np.array(data['b'])[:, 1]
        return pd.DataFrame({'T': t, 'bp': bp, 'bs': bv, 'ap': ap, 'as': av})


if __name__ == '__main__':
    test = {'code': 0,
            'message': 'Success',
            'topic': 'orderbook:binance_BTC_USDT',
            'data': {'m': 'binance_BTC_USDT',
                     'a': [[43456.14, 5.99572], [43457.31, 0.05131], [43457.4, 1.16325], [43457.64, 0.00437],
                           [43458.44, 0.1153], [43460.0, 0.02301], [43460.49, 0.36], [43460.94, 0.0117],
                           [43461.76, 0.02301], [43462.33, 0.86999], [43462.34, 2.24623], [43462.56, 0.01],
                           [43463.11, 2.24963], [43463.13, 0.24], [43463.14, 0.02094], [43463.17, 0.01881],
                           [43463.22, 0.00675], [43464.05, 0.02], [43464.7, 1.63585], [43464.71, 0.23014]],
                     'b': [[43456.13, 1.7975], [43454.87, 0.185], [43453.45, 0.11505], [43453.28, 0.34512],
                           [43453.09, 0.00024], [43451.87, 0.11506], [43451.65, 0.01318], [43451.59, 0.01584],
                           [43451.54, 0.31067], [43451.47, 0.05731], [43450.69, 0.881], [43449.8, 0.881],
                           [43449.57, 0.99999], [43449.32, 0.99999], [43449.08, 0.31067], [43448.86, 0.99999],
                           [43448.46, 0.99999], [43448.01, 0.34514], [43447.29, 0.38875], [43447.28, 0.00029]],
                     'T': 1649318519265}}
    test2 = {'code': 0,
             'message': 'Success',
             'topic': 'ticker:binance_BTC_USDT',
             'data': {'T': 1649318904417,
                      'm': 'binance_BTC_USDT',
                      'o': 45369.6,
                      'c': 43468.6,
                      'l': 42727.3,
                      'h': 45453.9,
                      'a': 43468.6,
                      'A': 0.0,
                      'b': 43468.6,
                      'B': 0.0,
                      'C': -0.0419,
                      'bv': 59957.8,
                      'qv': 2635377517.0,
                      'r': 1.0036125,
                      'p': 1.0,
                      's': 2.3005106e-07}}
    Handler(test2)
