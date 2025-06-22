import pandas as pd
from bs4 import BeautifulSoup
import re
from urllib.request import urlopen
import sys

def standings_html_to_csv(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table', class_='standings')
    
    # 确定题目列数量
    header_ths = table.find('tr').find_all('th')[2:-3]  # 跳过Rank、Username，最后三个是Solved/Penalty/Dirt
    problem_ids = [th.get_text().strip().split('\n')[0] for th in header_ths]
    problem_ids = [s[0] for s in problem_ids]  # 取每个题目的第一个字符作为ID
    
    data = []
    
    # 处理每一行数据
    for row in table.find_all('tr')[1:]:
        tds = row.find_all('td')
        if not tds:
            continue
            
        rank = tds[0].get_text().strip()
        if not rank.isdigit():
            continue
        username = tds[1].get_text().strip()
        solved = tds[-3].get_text().strip()
        penalty = tds[-2].get_text().strip()
        
        problems_data = []
        # 处理每个题目单元格
        for td in tds[2:2+len(problem_ids)]:
            center = td.find('center')
            if not center:
                problems_data.append('')
                continue
                
            # 获取提交状态文本
            status_text = center.contents[0].strip() if center.contents else ''
            time_font = center.find('font')
            time_str = time_font.get_text().strip() if time_font else ''
            
            # 处理不同类型的状态
            if status_text.startswith('+'):
                # 计算提交次数
                attempts_match = re.search(r'\d+', status_text)
                attempts = int(attempts_match.group(0)) + 1 if attempts_match else 1
                
                # 转换时间到分钟
                time_minutes = 0
                if ':' in time_str:
                    h, m = map(int, time_str.split(':'))
                    time_minutes = h * 60 + m
                
                problems_data.append(f"+{attempts}({time_minutes})")
                
            elif status_text.startswith('-'):
                problems_data.append(status_text)
                
            else:  # 空单元格处理
                problems_data.append('')
        
        row_data = [rank, username, solved, penalty] + problems_data
        data.append(row_data)
    
    # 创建DataFrame
    columns = ['Rank', 'Username', 'Solved', 'Penalty'] + problem_ids
    df = pd.DataFrame(data, columns=columns)
    return df

# 示例使用
if __name__ == "__main__":
    file = sys.argv[1]
    name = file.split('/')[-1].split('.')[0]
    with open(file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    df = standings_html_to_csv(html_content)
    df.to_csv(f"{name}.csv", index=False, encoding='utf-8-sig')