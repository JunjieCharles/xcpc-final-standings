import csv
import os
from datetime import datetime
import re

# 判断字符串是否包含中文
def contains_chinese(text):
    if text is None:
        return False
    return bool(re.search('[\u4e00-\u9fff]', text))

contests = set()

# 读取日期数据
dates_dict = {}
with open('date.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        contest = row['contest']
        date_str = row['date']
        if not date_str:
            continue
        dates_dict[contest] = datetime.strptime(date_str, '%Y/%m/%d')
        contests.add(contest)

# 准备数据列表
data = []

# 遍历csv文件夹
csv_dir = './csv'
for filename in os.listdir(csv_dir):
    if not filename.endswith('.csv'):
        continue
        
    # 解析文件名
    base_name = filename[:-4]
    contests.add(base_name)

for contest in contests:
    parts = contest.split('_', 2)
    if len(parts) < 3:
        continue
        
    season = int(parts[0])
    contest_type = parts[1]
    city = parts[2]
    # contest_name = f"{season}_{contest_type}_{city}"
    
    # 获取日期
    date_val = dates_dict.get(contest)

    if date_val is not None and not os.path.exists(os.path.join(csv_dir, f"{contest}.csv")):
        has_rank = False
        has_school_rank = False
        has_school = False
        has_team = False
        has_solved = False
        has_penalty = False
        has_medal = False
        has_problem = False
        has_members = False
        has_date = True
        school_has_chinese = False
        members_has_chinese = False
    
    else:
        # 检查列名和内容
        filename = f"{contest}.csv"
        filepath = os.path.join(csv_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)
            headers = [header.strip('\ufeff') for header in headers]  # 去除BOM头
            # print(f"Processing file: {filename}, Headers: {headers}")
            
            # 检查列存在性
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
            
            # 检查School列内容语言
            school_col_index = headers.index('School') if has_school else -1
            school_has_chinese = False
            if has_school:
                # 最多检查前50行
                row_count = 0
                for row in reader:
                    if school_col_index < len(row):
                        text = row[school_col_index]
                        if text and contains_chinese(text):
                            school_has_chinese = True
                            break
                    row_count += 1
                    if row_count >= 50:  # 最多检查50行
                        break
                # 重置文件指针到开头（跳过标题行）
                f.seek(0)
                next(reader)  # 跳过标题行
                
            # 检查Members列内容语言 (检查Member1)
            members_col_index = headers.index('Member1') if has_members else -1
            members_has_chinese = False
            if has_members:
                # 最多检查前50行
                row_count = 0
                for row in reader:
                    if members_col_index < len(row):
                        text = row[members_col_index]
                        if text and contains_chinese(text):
                            members_has_chinese = True
                            break
                    row_count += 1
                    if row_count >= 50:  # 最多检查50行
                        break
    
    data.append({
        'season': season,
        'type': contest_type,
        'city': city,
        'date': date_val,
        'contest_name': contest,
        'has_rank': has_rank,
        'has_school_rank': has_school_rank,
        'has_school': has_school,
        'has_team': has_team,
        'has_solved': has_solved,
        'has_penalty': has_penalty,
        'has_medal': has_medal,
        'has_problem': has_problem,
        'has_members': has_members,
        'has_date': has_date,
        'school_has_chinese': school_has_chinese if has_school else False,
        'members_has_chinese': members_has_chinese if has_members else False
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
    "|Contest|Date|Rank|School|Team|Solved|Penalty|Medal|Problems|Members|",
    "|---|---|---|---|---|---|---|---|---|---|"
]

# 检查符号函数 - 通用
def check_symbol(condition):
    return '✅' if condition else ''

# 检查符号函数 - School列专用
def check_school_symbol(has_column, has_chinese):
    if not has_column:
        return ''
    return '✅' if has_chinese else '🔤'

# 检查符号函数 - Members列专用
def check_members_symbol(has_column, has_chinese):
    if not has_column:
        return ''
    return '✅' if has_chinese else '🔤'

# 添加表格行
for item in data:
    line = (
        f"|{item['contest_name']}"
        f"|{item['date'].strftime('%Y/%m/%d') if item['date'] else ''}"
        f"|{check_symbol(item['has_rank'])}"
        # f"|{check_symbol(item['has_school_rank'])}"
        f"|{check_school_symbol(item['has_school'], item['school_has_chinese'])}"
        f"|{check_symbol(item['has_team'])}"
        f"|{check_symbol(item['has_solved'])}"
        f"|{check_symbol(item['has_penalty'])}"
        f"|{check_symbol(item['has_medal'])}"
        f"|{check_symbol(item['has_problem'])}"
        f"|{check_members_symbol(item['has_members'], item['members_has_chinese'])}"
        # f"|{check_symbol(item['has_date'])}|"
    )
    markdown_lines.append(line)

# 写入README.md文件
with open('README.md', 'w', encoding='utf-8') as f:
    intro = """# ICPC/CCPC 区域赛终榜汇总

- 榜单仅包含正式队伍
- 原始文件在 org 文件夹下，解析后的文件在 csv 文件夹下
- contests.csv 包含赛站日期信息
- 特别鸣谢：[xcpcio](https://github.com/xcpcio/xcpcio)、[RankLand](https://rl.algoux.org/collection/official)

## 数据完整性

"""
    f.write(intro)
    f.write('\n'.join(markdown_lines))

# print("README.md generated successfully!")