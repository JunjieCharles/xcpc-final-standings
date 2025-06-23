import pandas as pd
import math
import re
from opencc import OpenCC
import os
from tqdm import tqdm

def normalize(s):
    s = str(s)
    s = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', s)
    s = s.lower()
    if '港' in s or '澳' in s:
        s = OpenCC('t2s').convert(s)
    return s

df = pd.read_csv('school.csv')
alt_zh = {}
for i, row in df.iterrows():
    if row.isnull().all():
        continue
    zh = normalize(row['zh'])
    en = normalize(row['en'])
    alts = row["alt"].split(',') if pd.notna(row["alt"]) else []
    alts = [normalize(alt.strip()) for alt in alts if alt.strip()]
    alt_zh[en] = zh
    for alt in alts:
        alt_zh[alt] = zh

def getSchool(s):
    s = normalize(s)
    if s in alt_zh:
        s = alt_zh[s]
    return s

def calcSeed(ratingToCounts, rating, prev=None):
    if prev==None:
        prev = rating
    seed = 1
    for t in ratingToCounts:
        seed += ratingToCounts[t] * (1.0 / (1 + math.pow(10, (rating - t) / 400)))
    seed -= 1.0 / (1 + math.pow(10, (rating - prev) / 400))
    return seed

def calculateRating(userRank, currentRatings):
    '''
    userRank: dict {user:rank}
    currentRatings: dict {user:rating}
    '''
    userCount = len(userRank)
    if userCount == 0:
        return []
    userList = list(userRank.keys())
    ratingToCounts = {}
    for user in userList:
        if user not in currentRatings:
            currentRatings[user] = 1400
        rating = currentRatings[user]
        if rating not in ratingToCounts:
            ratingToCounts[rating] = 0
        ratingToCounts[rating] += 1
    userList = sorted(userList, key=lambda x: currentRatings[x])
    inc = 0
    delta = {}
    for user in userList:
        rank = userRank[user]
        rating = currentRatings[user]
        M = math.sqrt(calcSeed(ratingToCounts, rating) * rank)
        l = 1
        r = 8000
        while l<r-1:
            m = int((l+r)/2.0)
            if calcSeed(ratingToCounts, m, rating) < M:
                r = m
            else:
                l = m
        delta[user] = int((l-rating)/2.0)
        inc += delta[user]
    inc = -(inc/userCount)-1
    for user in delta:
        delta[user] += inc
    s = math.floor(min(userCount, 4 * math.sqrt(userCount)))
    sum = 0
    for i in range(s):
        sum += delta[userList[i]]
    inc = min(max(-1 * int(sum/s), -10), 0)
    returnValue = {}
    for user in userList:
        delta[user] += inc
        rating = currentRatings[user]
        new_rating = math.floor(rating + delta[user])
        returnValue[user] = new_rating
    return returnValue
    

if __name__ == "__main__":
    df = pd.read_csv('date.csv')
    df['date'] = pd.to_datetime(df['date'], format='%Y/%m/%d')
    df['type'] = df['contest'].apply(lambda x: 'ICPC' if 'ICPC' in x else 'CCPC')
    df['priority'] = df['type'].map({'CCPC': 0, 'ICPC': 1})
    sorted_df = df.sort_values(by=['date', 'priority'], ascending=[True, True])
    sorted_contests = sorted_df['contest'].tolist()
    
    # 初始化数据结构
    current_ratings = {}  # 当前所有学校的rating
    valid_contests = []    # 有效的比赛名称列表
    valid_contests_ratings = []  # 每场有效比赛后的rating状态
    
    # 遍历每一场比赛
    for contest in tqdm(sorted_contests):
        path = f'./csv/{contest}.csv'
        if not os.path.exists(path):
            continue
            
        df = pd.read_csv(path)
        if 'School' not in df.columns:
            continue
            
        # 处理数据
        df = df.dropna(how='all')
        df = df[['School', 'Solved', 'Penalty']]
        df['School'] = df['School'].apply(getSchool)
        # df = df[df['School'] != '']  # 移除非法的空学校名称
        df['Score'] = df['Solved'] * 1000000 - df['Penalty']
        df = df.sort_values(by='Score', ascending=False)
        df = df.drop_duplicates(subset='School', keep='first')
        df['School Rank'] = df['Score'].rank(method='min', ascending=False).astype(int)
        
        # 创建排名字典
        userRank = dict(zip(df['School'], df['School Rank']))
        
        # 确保所有参赛学校都有初始Rating
        for school in userRank.keys():
            if school not in current_ratings:
                current_ratings[school] = 1400  # 初始Rating
        
        # 计算新的rating
        new_ratings = calculateRating(userRank, current_ratings.copy())
        
        # 更新当前rating
        current_ratings.update(new_ratings)
        
        # 记录有效比赛和比赛后的rating状态
        valid_contests.append(contest)
        valid_contests_ratings.append(current_ratings.copy())
    
    # 收集所有出现过学校
    all_schools = set()
    for ratings in valid_contests_ratings:
        all_schools.update(ratings.keys())
    all_schools = sorted(list(all_schools))
    
    # 构建结果表（修改部分：首次参赛前显示1400）
    result_data = []
    for school in all_schools:
        row = [school]
        # 遍历每场比赛
        for ratings in valid_contests_ratings:
            if school in ratings:
                row.append(float(ratings[school]))
            else:
                row.append(1400.0)  # 首次参赛前显示1400
        result_data.append(row)
    
    # 创建最终DataFrame并保存
    result_df = pd.DataFrame(result_data, columns=['School'] + valid_contests)
    result_df.to_csv('rating/rating_school.csv', index=False, encoding='utf-8-sig')
    print(f"成功保存学校Rating数据到 rating_school.csv (包含{len(valid_contests)}场有效比赛)")