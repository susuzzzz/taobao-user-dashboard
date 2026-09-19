# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

FILE = r'UserBehavior.csv'   # ← 改成你的路径

df = pd.read_csv(FILE, header=None,
                 names=['user_id','item_id','category_id','behavior','timestamp'],
                 nrows=3_000_000, on_bad_lines='skip')
df['dt'] = pd.to_datetime(df['timestamp'], unit='s')
df['date'] = df['dt'].dt.date
df = df[(df['date'] >= pd.to_datetime('2017-11-25').date()) &
        (df['date'] <= pd.to_datetime('2017-12-03').date())]
print("清洗后规模:", df.shape)
print("规模:", df.shape, "| 日期:", df['date'].min(), "→", df['date'].max())

# 1. 复购率
buy = df[df['behavior']=='buy']
rep = buy.groupby('user_id')['date'].nunique()
rep_rate = (rep >= 2).mean()
print(f"购买用户数: {len(rep)}，复购率: {rep_rate:.1%}")

# 2. 留存分析
first_seen = df.groupby('user_id')['date'].min().rename('first_date')
d2 = df.merge(first_seen, on='user_id')
d2['day_gap'] = (pd.to_datetime(d2['date']) - pd.to_datetime(d2['first_date'])).dt.days
cohort = d2.groupby(['first_date','day_gap'])['user_id'].nunique().unstack(fill_value=0)
ret_d1 = (cohort[1] / cohort[0]).mean()
ret_d3 = (cohort[3] / cohort[0]).mean()
print(f"次日留存率: {ret_d1:.1%}   第4日留存率: {ret_d3:.1%}")
print(cohort)

# 3. 用户分层（无金额字段，用品类宽度代替M）
end_date = df['date'].max()
uf = buy.groupby('user_id').agg(
    F=('item_id','count'), last_buy=('date','max'),
    M_proxy=('category_id','nunique')).reset_index()
uf['R'] = (pd.to_datetime(end_date) - pd.to_datetime(uf['last_buy'])).dt.days

def seg(row):
    if row.F >= 3 and row.M_proxy >= 2: return '高频多品类用户'
    if row.F >= 2: return '稳定复购用户'
    if row.R <= 1: return '新购买用户'
    return '低频沉睡用户'
uf['分层'] = uf.apply(seg, axis=1)
print(uf['分层'].value_counts())
uf.to_csv('user_segments_real.csv', index=False, encoding='utf-8-sig')

plt.figure(figsize=(5,4))
plt.bar(['仅购买1次','购买2次及以上'], [1-rep_rate, rep_rate], color=['#9BB7D4','#2E75B6'])
plt.title(f'用户复购率（{rep_rate:.1%}）')
plt.ylabel('占比'); plt.tight_layout(); plt.savefig('repurchase.png', dpi=150)
print("已保存: user_segments_real.csv, repurchase.png")