"""
    サンプルデータ作成用のスクリプト。
    以下を作成可能。
        sin, cos, 矩形波, のこぎり波, 三角波

    【注意】
        パラメータ類はハードコーディングされているため、必要に応じて書き換える。
        最低限mainの以下を書き換える。
            # --- setting下
                n
                T
            # --- set anomaly dataの各設定(推論用)
                df.loc[df_date[<index1>]:df_date[<index2>], <columns>] = <anomaly_value>

"""

import pandas as pd
import numpy as np

def create_sin(n, T, use_cos=False):
    """
    Args:
        n(int): 生成データ数
        T(list): 周期の配列
    Returns:
        周期Tのsinカーブの行列
    """

    x = np.arange(0, n)
    buf = np.zeros((len(T), n))

    for i, t in enumerate(T):
        if not use_cos:
            y = np.sin(2*np.pi*x/t)
        else:
            y = np.cos(2*np.pi*x/t)
        buf[i] = y
    return buf

def create_rect(n, T, min=0, max=1):
    """
    Args:
        n(int): 生成データ数
        T(list): 周期の配列
        min : 最小値
        max : 最大値
    Returns:
        周期Tの矩形波の行列
    """

    x = np.arange(0, n)
    buf = np.zeros((len(T), n))

    for i, t in enumerate(T):
        y = np.sin(2*np.pi*x/t)
        y[y>0] = max
        y[y<0] = min
        buf[i] = y

    return buf

def create_saw_tooth(n, T, pp=1):
    """
    Args:
        n(int): 生成データ数
        T(list): 周期の配列
        pp : pp振幅
    Returns:
        周期Tののこぎり波の行列
    """

    x = np.arange(0, n)
    buf = np.zeros((len(T), n))

    for i, t in enumerate(T):
        y = np.mod(x, t/2)
        y = y/y.max()*pp
        y = y - pp/2
        buf[i] = y

    return buf

def create_triangle(n, T, pp=1):
    """
    Args:
        n(int): 生成データ数
        T(list): 周期の配列
        pp : pp振幅
    Returns:
        周期Tの三角波の行列
    """

    x = np.arange(0, n)
    buf = np.zeros((len(T), n))

    for i, t in enumerate(T):
        y = np.arccos(np.cos(2*np.pi*x/t))
        y = y/y.max()*pp
        y = y - pp/2
        buf[i] = y

    return buf

def append_noize(data, n, order=0.05):
    """
    dataにノイズを付与。※ 元データを変更する
    Args:
        data: データ
        n: データ点数
        order: データに対するノイズの大きさ。
    """
    for data_col in data:
        pp = data_col.max() - data_col.min()
        noize = (np.random.rand(n)-0.5) * order * pp
        data_col += noize

if __name__ == "__main__":
    print('--- Start.')

    # --- setting
    # n: 作成点数, T: 作成データの周期のリスト
    n = 20000
    T = range(0, 361, 12)[1:] # 適当に周期のリストを作成
    savepath = 'anomaly_large_train.csv'
    start_time = '2019/1/1 9:00:00'
    time_stamp_format = r"%Y/%m/%d %H:%M:%S"
    freq = '1T' # D H T S
    noize_order = 0.05

    print('parameters')
    print('n: {}'.format(n))
    print('T: {}'.format([t for t in T]))
    print('start_time: {}'.format(start_time))
    print('freq: {}'.format(freq))
    print('time_stamp_format: {}'.format(time_stamp_format))
    print('noize_order: {}'.format(noize_order))
    print('')

    # --- create data.
    print('creating data...')
    data_sin = create_sin(n, T)
    data_cos = create_sin(n, T, use_cos=True)
    data_rect = create_rect(n, T)
    data_saw = create_saw_tooth(n, T)
    data_triangle = create_triangle(n, T)

    data = np.concatenate([data_sin, data_cos, data_rect, data_saw, data_triangle], 0)

    # set random noize
    append_noize(data, n, order=noize_order)

    # set data to dataframe.
    df = pd.DataFrame(data.T)

    # --- append timestamp
    df_date = pd.date_range(start=start_time, periods=n, freq=freq)
    df_date = pd.Series(df_date).dt.strftime(time_stamp_format)

    df = df.set_index(df_date)

    # --- set anomaly data(推論用に異常値を設定。手動で変更)
    df.loc[df_date[100]:df_date[110],0] = 5
    df.loc[df_date[1000]:df_date[1010],1] = 5
    df.loc[df_date[5000]:df_date[5100],2] = 5
    df.loc[df_date[10000]:df_date[10100],3] = 5
    df.loc[df_date[15000]:df_date[15010],10] = 5

    # save
    df.to_csv(savepath, encoding='utf-8')

    print('append time stamp: {} to {}'.format(df.index[0], df.index[-1]))
    print('--- End')
