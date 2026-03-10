# 基于生成式AI的学生作答分析与知识诊断系统

## 项目简介

本系统面向中小学教师，利用生成式AI（大语言模型）对学生主观题作答进行智能分析，自动诊断知识薄弱点，并生成个性化学习建议。体现了教育技术领域中**学习分析**、**智能评测**、**个性化学习**的核心理念。

## 理论基础

- **形成性评价理论**：通过持续的作答分析为教学提供即时反馈
- **知识追踪（Knowledge Tracing）**：追踪学生各知识点掌握状态
- **个性化学习路径**：基于诊断结果推荐差异化学习资源

## 技术栈

- Python + Streamlit（Web界面）
- OpenAI/兼容 API（大模型调用）
- Pyecharts + Streamlit-Echarts（数据可视化）
- SQLite（数据持久化）
- Pandas（数据处理）

## 核心功能

1. **作答数据管理**：上传 CSV/Excel 格式学生作答数据
2. **AI智能批阅**：自动评分、错误分类、评语生成
3. **知识诊断可视化**：雷达图（个人）、热力图（班级）
4. **个性化学习推荐**：基于弱项的针对性学习资源推荐
5. **班级分析看板**：成绩分布、知识点达标率、高频错误

## 运行方式

```bash
# 安装依赖
pip install -r requirements.txt

# 设置 API Key（选择一种方式）
export OPENAI_API_KEY="your-api-key"
# 或在界面侧边栏中填入

# 启动系统
streamlit run app.py
```

## 示例数据

项目包含 `data/sample_answers.csv` 示例数据，可直接上传体验。

## 目录结构

```
project1_knowledge_diagnosis/
├── app.py                  # 主入口
├── pages/
│   ├── 1_📤_数据上传.py
│   ├── 2_🤖_AI智能批阅.py
│   ├── 3_📊_知识诊断.py
│   ├── 4_📚_学习推荐.py
│   └── 5_🏫_班级看板.py
├── utils/
│   ├── ai_service.py       # 大模型调用
│   ├── db_manager.py       # 数据库管理
│   ├── chart_helper.py     # 可视化辅助
│   └── data_processor.py   # 数据处理
├── data/
│   └── sample_answers.csv  # 示例数据
├── requirements.txt
└── README.md
```
