"""
AI智能批阅页面
"""
import streamlit as st
import pandas as pd
import time
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db_manager import get_ungraded_answers, get_all_answers, save_grading_result, get_grading_results, init_db
from utils.ai_service import get_client, grade_answer, demo_grade_answer

init_db()

st.set_page_config(page_title="AI智能批阅", page_icon="🤖", layout="wide")
st.title("🤖 AI 智能批阅")

st.markdown("""
利用生成式AI对学生的主观题作答进行自动批阅，生成**评分**、**错误类型分类**和**改进建议**。
""")

# 检查运行模式
demo_mode = st.session_state.get('demo_mode', True)
api_key = st.session_state.get('api_key', '')
base_url = st.session_state.get('base_url', 'https://api.openai.com/v1')
model_name = st.session_state.get('model_name', 'gpt-3.5-turbo')

if demo_mode:
    st.info("🎮 当前为 **Demo 演示模式**，使用内置规则模拟 AI 批阅")
elif not api_key:
    st.warning("⚠️ 请先在主页侧边栏配置 API Key 或开启 Demo 模式")
    st.stop()

# 获取待批阅数据
ungraded = get_ungraded_answers()
graded = get_grading_results()

col1, col2 = st.columns(2)
with col1:
    st.metric("待批阅", f"{len(ungraded)} 题")
with col2:
    st.metric("已批阅", f"{len(graded)} 题")

if ungraded.empty:
    if graded.empty:
        st.info("📭 暂无作答数据，请先上传数据")
    else:
        st.success("✅ 所有作答已批阅完成！")

        st.subheader("📋 批阅结果")
        display_cols = ['student_name', 'question_id', 'knowledge_point',
                        'student_answer', 'score', 'error_type', 'comment']
        st.dataframe(graded[display_cols], use_container_width=True, height=400)
    st.stop()

# 预览待批阅数据
st.subheader("📋 待批阅作答")
st.dataframe(ungraded[['student_name', 'question_id', 'question_content',
                        'knowledge_point', 'student_answer']],
             use_container_width=True, height=300)

# 开始批阅
st.markdown("---")
st.subheader("🚀 开始 AI 批阅")

batch_size = st.slider("每批处理数量", 1, min(20, len(ungraded)), min(5, len(ungraded)))

if st.button("🤖 开始自动批阅", type="primary"):
    client = None if demo_mode else get_client(api_key, base_url)

    progress_bar = st.progress(0)
    status_text = st.empty()
    results_container = st.container()

    batch = ungraded.head(batch_size)
    total = len(batch)

    for idx, (_, row) in enumerate(batch.iterrows()):
        status_text.text(f"正在批阅: {row['student_name']} - 题目{row['question_id']} ({idx+1}/{total})")

        if demo_mode:
            result = demo_grade_answer(
                question=row['question_content'],
                reference=row['reference_answer'],
                student_answer=row['student_answer'],
                full_score=row['full_score']
            )
        else:
            result = grade_answer(
                client=client,
                model=model_name,
                question=row['question_content'],
                reference=row['reference_answer'],
                student_answer=row['student_answer'],
                full_score=row['full_score']
            )

        # 保存结果
        save_grading_result(
            answer_id=row['id'],
            score=result['score'],
            error_type=result['error_type'],
            comment=result['comment'],
            improvement=result['improvement']
        )

        # 显示结果
        with results_container:
            with st.expander(f"✅ {row['student_name']} - 题目{row['question_id']}: {result['score']}/{row['full_score']}分"):
                st.markdown(f"**题目：** {row['question_content']}")
                st.markdown(f"**学生作答：** {row['student_answer']}")
                st.markdown(f"**得分：** {result['score']}/{row['full_score']}")
                st.markdown(f"**错误类型：** {result['error_type']}")
                st.markdown(f"**评语：** {result['comment']}")
                st.markdown(f"**改进建议：** {result['improvement']}")

        progress_bar.progress((idx + 1) / total)
        time.sleep(0.5)  # 避免 API 限流

    status_text.text("🎉 批阅完成！")
    st.success(f"✅ 本次成功批阅 {total} 道题目")
    st.balloons()

# 显示已有结果
if not graded.empty:
    st.markdown("---")
    st.subheader("📊 已有批阅结果")
    st.dataframe(graded, use_container_width=True, height=400)
