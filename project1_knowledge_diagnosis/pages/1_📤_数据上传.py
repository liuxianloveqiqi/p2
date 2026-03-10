"""
数据上传页面
"""
import streamlit as st
import pandas as pd
import uuid
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.db_manager import save_answers, get_all_answers, clear_all_data, init_db
from utils.data_processor import validate_upload_data

init_db()

st.set_page_config(page_title="数据上传", page_icon="📤", layout="wide")
st.title("📤 学生作答数据上传")

st.markdown("""
上传学生的主观题作答数据，支持 **CSV** 和 **Excel** 格式。

**必要字段：** `学生姓名`、`题目编号`、`题目内容`、`所属知识点`、`学生作答`、`参考答案`
**可选字段：** `满分`（默认为10分）
""")

# 上传文件
uploaded_file = st.file_uploader("选择文件", type=['csv', 'xlsx', 'xls'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success(f"✅ 文件读取成功！共 {len(df)} 条记录")

        # 数据预览
        st.subheader("📋 数据预览")
        st.dataframe(df, use_container_width=True, height=300)

        # 数据统计
        col1, col2, col3 = st.columns(3)
        with col1:
            students = df['学生姓名'].nunique() if '学生姓名' in df.columns else 0
            st.metric("学生人数", students)
        with col2:
            questions = df['题目编号'].nunique() if '题目编号' in df.columns else 0
            st.metric("题目数量", questions)
        with col3:
            kps = df['所属知识点'].nunique() if '所属知识点' in df.columns else 0
            st.metric("知识点数量", kps)

        # 验证数据
        is_valid, msg = validate_upload_data(df)
        if not is_valid:
            st.error(f"❌ 数据验证失败: {msg}")
        else:
            st.success(f"✅ {msg}")

            if st.button("📥 导入数据到系统", type="primary"):
                batch_id = str(uuid.uuid4())[:8]
                save_answers(df, batch_id)
                st.success(f"🎉 数据导入成功！批次号: {batch_id}")
                st.balloons()
    except Exception as e:
        st.error(f"❌ 文件读取失败: {str(e)}")

# 示例数据下载
st.markdown("---")
st.subheader("📦 示例数据")
sample_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_answers.csv")
if os.path.exists(sample_path):
    with open(sample_path, 'r', encoding='utf-8') as f:
        st.download_button(
            label="⬇️ 下载示例数据 (CSV)",
            data=f.read(),
            file_name="sample_answers.csv",
            mime="text/csv"
        )

# 查看已有数据
st.markdown("---")
st.subheader("📂 已导入数据")
existing = get_all_answers()
if not existing.empty:
    st.dataframe(existing, use_container_width=True, height=300)
    st.info(f"共有 {len(existing)} 条作答记录")

    if st.button("🗑️ 清空所有数据", type="secondary"):
        clear_all_data()
        st.warning("已清空所有数据，请刷新页面")
        st.rerun()
else:
    st.info("暂无数据，请上传作答文件")
