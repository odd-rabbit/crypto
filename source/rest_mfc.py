import numpy as np
import requests
import pandas as pd


class API(object):
    def __init__(self):
        self.exchange = 'binance'
        self.api_key = 'JNJELCGY4A9OQWVXKQP3PYB5ZF3QUZY2CIWN1HN4'
        self.url = 'http://data.mifengcha.com/api/v3/'

    def price(self, coin=''):
        url = self.url + 'price'
        params = {
            'api_key': self.api_key,
            'slug': coin,
        }
        data = requests.get(url, params=params).json()
        return pd.DataFrame(data).set_index('T')

    def tickers(self, pair):
        url = self.url + 'tickers'
        pair = ','.join([self.exchange + '_' + p for p in pair])
        params = {
            'api_key': self.api_key,
            'market_pair': pair,
        }
        data = requests.get(url, params=params).json()
        df = pd.DataFrame(data)
        df['past'] = df['T'] - int(1000 * time.time())
        return df.set_index('T')

    def kline(self, pair, interval, start='', end=''):
        url = self.url + 'kline'
        params = {
            'api_key': self.api_key,
            'desc': self.exchange + '_' + pair,
            'interval': interval,
            'start': start,
            'end': end,
        }
        data = requests.get(url, params=params).json()
        return pd.DataFrame(data).set_index('T')

    def historical_price(self, pair, interval, start='', end=''):
        url = self.url + 'price/history'
        params = {
            'api_key': self.api_key,
            'slug': pair,
            'interval': interval,
            'start': start,
            'end': end,
        }
        data = requests.get(url, params=params).json()
        return pd.DataFrame(data).set_index('T')

    def orderbook(self, pair, limit=25):
        url = self.url + 'orderbook'
        params = {
            'api_key': self.api_key,
            'desc': self.exchange + '_' + pair,
            'limit': str(limit),
        }
        data = requests.get(url, params=params).json()
        t = np.full(len(data['a']), data['T'])
        ap = np.array(data['a'])[:, 0]
        av = np.array(data['a'])[:, 1]
        bp = np.array(data['b'])[:, 0]
        bv = np.array(data['b'])[:, 1]
        return pd.DataFrame({'Time': t, 'ap': ap, 'as': av, 'bp': bp, 'bs': bv})

    def trades(self, pair, limit=50):
        url = self.url + 'trades'
        params = {
            'api_key': self.api_key,
            'desc': self.exchange + '_' + pair,
            'limit': str(limit),
        }
        data = requests.get(url, params=params).json()
        df = pd.DataFrame(data).set_index('T').drop(['m'], axis=1)
        df['s'] = df['s'].replace('buy', 1).replace('sell', -1).replace('none', 0)
        return df


if __name__ == '__main__':
    import time

    # API().price('bitcoin').to_csv('tickers.csv')
    API().tickers(['BTC_USDT']).to_csv('tickers.csv')
    # API().kline('BTC_USDT', '1m').to_csv('kline.csv')
    # API().orderbook('BTC_USDT', 100).to_csv('book.csv')
    # API().trades('BTC_USDT', 100).to_csv('trade.csv')
    for i in range(5):
        time.sleep(1)
        # API().price('bitcoin').to_csv('price.csv', mode='a', header=False)
        API().tickers(['BTC_USDT']).to_csv('tickers.csv', mode='a', header=False)
        # API().kline('BTC_USDT', '1m').to_csv('kline.csv', mode='a', header=False)
        # API().trades('BTC_USDT', 100).to_csv('trade.csv', mode='a', header=False)
        # API().orderbook('BTC_USDT', 100).to_csv('book.csv', mode='a', header=False)
        print(i)
