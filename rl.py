import pandas as pd
import re
import sys

if __name__ == '__main__':
    name = sys.argv[1]
    df = pd.read_excel(f'{name}.xlsx', sheet_name='Official')

    # 清理列名：去除括号及其内容
    new_columns = []
    for col in df.columns:
        if '(' in col:
            new_columns.append(col.split('(')[0].strip())
        else:
            new_columns.append(col)
    df.columns = new_columns

    # 处理Rank和Medal列
    def split_rank_medal(value):
        if pd.isna(value):
            return None, ""
        value_str = str(value)
        if '(' in value_str:
            rank_part, medal_part = value_str.split('(', 1)
            rank = rank_part.strip()
            medal = medal_part.replace(')', '').strip()
        else:
            rank = value_str.strip()
            medal = ""
        return rank, medal

    rank_medal = df['#'].apply(split_rank_medal)
    df['Rank'] = [rm[0] for rm in rank_medal]
    df['Medal'] = [rm[1] for rm in rank_medal]

    # 重命名列
    df.rename(columns={
        'Organization': 'School',
        'Name': 'Team',
        'Score': 'Solved'
    }, inplace=True)

    # 使用Time列计算Penalty（新方法）
    def convert_time_to_minutes(time_str):
        if pd.isna(time_str) or time_str == '':
            return 0
        parts = str(time_str).split(':')
        if len(parts) < 2:
            return 0
        try:
            hours = int(parts[0])
            minutes = int(parts[1])
            return hours * 60 + minutes
        except:
            return 0

    df['Penalty'] = df['Time'].apply(convert_time_to_minutes)

    # 删除不需要的列
    columns_to_drop = ['#', 'R#', 'S#', 'Markers', 'Official', 'Time']
    for col in columns_to_drop:
        if col in df.columns:
            df.drop(col, axis=1, inplace=True)

    # 初始化罚时列（原始方法，已注释）
    # df['Penalty'] = 0

    # 识别题目列（A到M）
    problem_cols = [col for col in df.columns if len(col) == 1 and 'A' <= col <= 'M']

    # 处理每个题目列
    for col in problem_cols:
        for idx in df.index:
            val = df.at[idx, col]
            if pd.isna(val) or val == '':
                continue  # 保持空值不变
                
            # 处理RJ格式
            if val.startswith('RJ'):
                parts = val.split('/')
                if len(parts) >= 2:
                    attempts = parts[1]
                    df.at[idx, col] = f'-{attempts}'
                    
            # 处理AC/FB格式
            elif any(val.startswith(prefix) for prefix in ['AC/', 'FB/']):
                parts = val.split('/')
                if len(parts) >= 3:
                    attempts = parts[1]
                    time_part = parts[2]
                    
                    # 解析时间
                    time_parts = time_part.split(':')
                    if len(time_parts) >= 2:
                        hours = int(time_parts[0])
                        minutes = int(time_parts[1])
                        total_minutes = hours * 60 + minutes
                        
                        # 计算罚时贡献（原始方法，已注释）
                        # penalty_contrib = total_minutes + (int(attempts) - 1) * 20
                        # df.at[idx, 'Penalty'] += penalty_contrib
                        
                        # 更新单元格值
                        df.at[idx, col] = f'+{attempts}({total_minutes})'

    # 确定列顺序
    final_columns = ['Rank', 'Medal', 'School', 'Team', 'Solved', 'Penalty'] + problem_cols
    df = df[final_columns]

    # 保存为CSV文件
    df.to_csv(f'{name}.csv', index=False, encoding='utf-8-sig')