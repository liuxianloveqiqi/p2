# AI驱动的课堂互动分析与教学反思辅助平台

## 项目简介

本平台面向教师专业发展场景，教师上传课堂对话记录或教学文本，系统利用**生成式AI**和**NLP技术**自动分析课堂互动质量、提问层次、师生对话模式，并生成结构化的教学反思报告，帮助教师持续改进教学。

## 理论基础

- **Bloom认知目标分类学**：对教师提问进行认知层次分类（记忆→创造）
- **IRE/IRF话语分析模式**：分析课堂中"发起-回应-评价/反馈"的互动结构
- **教师专业发展**：通过数据驱动的教学反思促进教师成长
- **学习分析（Learning Analytics）**：运用数据挖掘技术理解和优化教学

## 技术栈

- Python + Streamlit（Web界面）
- OpenAI/兼容 API（大模型文本分析与报告生成）
- jieba（中文分词）
- Pyecharts + Plotly（数据可视化）
- WordCloud（词云生成）
- SQLite（数据持久化）

## 核心功能

1. **课堂对话上传与解析**：上传对话文本，自动区分师生话语
2. **互动模式分析**：师生话语比例、Bloom提问层次、IRE/IRF模式
3. **关键词与主题分析**：中文分词、词云、AI主题提取
4. **AI教学反思报告**：自动生成结构化教学反思
5. **历史对比看板**：跨课次互动指标趋势分析

## 运行方式

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-api-key"
streamlit run app.py
```

## 示例数据

项目包含 `data/sample_dialogue.txt` 和 `data/sample_dialogue.csv` 示例数据。

## 目录结构

```
project2_classroom_analysis/
├── app.py
├── pages/
│   ├── 1_📤_课堂上传.py
│   ├── 2_💬_互动分析.py
│   ├── 3_☁️_主题词云.py
│   ├── 4_📝_AI反思报告.py
│   └── 5_📈_历史对比.py
├── utils/
│   ├── ai_service.py
│   ├── db_manager.py
│   ├── nlp_processor.py
│   └── chart_helper.py
├── data/
│   ├── sample_dialogue.txt
│   └── sample_dialogue.csv
├── requirements.txt
└── README.md
```
