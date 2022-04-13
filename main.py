from EmailAlert import sent
from source.rest_mfc import API
import pandas as pd
import numpy as np


def rsi(data, window):
    import talib
    if len(data) <= window:
        print('Input length is not enough')
        return
    close = np.array(data['c'])[-window-1:]
    ind = talib.RSI(close, window)[-1]
    ind = np.where(ind < 30, -1, ind)
    ind = np.where(ind > 70, 1, ind)
    ind = np.where((30 <= ind) & (ind <= 70), 0, ind)
    signal = ind
    return signal


if __name__ == '__main__':
    import time
    import datetime

    SLEEP = 10
    status = True
    while status:
        OHLCV = API().kline('BTC_USDT', '15h')
        # 将来需要展开
        res = rsi(OHLCV, 21)
        # 文本处理
        order_price = OHLCV.iloc[-1, 0]
        time_price = datetime.datetime.fromtimestamp(int(OHLCV.index[-1]/1000))
        text = f'Position {res} with closing price {order_price} at time {time_price}'
        sent(text)
        print(text)
        time.sleep(SLEEP)
