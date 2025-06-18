import pandas as pd
import os
import shutil
from tqdm import tqdm

def export_formal_team_to_csv(path, output_path=None):
    """
    读取Excel文件中的"正式队伍"工作表，处理后导出为CSV文件
    
    参数:
    path (str): Excel文件路径
    output_path (str): 输出CSV路径(默认为同目录下的"正式队伍.csv")
    """
    # 设置默认输出路径
    if output_path is None:
        output_path = path.replace('.xlsx', '_正式队伍.csv')
    
    # 读取Excel文件
    try:
        # 读取整个工作表(不自动转换列名)
        df = pd.read_excel(path, sheet_name='正式队伍', header=None)
    except Exception as e:
        raise ValueError(f"读取文件失败: {str(e)}")
    
    # 检查第一行是否有且只有一个非空值
    first_row = df.iloc[0]
    non_empty_count = first_row.notnull().sum()
    
    # 如果第一行只有一个非空值，则删除该行
    if non_empty_count == 1:
        df = df.iloc[1:]
    
    # 导出为CSV文件
    df.to_csv(output_path, index=False, header=False, encoding='utf-8-sig')
    return output_path

def parse(name):
    xcpc = None
    if 'ICPC' in name or 'International' in name or '国际' in name:
        xcpc = 'ICPC'
    elif 'CCPC' in name or '中国' in name:
        xcpc = 'CCPC'
    assert xcpc is not None, f"无法解析竞赛类型: {name}"

    year = None
    offset = 1975 if xcpc == 'ICPC' else 2014
    if '第' in name and '届' in name:
        year = int(name.split('第')[1].split('届')[0].strip())
    elif '第' in name and '屆' in name:
        year = int(name.split('第')[1].split('屆')[0].strip())
    elif 'th' in name:
        year = int(name.split('th')[0].split()[-1].strip())
    elif '202' in name:
        year = name[name.index('202'): name.index('202') + 4]
        year = int(year) - offset
    assert year is not None, f"无法解析年份: {name}"

    city = None
    if '站' in name and '赛' in name:
        pos_zhan = name.index('站')
        pos_sai = name.rfind('赛', 0, pos_zhan)
        city = name[pos_sai + 1: pos_zhan].strip()
    elif '澳門' in name or 'macau' in name.lower():
        city = '澳门'
    elif 'Yinchuan' in name:
        city = '银川'
    elif '决赛' in name:
        city = '总决赛' if xcpc == 'CCPC' else 'ECFinal'
    elif 'East' in name and 'Final' in name:
        city = 'ECFinal'
    assert city is not None, f"无法解析城市: {name}"

    return year, xcpc, city


# 使用示例
if __name__ == "__main__":
    # excel_path = "your_file_path.xlsx"  # 替换为实际文件路径
    # try:
    #     csv_path = export_formal_team_to_csv(excel_path)
    #     print(f"文件已成功导出至: {csv_path}")
    # except Exception as e:
    #     print(f"处理过程中出错: {str(e)}")
    files = os.listdir('org')
    for file in tqdm(files, desc="Processing files"):
        if file.endswith('.xlsx'):
            year, xcpc, city = parse(file)
            csv_path = os.path.join('csv', f'{year}_{xcpc}_{city}.csv')
            export_formal_team_to_csv(os.path.join('org', file), output_path=csv_path)
        elif file.endswith('.csv'):
            year, xcpc, city = parse(file)
            csv_path = os.path.join('csv', f'{year}_{xcpc}_{city}.csv')
            shutil.copy(os.path.join('org', file), csv_path)