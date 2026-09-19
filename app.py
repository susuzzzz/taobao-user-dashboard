# -*- coding: utf-8 -*-
import json
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

st.set_page_config(page_title="电商用户行为分析看板", layout="wide")
st.title("电商用户行为数据分析看板")
st.caption("数据：淘宝公开用户行为数据集 | 296万条 | 2026-09 郭素素")

data = json.load(open('dashboard_data.json', encoding='utf-8'))
s = data['summary']

# 顶部指标卡
c1, c2, c3, c4 = st.columns(4)
c1.metric("购买用户数", f"{s['购买用户']:,}")
c2.metric("复购率", f"{s['复购率']}%")
c3.metric("次日留存率", f"{s['次日留存']}%")
c4.metric("高频多品类用户", f"{data['seg_counts'].get('高频多品类用户',0):,}")

# 漏斗图
# 漏斗图（部署版：图表用英文标签，防止云端字体缺字）
st.subheader("行为漏斗")
f = s['漏斗']
fig, ax = plt.subplots(figsize=(6, 3.5))
ax.bar(['View', 'Fav/Cart', 'Buy'], f.values(), color=['#4C9F70', '#E8A33D', '#C0504D'])
ax.set_ylabel("Users")
st.pyplot(fig)

col_l, col_r = st.columns(2)

# 留存表
with col_l:
    st.subheader("Cohort 留存表（按首次活跃日期）")
    cohort = pd.read_csv('cohort_table.csv', index_col=0)
    st.dataframe(cohort)

# 用户分层
with col_r:
    st.subheader("用户分层")
    seg = pd.DataFrame({
        '人数': pd.Series(data['seg_counts']),
        '平均购买次数': pd.Series({k: v['F'] for k, v in data['seg_stats'].items()}),
        '平均品类宽度': pd.Series({k: v['M_proxy'] for k, v in data['seg_stats'].items()}),
    })
    st.dataframe(seg)

# 分层名单查询
st.subheader("分层用户明细查询")
uf = pd.read_csv('user_segments_real.csv')
choice = st.selectbox("选择用户类型", sorted(uf['分层'].unique()))
st.dataframe(uf[uf['分层'] == choice].head(50))
st.caption("显示前50条，完整名单见 user_segments_real.csv")

st.subheader("核心结论")
st.markdown("""
- **数据质量**：清洗前留存率仅20.3%，剔除越界时间戳后修正为77.3%------数据治理直接决定业务结论
- **转化**：87%浏览用户产生意向，意向到购买转化78.9%
- **粘性**：复购率54.8%，次日留存77.3%，用户粘性良好
- **建议**：对"低频沉睡用户"做定向召回；对"高频多品类用户"做新品优先推送
""")