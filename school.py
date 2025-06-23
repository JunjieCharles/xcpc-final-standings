import pandas as pd
import os
import re
from opencc import OpenCC

def normalize(s):
    s = str(s)
    s = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9]', '', s)
    s = s.lower()
    if '港' in s or '澳' in s:
        s = OpenCC('t2s').convert(s)
    return s

df = pd.read_csv('school.csv')
zh_en = {}
en_zh = {}
for i, row in df.iterrows():
    if row.isnull().all():
        continue
    chn = normalize(row['zh'])
    eng = normalize(row['en'])
    alts = row["alt"].split(',') if pd.notna(row["alt"]) else []
    alts = [normalize(alt.strip()) for alt in alts if alt.strip()]
    zh_en[chn] = eng
    en_zh[eng] = chn
    for alt in alts:
        if alt.encode('utf-8').isalpha():
            en_zh[alt] = chn
        else:
            zh_en[alt] = eng

notfound = {}

for file in os.listdir('./csv'):
    if file.endswith('.csv'):
        df = pd.read_csv(os.path.join('./csv', file))
        if 'School' in df.columns:
            for i, row in df.iterrows():
                if row.isnull().all():
                    continue
                school = normalize(row['School'])
                if school not in zh_en and school not in en_zh:
                    notfound[school] = notfound.get(school, []) + [(file, i)]

for school in sorted(notfound):
    print(f"{school}: {', '.join([f'{f}({i})' for f, i in notfound[school]])}")