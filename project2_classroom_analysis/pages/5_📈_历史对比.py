"""
历史对比看板 - 多课次互动指标趋势追踪
"""
import streamlit as st
import pandas as pd
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db_manager import get_all_sessions, get_all_analysis_for_comparison, init_db
from utils.chart_helper import create_comparison_line
from streamlit_echarts import st_pyecharts

init_db()

st.set_page_config(page_title="历史对比", page_icon="📈", layout="wide")
st.title("📈 历史对比看板")

st.markdown("""
对比多次课堂的互动指标变化趋势，帮助教师追踪自身教学改进历程，
体现**数据驱动的教师专业发展**理念。
""")

# 获取所有session
sessions = get_all_sessions()
if sessions.empty or len(sessions) < 1:
    st.warning("⚠️ 至少需要1条课堂记录才能查看分析。请先上传并分析课堂数据。")
    st.stop()

# 获取分析数据
all_analysis = get_all_analysis_for_comparison()

if all_analysis.empty:
    st.warning("⚠️ 暂无分析数据，请先在「互动分析」页面完成课堂分析")
    st.stop()

# 提取互动分析数据
interaction_data = all_analysis[all_analysis['analysis_type'] == 'interaction']

if interaction_data.empty:
    st.warning("⚠️ 暂无互动分析数据")
    st.stop()

# 解析数据
records = []
for _, row in interaction_data.iterrows():
    try:
        data = json.loads(row['result_data'])
        records.append({
            'session_name': row['session_name'],
            'created_at': row['created_at'],
            'teacher_turns': row['teacher_turns'],
            'student_turns': row['student_turns'],
            'teacher_word_ratio': data.get('talk_ratio', {}).get('teacher_word_ratio', 0),
            'student_word_ratio': data.get('talk_ratio', {}).get('student_word_ratio', 0),
            'question_count': data.get('question_count', 0),
            'ire_count': data.get('ire_count', 0),
            'irf_count': data.get('irf_count', 0),
        })
    except:
        continue

if not records:
    st.warning("无法解析分析数据")
    st.stop()

df = pd.DataFrame(records)

# ========== 概览表 ==========
st.subheader("📋 各课次互动指标总览")

display_df = df.copy()
display_df['教师话语占比'] = display_df['teacher_word_ratio'].apply(lambda x: f"{x:.0%}")
display_df['学生话语占比'] = display_df['student_word_ratio'].apply(lambda x: f"{x:.0%}")
display_df = display_df.rename(columns={
    'session_name': '课堂名称',
    'teacher_turns': '教师轮次',
    'student_turns': '学生轮次',
    'question_count': '提问数',
    'ire_count': 'IRE次数',
    'irf_count': 'IRF次数',
    'created_at': '时间',
})

st.dataframe(display_df[['课堂名称', '教师轮次', '学生轮次', '教师话语占比', '学生话语占比',
                           '提问数', 'IRE次数', 'IRF次数', '时间']],
             use_container_width=True, hide_index=True)

# ========== 趋势图 ==========
if len(df) >= 2:
    st.markdown("---")
    st.subheader("📊 互动指标趋势")

    session_names = df['session_name'].tolist()

    # 选择要对比的指标
    metric_options = {
        "教师话语占比(%)": [round(v * 100, 1) for v in df['teacher_word_ratio']],
        "学生话语占比(%)": [round(v * 100, 1) for v in df['student_word_ratio']],
        "教师提问数": df['question_count'].tolist(),
        "IRE模式次数": df['ire_count'].tolist(),
        "IRF模式次数": df['irf_count'].tolist(),
        "教师发言轮次": df['teacher_turns'].tolist(),
        "学生发言轮次": df['student_turns'].tolist(),
    }

    selected_metrics = st.multiselect(
        "选择要对比的指标",
        list(metric_options.keys()),
        default=["教师话语占比(%)", "教师提问数", "IRF模式次数"]
    )

    if selected_metrics:
        metrics_data = {k: metric_options[k] for k in selected_metrics}
        line_chart = create_comparison_line(session_names, metrics_data)
        st_pyecharts(line_chart, height="450px")

    # ========== 改进建议 ==========
    st.markdown("---")
    st.subheader("💡 趋势分析")

    if len(df) >= 2:
        latest = df.iloc[-1]
        previous = df.iloc[-2]

        changes = []
        # 教师话语占比变化
        tw_change = latest['teacher_word_ratio'] - previous['teacher_word_ratio']
        if tw_change > 0.05:
            changes.append(f"⚠️ 教师话语占比增加了 {tw_change:.0%}，建议关注学生发言机会")
        elif tw_change < -0.05:
            changes.append(f"✅ 教师话语占比减少了 {abs(tw_change):.0%}，学生参与度有所提升")

        # 提问数变化
        q_change = latest['question_count'] - previous['question_count']
        if q_change > 0:
            changes.append(f"✅ 教师提问数增加了 {q_change} 个，互动性增强")
        elif q_change < 0:
            changes.append(f"ℹ️ 教师提问数减少了 {abs(q_change)} 个")

        # IRF变化
        irf_change = latest['irf_count'] - previous['irf_count']
        if irf_change > 0:
            changes.append(f"✅ IRF模式增加了 {irf_change} 次，反馈质量提升")
        elif irf_change < 0:
            changes.append(f"⚠️ IRF模式减少了 {abs(irf_change)} 次，建议增加引导性反馈")

        if changes:
            st.markdown(f"**与上一课次「{previous['session_name']}」相比：**")
            for c in changes:
                st.markdown(f"  {c}")
        else:
            st.info("各项指标变化不大")

else:
    st.info("💡 至少需要2个课堂的分析数据才能展示趋势图。请继续上传和分析更多课堂。")

# ========== 综合评估 ==========
st.markdown("---")
st.subheader("🎯 综合评估")

avg_teacher_ratio = df['teacher_word_ratio'].mean()
avg_questions = df['question_count'].mean()
avg_irf = df['irf_count'].mean()

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("平均教师话语占比", f"{avg_teacher_ratio:.0%}",
              delta="偏高" if avg_teacher_ratio > 0.65 else "合理")
with col2:
    st.metric("平均提问数", f"{avg_questions:.1f}")
with col3:
    st.metric("平均IRF次数", f"{avg_irf:.1f}")

st.markdown("""
> 📖 **参考标准**（基于课堂互动研究文献）：
> - 教师话语占比建议控制在 40%-60%
> - 高阶思维提问应占总提问的 30% 以上
> - IRF模式（含反馈引导）占比越高，课堂对话质量越好
""")
