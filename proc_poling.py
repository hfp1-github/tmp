import os
import shutil
import argparse, textwrap
import subprocess
from time import sleep
from typing import List
# from distutils.util import strtobool

def copy_proc_status(pids: List[str], output_dir: str = './'):
    # /proc/<pid>/status をコピーする。既存データは上書き
    for pid in pids:
        src = f'/proc/{pid}/status'
        savepath = os.path.join(output_dir, f'proc_{pid}.txt')
        try:
            shutil.copyfile(src, savepath)
        except:
            pass

def grep_pids(grep_words: str, exclude_pids: List[str] = None)->List[str]:
    """psコマンドをgrepし、ヒットしたプロセスのpidを返します。
    ヒットしなかった場合、空のリストを返します。

    Args:
        grep_words (str): grepのキーワードのリスト
        exclude_pids (List[str], optional): 除外したいpid. Defaults to None.

    Returns:
        List[str]: pidのリスト
    """    
    ps_cmd = ['ps', '-e', '-o', 'pid,cmd']
    grep_cmd_ingore = ['grep', '-v', 'grep']
    grep_cmd_include = ['grep']
    # キーワードを全てgrepするコマンド作成
    for word in grep_words:
        grep_cmd_include.extend(['-e', word])
    
    # psコマンドを実行し、grep
    ps_process = subprocess.Popen(ps_cmd, stdout=subprocess.PIPE)
    grep_process_ignore = subprocess.Popen(grep_cmd_ingore, stdin=ps_process.stdout, stdout=subprocess.PIPE)
    grep_process_include = subprocess.Popen(grep_cmd_include, stdin=grep_process_ignore.stdout, stdout=subprocess.PIPE)

    # grep結果取得、文字列に変換
    grep_results = grep_process_include.communicate()[0].decode()
    if len(grep_results) == 0:
        return []
    grep_results = grep_results.splitlines()

    # pid取得
    pids = [grep_line.split()[0] for grep_line in grep_results]

    # 除外するpidがある場合
    if exclude_pids:
        for pid in exclude_pids:
            if pid in pids:
                pids.remove(pid)
    
    return pids

def poling_proc(grep_words: str, output_dir: str = './', interval: int = 1):
    """
    指定したキーワードでpsコマンドの結果ををgrepし、
    ヒットしたプロセスの proc/<pid>/status を定期的にコピーします。

    Args:
        grep_words (str): grepのキーワードのリスト
        output_dir (str, optional): 出力ディレクトリ. Defaults to './'.
        interval (int, optional): 実行周期. Defaults to 1.
    """    
    self_pid = str(os.getpid())
    while True:
        # pid取得(このプロセスは除外)
        pids = grep_pids(grep_words, [self_pid])
        # procを取得(既存データは上書き)
        copy_proc_status(pids, output_dir)

        sleep(interval)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=\
            textwrap.dedent('''\
                指定したキーワードでpsコマンドの結果ををgrepし、
                ヒットしたプロセスの proc/<pid>/status を定期的にコピーします。
            '''
        ))

    parser.add_argument('grep_words', help='grepするキーワード', type=str, nargs='+')
    parser.add_argument('-o', '--output_dir', help='結果出力先.', type=str, default='./')
    parser.add_argument('-i', '--interval', help='監視の周期.', type=float, default=1)

    # ---parse
    args = parser.parse_args()
    poling_proc(args.grep_words, args.output_dir, args.interval)

