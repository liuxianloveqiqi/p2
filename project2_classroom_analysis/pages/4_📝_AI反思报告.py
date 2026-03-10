"""
AI教学反思报告页面
"""
import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db_manager import (get_all_sessions, get_session_dialogues,
                               get_session_info, get_analysis_result,
                               save_reflection_report, get_reflection_report, init_db)
from utils.nlp_processor import compute_interaction_metrics
from utils.ai_service import get_client, generate_reflection_report, demo_generate_reflection_report

init_db()

st.set_page_config(page_title="AI反思报告", page_icon="📝", layout="wide")
st.title("📝 AI 教学反思报告")

st.markdown("""
综合课堂互动数据分析结果，利用**生成式AI**自动生成结构化的教学反思报告，
涵盖互动质量评估、教学亮点、改进建议和专业发展方向。
""")

# 选择课堂
sessions = get_all_sessions()
if sessions.empty:
    st.warning("⚠️ 暂无课堂记录，请先上传对话数据")
    st.stop()

session_options = {f"{row['session_name']} (ID:{row['id']})": row['id']
                   for _, row in sessions.iterrows()}
selected = st.selectbox("选择课堂", list(session_options.keys()))
session_id = session_options[selected]

# 获取数据
session_info = get_session_info(session_id)
dialogues_df = get_session_dialogues(session_id)

if dialogues_df.empty:
    st.warning("该课堂暂无对话数据")
    st.stop()

dialogues = [{'role': row['role'], 'content': row['content']} for _, row in dialogues_df.iterrows()]

# 课堂基本信息
st.subheader("📋 课堂基本信息")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("课堂名称", session_info.get('session_name', ''))
with col2:
    st.metric("学科", session_info.get('subject', ''))
with col3:
    st.metric("年级", session_info.get('grade', ''))
with col4:
    st.metric("总轮次", session_info.get('total_turns', 0))

# 计算互动指标
metrics = compute_interaction_metrics(dialogues)

st.subheader("📊 互动指标概览")
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("教师话语占比", f"{metrics['teacher_word_ratio']:.0%}")
with col2:
    st.metric("教师提问数", metrics['question_count'])
with col3:
    st.metric("IRE模式", f"{metrics['ire_count']}次")
with col4:
    st.metric("IRF模式", f"{metrics['irf_count']}次")
with col5:
    dominance = "偏高" if metrics['teacher_dominance'] > 0.7 else ("均衡" if metrics['teacher_dominance'] > 0.5 else "学生主导")
    st.metric("教师主导度", dominance)

# 查看已有报告
st.markdown("---")
existing_report = get_reflection_report(session_id)

if existing_report:
    st.subheader("📄 已生成的反思报告")
    st.markdown(existing_report['report_content'])
    st.caption(f"生成时间: {existing_report['created_at']}")

    if st.button("🔄 重新生成报告"):
        existing_report = None

# 生成新报告
if not existing_report:
    st.subheader("🤖 生成 AI 教学反思报告")

    demo_mode = st.session_state.get('demo_mode', True)
    api_key = st.session_state.get('api_key', '')

    bloom_results = get_analysis_result(session_id, 'bloom')
    themes = get_analysis_result(session_id, 'themes')

    if not bloom_results:
        st.info("💡 建议先在「互动分析」页面完成 Bloom 分类，可使反思报告更全面")
    if not themes:
        st.info("💡 建议先在「主题词云」页面完成 AI 主题提取，可使反思报告更全面")

    btn_label = "🎮 Demo: 生成教学反思报告" if demo_mode else "📝 生成教学反思报告"
    if st.button(btn_label, type="primary"):
        with st.spinner("AI 正在综合分析并撰写教学反思报告，请稍候..."):
            if demo_mode:
                report = demo_generate_reflection_report(
                    session_info=session_info,
                    interaction_metrics=metrics,
                    bloom_results=bloom_results,
                    themes=themes
                )
            elif api_key:
                client = get_client(api_key, st.session_state.get('base_url', ''))
                report = generate_reflection_report(
                    client=client,
                    model=st.session_state.get('model_name', 'gpt-3.5-turbo'),
                    session_info=session_info,
                    interaction_metrics=metrics,
                    bloom_results=bloom_results,
                    themes=themes
                )
            else:
                st.warning("⚠️ 请配置 API Key 或开启 Demo 模式")
                st.stop()

            save_reflection_report(session_id, report)
            st.markdown(report)
            st.success("✅ 教学反思报告已生成并保存！")

            # 下载报告
            st.download_button(
                "📥 下载报告 (Markdown)",
                report,
                f"reflection_report_{session_id}.md",
                "text/markdown"
            )
