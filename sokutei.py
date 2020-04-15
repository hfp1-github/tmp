import os
import sys
import re
import pandas as pd
from time import sleep
import subprocess
from datetime import datetime as dt
import argparse, textwrap
import cProfile
import pstats
import io

def output_cProfile_to_text(filepath):
    s = io.StringIO()
    ps = pstats.Stats(filepath, stream=s).sort_stats('tottime')
    ps.print_stats()
    filename, _ = os.path.splitext(filepath)

    with open(filename + '.txt', 'w') as f:
        f.write(s.getvalue())

def run_test(command, suffix='', interval=1):
    command = 'python3 -m cProfile -o profile_{}.stats {}'.format(suffix, command)
    print(command)
    # コマンド実行
    proc_main = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE, encoding='utf-8')

    # psコマンド(grepとこのファイルの実行を除外)
    ps_cmd = 'grep -v *{}  | grep "{}"'.format(__file__, command)
    timestamp_fmt = "%Y/%m/%d %H:%M:%S"

    # proc
    proc_cmd = ''.format(proc_main.pid)

    ret = None
    ps_grep = []
    ps_time = []

    # プロセス終了(ret = None)までループ
    while ret is None:
        proc_status = subprocess.Popen(proc_cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
        proc_status_str = str(proc_status.communicate()[0])
        
        ps_proc = subprocess.Popen(ps_cmd, shell=True, stdout=subprocess.PIPE, encoding='utf-8')
        ps_grep.append(str(ps_proc.communicate()[0]))
        ps_time.append(str(dt.now().strftime(timestamp_fmt)))

        sleep(interval)
        ret = proc_main.poll()

    # ---後処理
    # ps: 連続スペース削除、スペースでsplit → csv保存
    ps_str = []
    r_space = re.compile(r" +")
    ps_str = [r_space.sub(" ", str.rstrip(s)).split(' ') for s in ps_grep]
    ps_str = [s if s[0] != '' else s[1:] for s in ps_str]
    df_ps = pd.DataFrame(ps_str, index=ps_time)
    df_ps.to_csv('ps_{}.csv'.format(suffix), header=False, encoding='utf-8')

    # console
    with open('console_{}.txt.'.format(suffix), 'w', encoding='utf-8') as f:
        f.write(str(proc_main.communicate()[0]))

    # proc
    with open('proc_{}.txt'.format(suffix), 'w', encoding='utf-8') as f:
        f.write(proc_status_str)
    
    output_cProfile_to_text("profile_{}.stats".format(suffix))




parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=\
        textwrap.dedent('''\
            pythonコマンド用の性能測定ツールです。
        '''
    ))

parser.add_argument('command', 
                    help= textwrap.dedent('''\
                    測定対象のスクリプトと引数。
                    ダブルコロンで囲む。
                    「python」は記載不要。
                    '''))
parser.add_argument('-s', '--suffix', help='ファイル末尾につけるsuffix', default='')
parser.add_argument('-i', '--interval', help='ps, procの実行間隔(秒)', type=float, default=1.0)

# ---parse
args = parser.parse_args()

run_test(args.command, args.suffix, args.interval)