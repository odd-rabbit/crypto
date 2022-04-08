import time
import numpy as np
from datetime import datetime
import pandas as pd
import rest_mfc


def history_kline(pair, interval, start, end=None, limit=2000):
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
    t_list = np.append(np.arange(start, end, second * limit), end) * 1000
    df = None
    for i in range(1, len(t_list)):
        t_df = rest_mfc.API().kline(pair, interval, str(int(t_list[i-1])), str(int(t_list[i])))
        print(len(t_df))
        if df is None:
            df = t_df
        else:
            df = pd.concat([df, t_df])
        time.sleep(0.5)
    return cleaner(df)


def cleaner(df):
    df = df.reset_index(level=0)
    df = df.drop_duplicates()
    t = np.array(df['T'])
    time = np.append(np.arange(t[0], t[-1], df['T'].diff()[1:].mode()[0]), t[-1])
    new_df = pd.DataFrame({'T': time})
    new_df = pd.concat([df.set_index('T'), new_df.set_index('T')], axis=1, join='outer')
    new_df = new_df.fillna(method='ffill')
    return new_df


if __name__ == '__main__':
    res = history_kline('BTC_USDT', '1m', '20210101', '20220401')
    print(res)
    res.to_csv('1m_210101_220401.csv')
    # print(cleaner(pd.read_csv('15m_210101_220401.csv'))['T'].diff()[1:].mean())
