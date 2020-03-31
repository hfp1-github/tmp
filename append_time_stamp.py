import os
import pandas as pd
import numpy as np
import argparse, textwrap
from distutils.util import strtobool

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=\
        textwrap.dedent('''\
            データにタイムスタンプを付与する。
                サポート形式: .csv, .npy
        '''
    ))

parser.add_argument('filepath', help='タイムスタンプを付与するファイル')
parser.add_argument('exists_header', help='入力ファイルにヘッダがあるかどうか', type=strtobool)
parser.add_argument('add_header', help='出力ファイルにヘッダを付与するかどうか', type=strtobool)
parser.add_argument('exists_timestamp', help='既にタイムスタンプがあるかどうか。あるなら置換する。', type=strtobool)
parser.add_argument('-o', '--output_suffix', help='出力ファイルに付与するサフィックス', default='conv')
parser.add_argument('-s', '--start_time', help='タイムスタンプの開始時刻', default='2019-1-1 9:00')
parser.add_argument('-k', '--interval_kind', default='S',
            help= textwrap.dedent('''\
            タイムステップの種類(pandas形式). 
                日: D
                時間: H
                分: T
                秒: S
                ミリ秒: L
                マイクロ: U
                ナノ秒: N
            '''))
parser.add_argument('-i', '--interval', help='タイムステップ', default='1')
parser.add_argument('-f', '--format', default=None,
            help= textwrap.dedent('''\
            タイムスタンプフォーマット(pandas形式).
                例.
                    "%%Y/%%m/%%d %%H:%%M:%%S"
                    "%%Y/%%m/%%d %%H:%%M:%%S.%%f"
                    "%%Y%%m%%d%%H%%M%%S"
                    "%%Y%%m%%dT%%H%%M%%S"
            '''))

# ---parse
args = parser.parse_args()
filepath = args.filepath
exists_header = 0 if args.exists_header else None
add_header = args.add_header if not args.exists_header else False
index_col = 0 if args.exists_timestamp else None
start_time = args.start_time
time_kind = args.interval_kind
interval = args.interval
freq = interval+time_kind
output_suffix = args.output_suffix
time_stamp_format = args.format

print('--- Start.')
if not os.path.exists(filepath):
    raise Exception('File {} is not found.'.format(filepath))

# ---check extend
filename , ext = os.path.splitext(filepath)
if ext == '.csv':
    df = pd.read_csv(filepath, encoding='utf-8', header=exists_header, index_col=index_col)
if ext == '.npy':
    df = np.load(filepath)
    df = pd.DataFrame(df)

# ---create timestamp
df_date = pd.date_range(start=start_time, periods=len(df), freq=freq)

# change timestamp format 
if time_stamp_format is not None:
    df_date = pd.Series(df_date).dt.strftime(time_stamp_format)
df = df.set_index(df_date)

# ---save <filename>_<prefix>.csv
savepath = os.path.join(filename + '_' + output_suffix + '.csv')
df.to_csv(savepath, index=True, header=add_header)

print('append time stamp: {} to {}'.format(df.index[0], df.index[-1]))
print('save as: {}'.format(savepath))

print('--- End.')
