import csv
import os
from datetime import datetime
import re

# 读取日期数据
dates_dict = {}
with open('date.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        contest = row['contest']
        date_str = row['date']
        dates_dict[contest] = datetime.strptime(date_str, '%Y/%m/%d')

# 准备数据列表
data = []

# 遍历csv文件夹
csv_dir = './csv'
for filename in os.listdir(csv_dir):
    if not filename.endswith('.csv'):
        continue
        
    # 解析文件名
    base_name = filename[:-4]
    parts = base_name.split('_', 2)
    if len(parts) < 3:
        continue
        
    season = int(parts[0])
    contest_type = parts[1]
    city = parts[2]
    contest_name = f"{season}_{contest_type}_{city}"
    
    # 获取日期
    date_val = dates_dict.get(contest_name)
    
    # 检查列名
    filepath = os.path.join(csv_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        headers = [header.strip('\ufeff') for header in headers]  # 去除BOM头
        print(f"Processing {contest_name} with headers: {headers}")
        
        # 检查列
        has_rank = 'Rank' in headers
        has_school_rank = 'School Rank' in headers
        has_school = 'School' in headers
        has_team = 'Team' in headers
        has_solved = 'Solved' in headers
        has_penalty = 'Penalty' in headers
        has_medal = 'Medal' in headers
        has_problem = 'A' in headers
        has_members = 'Member1' in headers
        has_date = date_val is not None
        
    data.append({
        'season': season,
        'type': contest_type,
        'city': city,
        'date': date_val,
        'contest_name': contest_name,
        'has_rank': has_rank,
        'has_school_rank': has_school_rank,
        'has_school': has_school,
        'has_team': has_team,
        'has_solved': has_solved,
        'has_penalty': has_penalty,
        'has_medal': has_medal,
        'has_problem': has_problem,
        'has_members': has_members,
        'has_date': has_date
    })

# 排序函数
def contest_sort_key(item):

    # 类型权重: ICPC 优先于 CCPC
    type_weight = 0 if item['type'] == 'ICPC' else 1
    
    # 是否总决赛标识
    is_final = 1 if item['city'] in ['ECFinal', '总决赛'] else 0
    
    # 日期存在标识
    has_date_val = 0 if item['date'] is not None else 1
    
    # 日期值或替代值
    date_val = item['date'] or datetime.max
    
    # 城市排序值
    city_val = item['city'] if not is_final else "zzz_" + item['city']
    
    return (
        type_weight,         # 类型优先级
        item['season'],      # 赛季数字
        has_date_val,        # 日期存在标志
        date_val,            # 实际日期值
        is_final,            # 是否总决赛
        city_val             # 城市名
    )

# 对数据进行排序
data.sort(key=contest_sort_key)

# 生成Markdown表格
markdown_lines = [
    "|contest|Rank|School Rank|School|Team|Solved|Penalty|Medal|Problem|Members|Date|",
    "|---|---|---|---|---|---|---|---|---|---|---|"
]

# 检查符号函数
def check_symbol(condition):
    return '✅' if condition else ''

# 添加表格行
for item in data:
    line = (
        f"|{item['contest_name']}"
        f"|{check_symbol(item['has_rank'])}"
        f"|{check_symbol(item['has_school_rank'])}"
        f"|{check_symbol(item['has_school'])}"
        f"|{check_symbol(item['has_team'])}"
        f"|{check_symbol(item['has_solved'])}"
        f"|{check_symbol(item['has_penalty'])}"
        f"|{check_symbol(item['has_medal'])}"
        f"|{check_symbol(item['has_problem'])}"
        f"|{check_symbol(item['has_members'])}"
        f"|{check_symbol(item['has_date'])}|"
    )
    markdown_lines.append(line)

# 写入README.md文件
with open('README.md', 'w', encoding='utf-8') as f:
    intro = """# ICPC/CCPC 区域赛终榜汇总

- 原始文件在 org 文件夹下，经过 convert.py 解析后的 .csv 文件在 csv 文件夹下
- contests.csv 包含赛站日期信息
- 特别鸣谢：[xcpcio](https://github.com/xcpcio/xcpcio)、[RankLand](https://rl.algoux.org/collection/official)

## 数据完整性

"""
    f.write(intro)
    f.write('\n'.join(markdown_lines))

print("README.md generated successfully!")