import math
import re
import os
from opencc import OpenCC

def calcSeed(ratingToCounts, rating, prev=None):
    if prev == None:
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
        return {}  # 返回空字典而非列表，与函数设计更一致
    
    userList = list(userRank.keys())
    ratingToCounts = {}
    
    for user in userList:
        if user not in currentRatings:
            currentRatings[user] = 1400
        rating = currentRatings[user]
        if rating not in ratingToCounts:
            ratingToCounts[rating] = 0
        ratingToCounts[rating] += 1

    # 第一次计算 Delta 时，按什么顺序遍历都可以
    delta = {}
    inc_sum = 0
    for user in userList:
        rank = userRank[user]
        rating = currentRatings[user]
        M = math.sqrt(calcSeed(ratingToCounts, rating) * rank)
        l = 1
        r = 8000
        while l < r - 1:
            m = int((l + r) / 2.0)
            if calcSeed(ratingToCounts, m, rating) < M:
                r = m
            else:
                l = m
        delta[user] = int((l - rating) / 2.0)
        inc_sum += delta[user]

    # 第一次调整：确保总和为负
    # 为了更精确地模拟 Java 的整数除法，可以使用 // 
    inc = -(inc_sum // userCount) - 1
    for user in delta:
        delta[user] += inc

    # 第二次调整前，必须按 Rating 从高到低排序
    # 这是关键的修正点
    userList = sorted(userList, key=lambda x: currentRatings[x], reverse=True)
    
    s = int(min(userCount, 4 * round(math.sqrt(userCount))))
    sum_top = 0
    for i in range(s):
        # 现在 userList[i] 是 Rating 最高的选手
        sum_top += delta[userList[i]]
    
    # 为了更精确地模拟 Java 的整数除法，可以使用 //
    inc = min(max(-1 * (sum_top // s), -10), 0)
    
    returnValue = {}
    for user in userList:
        # delta[user] += inc
        rating = currentRatings[user]
        # Java 源码没有 floor，而是直接整数加减，这里保持 int 转换即可
        new_rating = rating + delta[user]
        returnValue[user] = new_rating
        
    return returnValue

def normalize(s, t2s=False):
    s = str(s)
    s = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', s)
    s = s.lower()
    if t2s == True or '港' in s or '澳' in s:
        s = OpenCC('t2s').convert(s)
    return s

def rating_color(rating):
    if not rating:
        return 'color:#000000;'
    if rating<1200:
        return 'color:#808080;'
    elif rating<1400:
        return 'color:#008000;'
    elif rating<1600:
        return 'color:#03A89E;'
    elif rating<1900:
        return 'color:#0000FF;'
    elif rating<2100:
        return 'color:#AA00AA;'
    elif rating<2400:
        return 'color:#FFC000;'
    elif rating<3000:
        return 'color:#FF0000;'
    else:
        return 'color:#FF0000;'
