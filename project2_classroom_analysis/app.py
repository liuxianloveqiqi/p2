"""
AI驱动的课堂互动分析与教学反思辅助平台 - 主入口
"""
import streamlit as st
from utils.db_manager import init_db

init_db()

st.set_page_config(
    page_title="课堂互动分析平台",
    page_icon="💬",
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
st.title("💬 AI驱动的课堂互动分析与教学反思辅助平台")

st.markdown("""
### 项目简介

本平台面向**教师专业发展**场景，利用生成式AI和自然语言处理技术，
对课堂教学对话进行深度分析，帮助教师了解自身教学互动模式，促进**反思性教学实践**。

---

### 🔄 分析流程

<div style="display: flex; justify-content: center; gap: 15px; margin: 30px 0;">
    <div style="text-align: center; padding: 20px; background: #e8f4fd; border-radius: 10px; flex: 1;">
        <h3>📤 Step 1</h3>
        <p>上传课堂对话<br>文本记录</p>
    </div>
    <div style="text-align: center; padding: 5px; display: flex; align-items: center;">
        <h2>→</h2>
    </div>
    <div style="text-align: center; padding: 20px; background: #e8f8e8; border-radius: 10px; flex: 1;">
        <h3>💬 Step 2</h3>
        <p>互动模式分析<br>Bloom分类 / IRE分析</p>
    </div>
    <div style="text-align: center; padding: 5px; display: flex; align-items: center;">
        <h2>→</h2>
    </div>
    <div style="text-align: center; padding: 20px; background: #fff8e1; border-radius: 10px; flex: 1;">
        <h3>☁️ Step 3</h3>
        <p>关键词主题分析<br>词云 / AI主题提取</p>
    </div>
    <div style="text-align: center; padding: 5px; display: flex; align-items: center;">
        <h2>→</h2>
    </div>
    <div style="text-align: center; padding: 20px; background: #f3e5f5; border-radius: 10px; flex: 1;">
        <h3>📝 Step 4</h3>
        <p>AI教学反思报告<br>亮点/不足/改进建议</p>
    </div>
    <div style="text-align: center; padding: 5px; display: flex; align-items: center;">
        <h2>→</h2>
    </div>
    <div style="text-align: center; padding: 20px; background: #fce4ec; border-radius: 10px; flex: 1;">
        <h3>📈 Step 5</h3>
        <p>历史对比<br>多课次趋势追踪</p>
    </div>
</div>

---

### 📐 理论基础

| 理论框架 | 在本平台中的应用 |
|---------|---------------|
| **Bloom认知目标分类学** | 对教师提问进行6个认知层次分类分析 |
| **IRE/IRF话语分析** | 识别"发起-回应-评价/反馈"的课堂互动模式 |
| **教师专业发展理论** | 通过数据驱动的反思促进教学改进 |
| **学习分析 (Learning Analytics)** | 运用NLP和数据可视化理解教学过程 |

### 🛠️ 技术架构

| 组件 | 技术 |
|------|------|
| Web 框架 | Streamlit |
| AI 引擎 | OpenAI 兼容 API (GPT/GLM/DeepSeek) |
| NLP | jieba 中文分词 |
| 可视化 | Pyecharts + WordCloud + Plotly |
| 数据存储 | SQLite |

""", unsafe_allow_html=True)

st.markdown("---")
st.info("👈 请使用左侧导航栏进入各功能模块")
