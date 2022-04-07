import time
import numpy as np
from datetime import datetime
import pandas as pd
import rest_mfc


def history_kline(pair, interval, start, end=None, limit=1000):
    if isinstance(start, str):
        start = pd.to_datetime(start).timestamp()
    if isinstance(end, str):
        end = pd.to_datetime(end).timestamp()
    else:
        end = time.time()
    if interval[-1] == 'm':
        second = int(interval[:-1]) * 60
    elif interval[-1] == 'h':
        second = int(interval[:-1]) * 60 * 60
    elif interval[-1] == 'd':
        second = int(interval[:-1]) * 60 * 60 * 24
    else:
        print('History_kline error!')
        return
    t_list = np.arange(start, end, second)
    return t_list


if __name__ == '__main__':
    print(history_kline('BTC_USDT', '1d', '20220101', '20220401'))
