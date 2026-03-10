"""
基于生成式AI的学生作答分析与知识诊断系统 - 主入口
"""
import streamlit as st
from utils.db_manager import init_db

# 初始化数据库
init_db()

st.set_page_config(
    page_title="AI知识诊断系统",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ 侧边栏 - API配置 ============
with st.sidebar:
    st.header("⚙️ 系统配置")
    st.markdown("---")

    demo_mode = st.toggle("🎮 Demo 演示模式", value=True,
                          help="无需 API Key，使用内置规则模拟 AI 功能，可完整体验所有流程")
    st.session_state['demo_mode'] = demo_mode

    if demo_mode:
        st.success("✅ Demo 模式已开启，无需配置 API")
        st.session_state['api_key'] = ''
        st.session_state['base_url'] = ''
        st.session_state['model_name'] = ''
    else:
        st.markdown("#### 🔑 API 配置")
        # 优先从 Streamlit Cloud Secrets 读取，本地手动输入
        default_key = st.secrets.get("OPENAI_API_KEY", "") if hasattr(st, 'secrets') else ""
        default_url = st.secrets.get("OPENAI_BASE_URL", "https://api.deepseek.com") if hasattr(st, 'secrets') else "https://api.deepseek.com"
        default_model = st.secrets.get("OPENAI_MODEL", "deepseek-chat") if hasattr(st, 'secrets') else "deepseek-chat"

        api_key = st.text_input("API Key", value=default_key, type="password",
                                help="支持 OpenAI / 智谱 / DeepSeek 等兼容接口")
        base_url = st.text_input("API Base URL", value=default_url,
                                 help="兼容 OpenAI 格式的接口地址")
        model_name = st.text_input("模型名称", value=default_model,
                                    help="如 gpt-4, glm-4, deepseek-chat 等")

        st.session_state['api_key'] = api_key
        st.session_state['base_url'] = base_url
        st.session_state['model_name'] = model_name

    st.markdown("---")
    st.markdown("#### 💡 推荐 API 服务")
    st.markdown("""
    - **DeepSeek**: [platform.deepseek.com](https://platform.deepseek.com)  
      模型: `deepseek-chat`，价格低廉
    - **智谱AI**: [open.bigmodel.cn](https://open.bigmodel.cn)  
      模型: `glm-4-flash`，有免费额度
    - **硅基流动**: [siliconflow.cn](https://siliconflow.cn)  
      模型: `Qwen/Qwen2.5-7B-Instruct`，免费
    """)

# ============ 主页面 ============
st.title("🎓 基于生成式AI的学生作答分析与知识诊断系统")

st.markdown("""
### 系统简介

本系统面向中小学教师，利用**生成式人工智能**（大语言模型）对学生主观题作答进行智能分析，
帮助教师快速了解每位学生的知识掌握状况，实现**精准教学**与**因材施教**。

---

### 🔄 使用流程

<div style="display: flex; justify-content: center; gap: 20px; margin: 30px 0;">
    <div style="text-align: center; padding: 20px; background: #e8f4fd; border-radius: 10px; flex: 1;">
        <h3>📤 Step 1</h3>
        <p>上传学生作答数据<br>(CSV/Excel)</p>
    </div>
    <div style="text-align: center; padding: 5px; display: flex; align-items: center;">
        <h2>→</h2>
    </div>
    <div style="text-align: center; padding: 20px; background: #e8f8e8; border-radius: 10px; flex: 1;">
        <h3>🤖 Step 2</h3>
        <p>AI 自动智能批阅<br>评分+评语+错误分类</p>
    </div>
    <div style="text-align: center; padding: 5px; display: flex; align-items: center;">
        <h2>→</h2>
    </div>
    <div style="text-align: center; padding: 20px; background: #fff8e1; border-radius: 10px; flex: 1;">
        <h3>📊 Step 3</h3>
        <p>知识诊断可视化<br>雷达图+热力图</p>
    </div>
    <div style="text-align: center; padding: 5px; display: flex; align-items: center;">
        <h2>→</h2>
    </div>    cd /Users/liuxian/pyProject/education-projects/p2/project2_classroom_analysis && streamlit run app.py --server.port 8502
    <div style="text-align: center; padding: 20px; background: #fce4ec; border-radius: 10px; flex: 1;">
        <h3>📚 Step 4</h3>
        <p>个性化学习推荐<br>AI 生成学习路径</p>
    </div>
</div>

---

### 📐 理论基础

| 理论 | 应用 |
|------|------|
| **形成性评价** | 通过过程性分析为教学提供即时反馈 |
| **知识追踪 (Knowledge Tracing)** | 追踪学生各知识点掌握状态变化 |
| **布鲁姆认知目标分类** | 对题目与作答进行认知层次分析 |
| **个性化学习路径** | 基于诊断结果生成差异化学习方案 |

### 🛠️ 技术架构

| 组件 | 技术 |
|------|------|
| Web 框架 | Streamlit |
| AI 引擎 | OpenAI 兼容 API (GPT/GLM/DeepSeek) |
| 数据可视化 | Pyecharts + Streamlit-Echarts |
| 数据存储 | SQLite |
| 数据处理 | Pandas |

""", unsafe_allow_html=True)

st.markdown("---")
st.info("👈 请使用左侧导航栏进入各功能模块")
