"""
互动分析页面 - 师生话语比例、Bloom提问分类、IRE/IRF模式
"""
import streamlit as st
import pandas as pd
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db_manager import (get_all_sessions, get_session_dialogues,
                               get_session_info, save_analysis_result,
                               get_analysis_result, init_db)
from utils.nlp_processor import (
    compute_talk_ratio,
    extract_teacher_questions,
    analyze_ire_patterns,
    count_interaction_pattern_types,
    normalize_pattern_type,
)
from utils.chart_helper import create_talk_ratio_pie, create_bloom_bar, create_ire_bar
from utils.ai_service import get_client, classify_bloom_questions, demo_classify_bloom_questions
from streamlit_echarts import st_pyecharts

init_db()

st.set_page_config(page_title="互动分析", page_icon="💬", layout="wide")
st.title("💬 课堂互动模式分析")

st.markdown("""
从**师生话语比例**、**Bloom认知提问层次**、**IRE/IRF互动模式**三个维度分析课堂互动质量。
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

# 获取对话数据
dialogues_df = get_session_dialogues(session_id)
session_info = get_session_info(session_id)

if dialogues_df.empty:
    st.warning("该课堂暂无对话数据")
    st.stop()

dialogues = [{'role': row['role'], 'content': row['content']} for _, row in dialogues_df.iterrows()]

# ========== 1. 师生话语比例 ==========
st.subheader("📊 1. 师生话语比例分析")

talk_ratio = compute_talk_ratio(dialogues)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("教师发言轮次", talk_ratio['teacher_turns'])
with col2:
    st.metric("学生发言轮次", talk_ratio['student_turns'])
with col3:
    st.metric("教师平均发言长度", f"{talk_ratio['avg_teacher_length']:.0f}字")
with col4:
    st.metric("学生平均发言长度", f"{talk_ratio['avg_student_length']:.0f}字")

col1, col2 = st.columns(2)
with col1:
    pie1 = create_talk_ratio_pie(talk_ratio['teacher_word_ratio'],
                                  talk_ratio['student_word_ratio'], "字数")
    st_pyecharts(pie1, height="400px")
with col2:
    pie2 = create_talk_ratio_pie(talk_ratio['teacher_turn_ratio'],
                                  talk_ratio['student_turn_ratio'], "轮次")
    st_pyecharts(pie2, height="400px")

# 教师主导度评估
dominance = talk_ratio['teacher_word_ratio']
if dominance > 0.7:
    st.warning(f"⚠️ 教师话语占比 {dominance:.0%}，教师主导度偏高。建议增加学生表达机会。")
elif dominance > 0.5:
    st.info(f"ℹ️ 教师话语占比 {dominance:.0%}，师生互动相对均衡。")
else:
    st.success(f"✅ 教师话语占比 {dominance:.0%}，学生参与度较高。")

# ========== 2. Bloom 提问层次 ==========
st.markdown("---")
st.subheader("🧠 2. Bloom 认知目标提问分析")

st.markdown("""
> **Bloom认知目标分类学**将认知过程分为6个层次：
> 记忆 → 理解 → 应用 → 分析 → 评价 → 创造（从低阶到高阶思维）
""")

questions = extract_teacher_questions(dialogues)

if questions:
    st.markdown(f"**共提取到 {len(questions)} 个教师提问：**")
    for i, q in enumerate(questions):
        st.markdown(f"  {i+1}. {q}")

    # 检查是否有缓存的分析结果
    cached_bloom = get_analysis_result(session_id, 'bloom')

    demo_mode = st.session_state.get('demo_mode', True)
    api_key = st.session_state.get('api_key', '')

    if cached_bloom:
        bloom_results = cached_bloom
        st.success("✅ 已有 Bloom 分类结果（缓存）")
    else:
        btn_label = "🎮 Demo: 自动 Bloom 分类" if demo_mode else "🤖 AI 进行 Bloom 分类"
        if st.button(btn_label, type="primary"):
            with st.spinner("AI 正在分析提问的认知层次..."):
                if demo_mode:
                    bloom_results = demo_classify_bloom_questions(questions)
                elif api_key:
                    client = get_client(api_key, st.session_state.get('base_url', ''))
                    bloom_results = classify_bloom_questions(
                        client, st.session_state.get('model_name', 'gpt-3.5-turbo'), questions)
                else:
                    st.warning("⚠️ 请配置 API Key 或开启 Demo 模式")
                    bloom_results = None
                if bloom_results:
                    save_analysis_result(session_id, 'bloom', bloom_results)
                    st.success("✅ Bloom 分类完成！")
        else:
            bloom_results = None

    if bloom_results:
        # 分类结果表
        bloom_df = pd.DataFrame(bloom_results)
        st.dataframe(bloom_df, use_container_width=True, hide_index=True)

        # 统计分布
        level_counts = Counter([r.get('level', '未知') for r in bloom_results])
        bloom_bar = create_bloom_bar(level_counts)
        st_pyecharts(bloom_bar, height="400px")

        # 分析总结
        high_order = sum(level_counts.get(l, 0) for l in ['分析', '评价', '创造'])
        low_order = sum(level_counts.get(l, 0) for l in ['记忆', '理解'])
        total_q = len(bloom_results)

        if total_q > 0:
            high_ratio = high_order / total_q
            st.markdown(f"""
            **分析结论：**
            - 高阶思维提问（分析+评价+创造）占比：**{high_ratio:.0%}**
            - 低阶思维提问（记忆+理解）占比：**{(1-high_ratio):.0%}**
            """)
            if high_ratio >= 0.4:
                st.success("✅ 高阶思维提问比例良好，有利于促进学生深层学习。")
            else:
                st.warning("⚠️ 建议增加分析、评价、创造等高阶思维提问，促进深层学习。")
else:
    st.info("未检测到教师提问")

# ========== 3. IRE/IRF 互动模式 ==========
st.markdown("---")
st.subheader("🔄 3. IRE/IRF 课堂互动模式分析")

st.markdown("""
> **IRE模式**：Initiation（教师发起）→ Response（学生回应）→ Evaluation（教师评价）
> **IRF模式**：Initiation（教师发起）→ Response（学生回应）→ Feedback（教师反馈，引导深入）
> 
> IRF模式一般被认为优于IRE模式，因为反馈能引导学生进一步思考。
""")

patterns = analyze_ire_patterns(dialogues)

if patterns:
    pattern_counts = count_interaction_pattern_types(patterns)
    ire_count = pattern_counts['ire_count']
    irf_count = pattern_counts['irf_count']
    ir_count = pattern_counts['ir_count']

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("IRE（评价型）", ire_count)
    with col2:
        st.metric("IRF（反馈型）", irf_count)
    with col3:
        st.metric("IR（无评价）", ir_count)

    ire_chart = create_ire_bar(ire_count, irf_count, ir_count)
    st_pyecharts(ire_chart, height="400px")

    # 详细模式展示
    st.markdown("**详细互动模式：**")
    for i, p in enumerate(patterns):
        ptype = normalize_pattern_type(p.get('type', ''))
        with st.expander(f"模式 {i+1}：{ptype}"):
            st.markdown(f"**🧑‍🏫 教师发起 (I)**：{p['I']}")
            for r in p['R']:
                st.markdown(f"**👩‍🎓 学生回应 (R)**：{r}")
            if p['E']:
                label = "评价 (E)" if ptype == 'IRE' else "反馈 (F)"
                st.markdown(f"**🧑‍🏫 教师{label}**：{p['E']}")

    # 保存分析结果
    save_analysis_result(session_id, 'interaction', {
        'talk_ratio': talk_ratio,
        'question_count': len(questions),
        'ire_count': ire_count,
        'irf_count': irf_count,
        'ir_count': ir_count,
        'total_patterns': len(patterns),
    })
else:
    st.info("未检测到明显的互动模式")
