"""
课堂对话上传页面
"""
import streamlit as st
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db_manager import save_session, get_all_sessions, delete_session, init_db
from utils.nlp_processor import parse_dialogue_text

init_db()

st.set_page_config(page_title="课堂上传", page_icon="📤", layout="wide")
st.title("📤 课堂对话上传")

st.markdown("""
上传课堂对话文本，系统自动区分教师话语和学生话语。

**支持格式：**
- **TXT文件**：每行格式 `教师: 对话内容` 或 `学生: 对话内容`
- **CSV文件**：包含 `角色` 和 `对话内容` 两列
""")

# 课堂基本信息
st.subheader("📋 课堂基本信息")
col1, col2, col3, col4 = st.columns(4)
with col1:
    session_name = st.text_input("课堂名称", value="光合作用第一课时")
with col2:
    subject = st.text_input("学科", value="生物")
with col3:
    grade = st.text_input("年级", value="高一")
with col4:
    teacher_name = st.text_input("教师姓名", value="")

st.markdown("---")

# 上传方式选择
upload_method = st.radio("选择上传方式", ["📁 文件上传", "✏️ 手动输入"], horizontal=True)

dialogues = []

if upload_method == "📁 文件上传":
    uploaded_file = st.file_uploader("选择对话文件", type=['txt', 'csv'])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.txt'):
                text = uploaded_file.read().decode('utf-8')
                dialogues = parse_dialogue_text(text)
            elif uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
                if '角色' in df.columns and '对话内容' in df.columns:
                    dialogues = [{'role': row['角色'], 'content': row['对话内容']}
                                 for _, row in df.iterrows()]
                else:
                    st.error("CSV文件需包含'角色'和'对话内容'两列")

            if dialogues:
                st.success(f"✅ 解析成功！共 {len(dialogues)} 轮对话")
        except Exception as e:
            st.error(f"❌ 文件解析失败: {str(e)}")

else:
    st.markdown("请按 `角色: 对话内容` 格式输入，每行一轮对话：")
    text_input = st.text_area(
        "输入对话文本",
        height=300,
        placeholder="教师: 同学们，今天我们来学习...\n学生: 老师好！\n教师: 请大家翻开课本..."
    )
    if text_input:
        dialogues = parse_dialogue_text(text_input)
        if dialogues:
            st.success(f"✅ 解析成功！共 {len(dialogues)} 轮对话")

# 预览对话
if dialogues:
    st.subheader("👀 对话预览")

    teacher_count = sum(1 for d in dialogues if d['role'] == '教师')
    student_count = sum(1 for d in dialogues if d['role'] == '学生')

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("总轮次", len(dialogues))
    with col2:
        st.metric("教师发言", teacher_count)
    with col3:
        st.metric("学生发言", student_count)

    # 对话展示
    for d in dialogues:
        if d['role'] == '教师':
            st.markdown(f"🧑‍🏫 **教师**：{d['content']}")
        else:
            st.markdown(f"👩‍🎓 **学生**：{d['content']}")

    # 保存
    st.markdown("---")
    if st.button("💾 保存课堂记录", type="primary"):
        if not session_name:
            st.error("请填写课堂名称")
        else:
            session_id = save_session(session_name, subject, grade, teacher_name, dialogues)
            st.success(f"🎉 课堂记录保存成功！ID: {session_id}")
            st.balloons()

# 示例数据下载
st.markdown("---")
st.subheader("📦 示例数据")

col1, col2 = st.columns(2)
sample_txt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_dialogue.txt")
sample_csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_dialogue.csv")

with col1:
    if os.path.exists(sample_txt_path):
        with open(sample_txt_path, 'r', encoding='utf-8') as f:
            st.download_button("⬇️ 下载示例 TXT", f.read(), "sample_dialogue.txt", "text/plain")

with col2:
    if os.path.exists(sample_csv_path):
        with open(sample_csv_path, 'r', encoding='utf-8') as f:
            st.download_button("⬇️ 下载示例 CSV", f.read(), "sample_dialogue.csv", "text/csv")

# 已有课堂记录
st.markdown("---")
st.subheader("📂 已保存的课堂记录")

sessions = get_all_sessions()
if not sessions.empty:
    st.dataframe(sessions[['id', 'session_name', 'subject', 'grade', 'teacher_name',
                            'total_turns', 'teacher_turns', 'student_turns', 'created_at']],
                 use_container_width=True, hide_index=True)

    # 删除功能
    del_id = st.number_input("输入要删除的课堂 ID", min_value=1, step=1)
    if st.button("🗑️ 删除此课堂记录"):
        delete_session(del_id)
        st.warning(f"已删除课堂 ID: {del_id}")
        st.rerun()
else:
    st.info("暂无课堂记录，请上传对话数据")
