import pandas as pd
import xlwings as xw
import argparse

parser = argparse.ArgumentParser(description='Process some integers.')

# 入力シート設定
input_sheet_name = '入力'
start_work_time_range = 'B4'
end_work_time_range = 'G4'
over_work_time_range = 'L4'

# システムのフォーマット
start_work_time_column_name = '始業時刻'
end_work_time_column_name = '終業時刻'
over_work_time_column_name  = '健康管理'

"""
    参考
    休憩数式
        =IF(ISBLANK(B5),"",(G5-SUM(B5,L5,$U$2)))
"""

print('--- Start.')

# 選択範囲取得
print('Get selection cells data.')
workbooks = xw.books
wb = workbooks.active
cells = wb.selection

# テキストベースで取得
cells.autofit
cells_text = []
for row in cells.rows:
    cells_text.append([s.api.text for s in row])

# df生成
df = pd.DataFrame(cells_text[1:], dtype=object, columns=cells_text[0], index=None)

# 余計なカラム行を削除
print('Remove unnecessary columns.')
df = df[df[start_work_time_column_name] != start_work_time_column_name]

# 残業時間列を生成
print('Create overtime data.')
join_ex = lambda x : ':'.join(x[0]) if len(x) != 0 else ""
df_zangyo = df[over_work_time_column_name].str.findall('(\d{1,2})h(\d{1,2})m').apply(join_ex)
df[over_work_time_column_name] = df_zangyo

# 出力
print('Output to daily report sheet.')
input_sheet = xw.sheets(input_sheet_name)
input_sheet.range(start_work_time_range).options(index=False, header=False).value = df[start_work_time_column_name]
input_sheet.range(end_work_time_range).options(index=False, header=False).value = df[end_work_time_column_name]
input_sheet.range(over_work_time_range).options(index=False, header=False).value = df[over_work_time_column_name]

print('--- End.')
