"""
知识诊断可视化页面
"""
import streamlit as st
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db_manager import get_grading_results, init_db
from utils.data_processor import compute_student_knowledge_mastery
from utils.chart_helper import create_radar_chart, create_heatmap
from streamlit_echarts import st_pyecharts

init_db()

st.set_page_config(page_title="知识诊断", page_icon="📊", layout="wide")
st.title("📊 知识诊断可视化")

st.markdown("""
基于AI批阅结果，通过**雷达图**和**热力图**直观展示学生的知识点掌握情况，帮助教师精准定位薄弱环节。
""")

# 获取批阅结果
grading_df = get_grading_results()

if grading_df.empty:
    st.warning("⚠️ 暂无批阅数据，请先完成 AI 批阅")
    st.stop()

# 计算知识掌握度
mastery_df = compute_student_knowledge_mastery(grading_df)

# ========== 个人诊断 - 雷达图 ==========
st.subheader("🎯 个人知识诊断 - 雷达图")

students = mastery_df['student_name'].unique().tolist()
selected_student = st.selectbox("选择学生", students)

if selected_student:
    student_mastery = mastery_df[mastery_df['student_name'] == selected_student]
    knowledge_scores = dict(zip(student_mastery['knowledge_point'], student_mastery['score_rate']))

    if knowledge_scores:
        radar = create_radar_chart(selected_student, knowledge_scores)
        st_pyecharts(radar, height="500px")

        # 详细数据表
        st.markdown("**📋 详细数据：**")
        detail_df = student_mastery[['knowledge_point', 'score_rate', 'error_types']].copy()
        detail_df.columns = ['知识点', '得分率', '主要错误类型']
        detail_df['得分率'] = detail_df['得分率'].apply(lambda x: f"{x:.0%}")
        st.dataframe(detail_df, use_container_width=True, hide_index=True)

        # 薄弱知识点提醒
        weak = student_mastery[student_mastery['score_rate'] < 0.6]
        if not weak.empty:
            st.error(f"⚠️ {selected_student} 有 {len(weak)} 个薄弱知识点（得分率<60%）需要重点关注：")
            for _, row in weak.iterrows():
                st.markdown(f"  - **{row['knowledge_point']}**：得分率 {row['score_rate']:.0%}，问题类型：{row['error_types']}")
    else:
        st.info("该学生暂无诊断数据")

# ========== 班级诊断 - 热力图 ==========
st.markdown("---")
st.subheader("🔥 班级知识点掌握热力图")

if not mastery_df.empty:
    heatmap = create_heatmap(mastery_df)
    st_pyecharts(heatmap, height="500px")

    st.markdown("""
    > 📖 **图表说明**：颜色越绿代表掌握越好，越红代表越薄弱。
    > 教师可以根据热力图快速发现全班的共同薄弱环节，进行有针对性的复习教学。
    """)

# ========== 对比分析 ==========
st.markdown("---")
st.subheader("📊 学生对比分析")

compare_students = st.multiselect("选择要对比的学生", students, default=students[:min(3, len(students))])

if compare_students:
    compare_data = mastery_df[mastery_df['student_name'].isin(compare_students)]
    pivot = compare_data.pivot_table(
        values='score_rate', index='knowledge_point',
        columns='student_name', aggfunc='mean'
    ).fillna(0)

    # 展示对比表格
    display_pivot = pivot.copy()
    for col in display_pivot.columns:
        display_pivot[col] = display_pivot[col].apply(lambda x: f"{x:.0%}")
    st.dataframe(display_pivot, use_container_width=True)
