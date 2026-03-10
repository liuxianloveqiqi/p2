"""
班级分析看板页面
"""
import streamlit as st
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db_manager import get_grading_results, init_db
from utils.data_processor import compute_student_knowledge_mastery, compute_class_stats
from utils.chart_helper import create_score_distribution, create_error_type_pie, create_knowledge_bar
from utils.ai_service import get_client, generate_class_summary, demo_generate_class_summary
from streamlit_echarts import st_pyecharts

init_db()

st.set_page_config(page_title="班级看板", page_icon="🏫", layout="wide")
st.title("🏫 班级分析看板")

st.markdown("整合班级维度的学情数据，为教师提供全局视角的教学决策支持。")

# 获取数据
grading_df = get_grading_results()

if grading_df.empty:
    st.warning("⚠️ 暂无批阅数据，请先完成 AI 批阅")
    st.stop()

# 计算统计数据
stats = compute_class_stats(grading_df)

# ========== 核心指标 ==========
st.subheader("📈 核心指标")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("👥 学生总数", stats['total_students'])
with col2:
    st.metric("📊 平均得分率", f"{stats['avg_score']:.0%}")
with col3:
    st.metric("🏆 最高得分率", f"{stats['max_score']:.0%}")
with col4:
    st.metric("📉 最低得分率", f"{stats['min_score']:.0%}")

# ========== 成绩分布 ==========
st.markdown("---")
st.subheader("📊 成绩分布")

score_rates = stats['student_scores']['score_rate'].tolist()
score_bar = create_score_distribution(score_rates)
st_pyecharts(score_bar, height="400px")

# ========== 知识点达标率 ==========
st.markdown("---")
st.subheader("📐 各知识点达标率")

knowledge_mastery = stats['knowledge_mastery']
kp_bar = create_knowledge_bar(knowledge_mastery)
st_pyecharts(kp_bar, height="400px")

# 进度条形式展示
st.markdown("**详细达标情况：**")
for kp, rate in sorted(knowledge_mastery.items(), key=lambda x: x[1]):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.progress(min(rate, 1.0))
    with col2:
        status = "✅" if rate >= 0.8 else ("⚠️" if rate >= 0.6 else "❌")
        st.write(f"{status} {kp}: {rate:.0%}")

# ========== 错误类型分析 ==========
st.markdown("---")
st.subheader("🔍 高频错误类型分析")

error_types = stats['error_types']
if error_types:
    col1, col2 = st.columns([2, 1])
    with col1:
        error_pie = create_error_type_pie(error_types)
        st_pyecharts(error_pie, height="400px")
    with col2:
        st.markdown("**错误类型统计：**")
        for err_type, count in sorted(error_types.items(), key=lambda x: -x[1]):
            st.markdown(f"- **{err_type}**：{count} 次")

# ========== 学生排名 ==========
st.markdown("---")
st.subheader("🏅 学生得分排名")

student_scores = stats['student_scores'].copy()
student_scores['score_rate_display'] = student_scores['score_rate'].apply(lambda x: f"{x:.0%}")
student_scores = student_scores.sort_values('score_rate', ascending=False).reset_index(drop=True)
student_scores.index += 1
student_scores.index.name = '排名'

display_df = student_scores[['student_name', 'total_score', 'total_full', 'score_rate_display']].copy()
display_df.columns = ['学生姓名', '总得分', '总满分', '得分率']
st.dataframe(display_df, use_container_width=True)

# ========== AI 班级分析 ==========
st.markdown("---")
st.subheader("🤖 AI 班级分析总结")

demo_mode = st.session_state.get('demo_mode', True)
api_key = st.session_state.get('api_key', '')
base_url = st.session_state.get('base_url', 'https://api.openai.com/v1')
model_name = st.session_state.get('model_name', 'gpt-3.5-turbo')

if st.button("📝 生成AI班级分析报告", type="primary"):
    with st.spinner("AI 正在分析班级数据..."):
        stats_for_ai = {
            'total_students': stats['total_students'],
            'avg_score': stats['avg_score'],
            'max_score': stats['max_score'],
            'min_score': stats['min_score'],
            'knowledge_mastery': {k: round(v, 2) for k, v in knowledge_mastery.items()},
            'error_types': error_types
        }
        if demo_mode:
            summary = demo_generate_class_summary(stats_for_ai)
        elif api_key:
            client = get_client(api_key, base_url)
            summary = generate_class_summary(
                client=client,
                model=model_name,
                class_stats=stats_for_ai
            )
        else:
            summary = "⚠️ 请配置 API Key 或开启 Demo 模式"
        st.markdown(summary)
