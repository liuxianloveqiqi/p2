"""
个性化学习推荐页面
"""
import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db_manager import get_grading_results, save_recommendation, get_recommendations, init_db
from utils.data_processor import compute_student_knowledge_mastery, get_student_weak_points
from utils.ai_service import get_client, generate_learning_recommendation, demo_generate_learning_recommendation

init_db()

st.set_page_config(page_title="学习推荐", page_icon="📚", layout="wide")
st.title("📚 个性化学习路径推荐")

st.markdown("""
基于知识诊断结果，利用**生成式AI**为每位学生生成针对性的学习资源推荐和练习建议，
体现**个性化学习**与**精准教学**理念。
""")

# 检查模式
demo_mode = st.session_state.get('demo_mode', True)
api_key = st.session_state.get('api_key', '')
base_url = st.session_state.get('base_url', 'https://api.openai.com/v1')
model_name = st.session_state.get('model_name', 'gpt-3.5-turbo')

# 获取数据
grading_df = get_grading_results()
if grading_df.empty:
    st.warning("⚠️ 暂无批阅数据，请先完成 AI 批阅")
    st.stop()

mastery_df = compute_student_knowledge_mastery(grading_df)
students = mastery_df['student_name'].unique().tolist()

# 选择学生
selected_student = st.selectbox("🎓 选择学生", students)

if selected_student:
    # 显示该学生的知识掌握概况
    student_data = mastery_df[mastery_df['student_name'] == selected_student]

    st.subheader(f"📋 {selected_student} 的知识掌握概况")

    cols = st.columns(len(student_data))
    for idx, (_, row) in enumerate(student_data.iterrows()):
        with cols[idx]:
            rate = row['score_rate']
            color = "🟢" if rate >= 0.8 else ("🟡" if rate >= 0.6 else "🔴")
            st.metric(
                f"{color} {row['knowledge_point']}",
                f"{rate:.0%}",
                delta=f"{'达标' if rate >= 0.6 else '需加强'}"
            )

    # 薄弱知识点
    weak_points = get_student_weak_points(mastery_df, selected_student, threshold=0.8)

    if not weak_points:
        st.success("🎉 该学生各知识点掌握良好，无需特别推荐！")
    else:
        st.markdown("---")
        st.subheader("🔍 薄弱知识点分析")

        for wp in weak_points:
            level = "🔴 薄弱" if wp['mastery'] < 0.6 else "🟡 需巩固"
            st.markdown(f"- **{wp['knowledge_point']}**：掌握度 {wp['mastery']:.0%} {level}，问题类型：{wp['errors']}")

        # 生成AI推荐
        st.markdown("---")
        st.subheader("🤖 AI 个性化学习推荐")

        if st.button("🚀 生成个性化学习方案", type="primary"):
            with st.spinner("AI 正在分析并生成个性化学习方案..."):
                if demo_mode:
                    recommendation = demo_generate_learning_recommendation(
                        student_name=selected_student,
                        weak_points=weak_points
                    )
                elif api_key:
                    client = get_client(api_key, base_url)
                    recommendation = generate_learning_recommendation(
                        client=client,
                        model=model_name,
                        student_name=selected_student,
                        weak_points=weak_points
                    )
                else:
                    st.warning("⚠️ 请配置 API Key 或开启 Demo 模式")
                    st.stop()

                    # 保存推荐
                    for wp in weak_points:
                        save_recommendation(
                            selected_student,
                            wp['knowledge_point'],
                            wp['mastery'],
                            recommendation
                        )

                    # 显示推荐
                    st.markdown(recommendation)
                    st.success("✅ 学习推荐已生成并保存！")

    # 历史推荐
    st.markdown("---")
    st.subheader("📜 历史学习推荐")
    
    hist_recs = get_recommendations(selected_student)
    if not hist_recs.empty:
        for _, rec in hist_recs.drop_duplicates(subset=['recommendation']).iterrows():
            with st.expander(f"📝 {rec['created_at']} - {rec['knowledge_point']}"):
                st.markdown(rec['recommendation'])
    else:
        st.info("暂无历史推荐记录")
