# -*- coding: utf-8 -*-
import pandas as pd
import json

FILE = r'UserBehavior.csv'

df = pd.read_csv(FILE, header=None,
                 names=['user_id','item_id','category_id','behavior','timestamp'],
                 nrows=3_000_000, on_bad_lines='skip')
df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.date
df = df[(df['date'] >= pd.to_datetime('2017-11-25').date()) &
        (df['date'] <= pd.to_datetime('2017-12-03').date())]

users_pv   = set(df[df['behavior']=='pv']['user_id'])
users_fav  = set(df[df['behavior']=='fav']['user_id'])
users_cart = set(df[df['behavior']=='cart']['user_id'])
users_buy  = set(df[df['behavior']=='buy']['user_id'])

buy = df[df['behavior']=='buy']
rep = buy.groupby('user_id')['date'].nunique()

first_seen = df.groupby('user_id')['date'].min().rename('first_date')
d2 = df.merge(first_seen, on='user_id')
d2['gap'] = (pd.to_datetime(d2['date']) - pd.to_datetime(d2['first_date'])).dt.days
cohort = d2.groupby(['first_date','gap'])['user_id'].nunique().unstack(fill_value=0)

uf = pd.read_csv('user_segments_real.csv')   # 第3步已生成的分层名单

summary = {
    '漏斗': {'浏览': len(users_pv), '收藏加购': len(users_fav | users_cart), '购买': len(users_buy)},
    '复购率': round(float((rep >= 2).mean() * 100), 1),
    '次日留存': round(float((cohort[1] / cohort[0]).mean() * 100), 1),
    '购买用户': int(len(users_buy)),
}
seg_counts = uf['分层'].value_counts().to_dict()
seg_stats = uf.groupby('分层')[['F','M_proxy','R']].mean().round(1).to_dict('index')

json.dump({'summary': summary, 'seg_counts': seg_counts, 'seg_stats': seg_stats},
          open('dashboard_data.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
cohort.to_csv('cohort_table.csv', encoding='utf-8-sig')
print("已保存: dashboard_data.json, cohort_table.csv")
print(summary)