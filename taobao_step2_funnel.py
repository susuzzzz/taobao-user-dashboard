# -*- coding: utf-8 -*-
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

FILE = r'UserBehavior.csv'   # ← 改成你CSV的实际路径

df = pd.read_csv(FILE, header=None,
                 names=['user_id','item_id','category_id','behavior','timestamp'],
                 nrows=1_000_000,          # 先取前100万行
                 on_bad_lines='skip')      # 跳过不完整行
print("数据规模:", df.shape)
print(df.head(3))

df['date'] = pd.to_datetime(df['timestamp'], unit='s').dt.date
print("日期范围:", df['date'].min(), "→", df['date'].max())
print(df['behavior'].value_counts())

dau = df[df['behavior']=='pv'].groupby('date')['user_id'].nunique()
plt.figure(figsize=(9,4))
plt.plot(range(len(dau)), dau.values)
plt.title('每日浏览用户数（DAU）')
plt.xlabel('日期序号'); plt.ylabel('用户数')
plt.tight_layout(); plt.savefig('dau_trend.png', dpi=150)

users_pv   = set(df[df['behavior']=='pv']['user_id'])
users_fav  = set(df[df['behavior']=='fav']['user_id'])
users_cart = set(df[df['behavior']=='cart']['user_id'])
users_buy  = set(df[df['behavior']=='buy']['user_id'])

n_pv   = len(users_pv)
n_favc = len(users_fav | users_cart)
n_buy  = len(users_buy)

print(f"漏斗：浏览 {n_pv} → 有意向 {n_favc}（{n_favc/n_pv:.1%}）→ 购买 {n_buy}（{n_buy/n_pv:.1%}）")
print(f"有意向→购买转化：{n_buy/n_favc:.1%}")

plt.figure(figsize=(6,4))
labels = [f'浏览\n{n_pv}', f'收藏/加购\n{n_favc}', f'购买\n{n_buy}']
plt.bar(labels, [n_pv, n_favc, n_buy], color=['#4C9F70','#E8A33D','#C0504D'])
plt.title('用户行为漏斗')
plt.tight_layout(); plt.savefig('funnel.png', dpi=150)
print("图片已保存: dau_trend.png, funnel.png")