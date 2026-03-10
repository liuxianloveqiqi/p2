"""
主题词云页面 - 关键词分析与AI主题提取
"""
import streamlit as st
import pandas as pd
import base64
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db_manager import (get_all_sessions, get_session_dialogues,
                               save_analysis_result, get_analysis_result, init_db)
from utils.nlp_processor import segment_and_count
from utils.chart_helper import generate_wordcloud_image
from utils.ai_service import get_client, extract_themes, demo_extract_themes

init_db()

st.set_page_config(page_title="主题词云", page_icon="☁️", layout="wide")
st.title("☁️ 关键词与主题分析")

st.markdown("通过**中文分词**和**词频统计**生成词云，结合**AI主题提取**深度理解课堂教学内容。")

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
if dialogues_df.empty:
    st.warning("该课堂暂无对话数据")
    st.stop()

# ========== 1. 词频统计 ==========
st.subheader("📊 词频统计")

# 分角色分析
role_filter = st.radio("分析范围", ["全部对话", "仅教师话语", "仅学生话语"], horizontal=True)

if role_filter == "仅教师话语":
    texts = dialogues_df[dialogues_df['role'] == '教师']['content'].tolist()
elif role_filter == "仅学生话语":
    texts = dialogues_df[dialogues_df['role'] == '学生']['content'].tolist()
else:
    texts = dialogues_df['content'].tolist()

top_n = st.slider("显示词数", 10, 100, 30)
word_freq = segment_and_count(texts, top_n)

if word_freq:
    # 词频表格
    freq_df = pd.DataFrame(word_freq, columns=['关键词', '出现频次'])
    freq_df.index += 1
    freq_df.index.name = '排名'

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**📋 高频词汇表：**")
        st.dataframe(freq_df, use_container_width=True, height=400)

    with col2:
        st.markdown("**☁️ 词云图：**")
        wc_base64 = generate_wordcloud_image(word_freq)
        if wc_base64:
            st.image(f"data:image/png;base64,{wc_base64}", use_container_width=True)
        else:
            st.warning("词云生成失败，请检查系统字体配置")

        # 显示基本统计
        st.markdown(f"""
        **统计信息：**
        - 不重复词汇数：{len(word_freq)}
        - 最高频词：**{word_freq[0][0]}**（{word_freq[0][1]}次）
        - 总词频：{sum(c for _, c in word_freq)}
        """)
else:
    st.info("未提取到有效词汇")

# ========== 2. AI 主题提取 ==========
st.markdown("---")
st.subheader("🤖 AI 课堂主题提取")

cached_themes = get_analysis_result(session_id, 'themes')
demo_mode = st.session_state.get('demo_mode', True)
api_key = st.session_state.get('api_key', '')

if cached_themes:
    themes = cached_themes
    st.success("✅ 已有主题分析结果（缓存）")
else:
    btn_label = "🎮 Demo: 提取课堂主题" if demo_mode else "🔍 AI 提取课堂主题"
    if st.button(btn_label, type="primary"):
        with st.spinner("AI 正在分析课堂主题..."):
            full_text = "\n".join([f"{row['role']}: {row['content']}" for _, row in dialogues_df.iterrows()])
            if demo_mode:
                themes = demo_extract_themes(full_text)
            elif api_key:
                client = get_client(api_key, st.session_state.get('base_url', ''))
                themes = extract_themes(client, st.session_state.get('model_name', 'gpt-3.5-turbo'), full_text)
            else:
                st.warning("⚠️ 请配置 API Key 或开启 Demo 模式")
                themes = None
            if themes:
                save_analysis_result(session_id, 'themes', themes)
                st.success("✅ 主题提取完成！")
    else:
        themes = None

if themes:
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"### 📌 课堂主题：{themes.get('main_topic', '未知')}")

        st.markdown("**📚 子主题：**")
        for t in themes.get('sub_topics', []):
            st.markdown(f"  - {t}")

        st.markdown("**🎯 教学目标：**")
        for obj in themes.get('teaching_objectives', []):
            st.markdown(f"  - {obj}")

    with col2:
        st.markdown("**🔑 核心概念：**")
        for c in themes.get('key_concepts', []):
            st.markdown(f"  - `{c}`")

        st.markdown("**📖 教学方法：**")
        for m in themes.get('teaching_methods', []):
            st.markdown(f"  - {m}")

    st.markdown("---")
    st.markdown("**📝 课堂概述：**")
    st.markdown(themes.get('summary', ''))
