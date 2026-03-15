"""
AI服务模块 - 大模型调用：Bloom分类、主题提取、反思报告生成
支持 Demo 演示模式（无需 API Key）
"""
import json
import os
import time
import re
from openai import OpenAI


def get_client(api_key: str = None, base_url: str = None):
    key = api_key or os.getenv("OPENAI_API_KEY", "")
    url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return OpenAI(api_key=key, base_url=url)


# ============ Demo 模式模拟函数 ============

def _classify_question_by_rules(question: str) -> tuple:
    """基于规则的 Bloom 层次分类"""
    q = question.lower()
    
    # 创造层次
    if any(k in q for k in ['设计', '如何创', '提出', '方案', '规划', '如果你', '发明']):
        return '创造', '问题要求学生设计或创造新方案'
    # 评价层次
    if any(k in q for k in ['评价', '判断', '优缺点', '你认为', '是否合理', '比较好']):
        return '评价', '问题要求学生做出价值判断'
    # 分析层次
    if any(k in q for k in ['为什么', '原因', '分析', '比较', '区别', '关系', '如果', '会发生什么', '推理']):
        return '分析', '问题要求学生分析因果或比较'
    # 应用层次
    if any(k in q for k in ['举例', '应用', '实验', '验证', '怎样使用', '解决']):
        return '应用', '问题要求在新情境中运用知识'
    # 理解层次
    if any(k in q for k in ['解释', '说明', '描述', '意义', '过程', '概括', '总结']):
        return '理解', '问题要求解释或说明概念'
    # 记忆层次
    if any(k in q for k in ['什么是', '哪些', '列举', '回忆', '定义', '叫什么']):
        return '记忆', '问题要求回忆或列举事实'

    return '理解', '问题涉及对概念的理解和表述'


def demo_classify_bloom_questions(questions: list) -> list:
    """Demo模式：基于规则的Bloom提问分类"""
    time.sleep(0.5)
    results = []
    for q in questions:
        level, explanation = _classify_question_by_rules(q)
        results.append({
            "question": q,
            "level": level,
            "explanation": explanation
        })
    return results


def demo_extract_themes(dialogues_text: str) -> dict:
    """Demo模式：基于关键词的主题提取"""
    time.sleep(0.5)

    # 简单提取高频实词
    import jieba
    from collections import Counter
    from utils.nlp_processor import STOP_WORDS
    words = list(jieba.cut(dialogues_text))
    word_freq = Counter(w for w in words if len(w) >= 2 and w not in STOP_WORDS)
    top_words = [w for w, _ in word_freq.most_common(10)]

    # 检测主题关键词
    main_topic = top_words[0] if top_words else "课堂教学"

    return {
        "main_topic": main_topic,
        "sub_topics": [
            f"{main_topic}的基本概念与原理",
            f"{main_topic}的过程与机制",
            f"{main_topic}的实际应用与意义"
        ],
        "teaching_objectives": [
            f"理解{main_topic}的基本概念和核心原理",
            f"能够运用所学知识分析{main_topic}相关问题",
            f"培养科学思维能力和实验设计能力"
        ],
        "key_concepts": top_words[:5],
        "teaching_methods": [
            "问答法（通过层层递进的提问引导学生思考）",
            "讨论法（组织学生进行小组讨论）",
            "启发式教学（从已知引导未知）"
        ],
        "summary": f"本节课围绕「{main_topic}」展开教学，教师通过提问-回答-反馈的方式，"
                   f"从基本概念出发，逐步深入到原理机制，最后拓展到实际应用。"
                   f"课堂中涉及的核心概念包括{'、'.join(top_words[:4])}等。"
                   f"教师采用了启发式教学和讨论法相结合的方式，引导学生主动思考。"
    }


def demo_generate_reflection_report(session_info: dict, interaction_metrics: dict,
                                     bloom_results: list = None, themes: dict = None) -> str:
    """Demo模式：生成教学反思报告"""
    time.sleep(0.5)

    session_name = session_info.get('session_name', '课堂')
    subject = session_info.get('subject', '学科')
    teacher_ratio = interaction_metrics.get('teacher_word_ratio', 0.5)
    student_ratio = interaction_metrics.get('student_word_ratio', 0.5)
    question_count = interaction_metrics.get('question_count', 0)
    ire_count = interaction_metrics.get('ire_count', 0)
    irf_count = interaction_metrics.get('irf_count', 0)
    total_turns = interaction_metrics.get('teacher_turns', 0) + interaction_metrics.get('student_turns', 0)

    # Bloom分析
    bloom_summary = ""
    high_order_count = 0
    if bloom_results:
        from collections import Counter
        levels = Counter(r.get('level', '未知') for r in bloom_results)
        bloom_summary = "、".join([f"{k}{v}个" for k, v in levels.items()])
        high_order_count = sum(levels.get(l, 0) for l in ['分析', '评价', '创造'])

    theme_text = themes.get('main_topic', session_name) if themes else session_name

    # 评估
    dominance_eval = "偏高" if teacher_ratio > 0.65 else ("均衡" if teacher_ratio > 0.45 else "较低，学生主导性强")
    irf_ratio = irf_count / max(ire_count + irf_count, 1)

    return f"""## 📋 教学反思报告

### 一、课堂概况

本课为「{session_name}」（{subject}），主题为 **{theme_text}**。
课堂共产生 **{total_turns}** 轮对话，教师提出了 **{question_count}** 个问题，
形成了 {ire_count + irf_count} 个完整的互动循环。

---

### 二、互动质量分析

#### 2.1 师生话语比例
- 教师话语占比：**{teacher_ratio:.0%}**（{dominance_eval}）
- 学生话语占比：**{student_ratio:.0%}**
- 教师平均发言 {interaction_metrics.get('avg_teacher_length', 0):.0f} 字/轮，学生平均 {interaction_metrics.get('avg_student_length', 0):.0f} 字/轮

{"✅ 师生话语比例较为均衡，学生有充足的表达空间。" if 0.4 <= teacher_ratio <= 0.65 else "⚠️ 教师话语占比偏高，建议适当减少讲授时间，增加学生表达机会。" if teacher_ratio > 0.65 else "💡 学生话语占比较高，课堂互动活跃。"}

#### 2.2 提问层次分析（Bloom认知目标分类）
{f"- 本节课提问的Bloom层次分布：{bloom_summary}" if bloom_summary else "- 暂无Bloom分析数据"}
{f"- 高阶思维提问（分析+评价+创造）共 **{high_order_count}** 个，占比 **{high_order_count/max(question_count,1):.0%}**" if bloom_results else ""}
{f"- {'✅ 高阶思维提问比例良好' if high_order_count/max(question_count,1) >= 0.3 else '⚠️ 建议增加更多分析、评价、创造类的高阶提问'}" if bloom_results else ""}

#### 2.3 互动模式分析
- IRE模式（发起-回应-评价）：**{ire_count}** 次
- IRF模式（发起-回应-反馈）：**{irf_count}** 次
- IRF占比：**{irf_ratio:.0%}**
- {"✅ IRF模式占比较高，教师善于通过反馈引导学生深入思考。" if irf_ratio >= 0.6 else "⚠️ 建议将更多简单评价（IRE）转化为引导性反馈（IRF），促进学生深层学习。"}

---

### 三、教学亮点

1. **层层递进的提问设计**：教师的提问从基础概念逐步深入到应用分析，有利于搭建认知脚手架
2. **及时的反馈引导**：教师能在学生回答后给予积极反馈并进一步追问，形成有效的对话循环
3. **多样化的互动方式**：课堂中综合运用了个别提问、集体讨论等多种互动形式

---

### 四、改进建议

1. **增加等待时间**：提问后给学生更多思考时间（建议3-5秒），有助于获得更深层次的回答
2. **扩大参与面**：注意让更多学生参与回答，避免仅与少数学生互动
3. **提升提问开放性**：适当增加开放性问题（如"你怎么看""还有什么可能"），激发多元思维
4. **强化生生互动**：鼓励学生之间的讨论和互评，减少"教师-学生"的单一互动模式

---

### 五、专业发展方向

1. **课堂话语研究**：持续关注师生话语比例，逐步向"以学生为中心"的课堂转型
2. **提问技巧提升**：研究和实践 Bloom 分类学指导下的高阶思维提问策略
3. **形成性评价能力**：学习利用课堂互动数据进行教学反思，建立数据驱动的教学改进习惯
"""


def classify_bloom_questions(client, model: str, questions: list) -> list:
    """
    基于 Bloom 认知目标分类学对教师提问进行分类
    返回: [{"question": str, "level": str, "explanation": str}]
    
    Bloom层次: 记忆、理解、应用、分析、评价、创造
    """
    questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions)])

    prompt = f"""你是一位教育学专家，精通Bloom认知目标分类学。请对以下教师课堂提问进行认知层次分类。

Bloom认知目标六个层次（从低到高）：
1. 记忆（Remember）：回忆事实、术语、概念
2. 理解（Understand）：解释、说明、概括
3. 应用（Apply）：在新情境中使用知识
4. 分析（Analyze）：分解、比较、区分因果
5. 评价（Evaluate）：判断、评估、论证
6. 创造（Create）：设计、规划、产生新想法

【教师提问列表】
{questions_text}

请以JSON数组格式返回，每个元素包含 question、level、explanation 三个字段：
[
    {{"question": "原始提问", "level": "Bloom层次", "explanation": "分类理由（20字以内）"}}
]"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是教育学专家，请以JSON数组格式返回分析结果。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2000
        )
        content = response.choices[0].message.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        # 返回默认分类
        return [{"question": q, "level": "待分类", "explanation": f"分类失败: {str(e)}"} for q in questions]


def extract_themes(client, model: str, dialogues_text: str) -> dict:
    """
    提取课堂核心主题和教学重点
    """
    prompt = f"""你是一位教育研究者，请分析以下课堂对话记录，提取核心主题和教学重点。

【课堂对话】
{dialogues_text[:3000]}

请以JSON格式返回：
{{
    "main_topic": "课堂主题（10字以内）",
    "sub_topics": ["子主题1", "子主题2", "子主题3"],
    "teaching_objectives": ["教学目标1", "教学目标2"],
    "key_concepts": ["核心概念1", "核心概念2", "核心概念3"],
    "teaching_methods": ["使用的教学方法1", "教学方法2"],
    "summary": "课堂内容概述（100字左右）"
}}"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是教育研究专家，请以JSON格式返回分析结果。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1000
        )
        content = response.choices[0].message.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        return {
            "main_topic": "提取失败",
            "sub_topics": [],
            "teaching_objectives": [],
            "key_concepts": [],
            "teaching_methods": [],
            "summary": f"主题提取出现异常: {str(e)}"
        }


def generate_reflection_report(client, model: str, session_info: dict,
                                interaction_metrics: dict,
                                bloom_results: list = None,
                                themes: dict = None) -> str:
    """
    生成结构化教学反思报告
    """
    bloom_summary = ""
    if bloom_results:
        levels = [r.get('level', '未知') for r in bloom_results]
        from collections import Counter
        level_counts = Counter(levels)
        bloom_summary = "、".join([f"{k}{v}个" for k, v in level_counts.items()])

    theme_summary = ""
    if themes:
        theme_summary = f"课堂主题：{themes.get('main_topic', '未知')}，核心概念：{'、'.join(themes.get('key_concepts', []))}"

    prompt = f"""你是一位资深教育研究者和教师培训专家，请根据以下课堂互动分析数据，为教师撰写一份结构化的教学反思报告。

【课堂基本信息】
- 课堂名称：{session_info.get('session_name', '未知')}
- 学科：{session_info.get('subject', '未知')}
- {theme_summary}

【互动数据分析】
- 总对话轮次：{interaction_metrics.get('teacher_turns', 0) + interaction_metrics.get('student_turns', 0)}
- 教师话语占比：{interaction_metrics.get('teacher_word_ratio', 0):.0%}（字数）/ {interaction_metrics.get('teacher_turn_ratio', 0):.0%}（轮次）
- 学生话语占比：{interaction_metrics.get('student_word_ratio', 0):.0%}（字数）/ {interaction_metrics.get('student_turn_ratio', 0):.0%}（轮次）
- 教师平均发言长度：{interaction_metrics.get('avg_teacher_length', 0):.0f}字
- 学生平均发言长度：{interaction_metrics.get('avg_student_length', 0):.0f}字
- 教师提问数量：{interaction_metrics.get('question_count', 0)}
- Bloom提问层次分布：{bloom_summary}
- IRE模式：{interaction_metrics.get('ire_count', 0)}次
- IRF模式：{interaction_metrics.get('irf_count', 0)}次

请生成一份专业的教学反思报告，包含以下部分：

## 📋 教学反思报告

### 一、课堂概况
（简要描述课堂基本情况）

### 二、互动质量分析
#### 2.1 师生话语比例分析
#### 2.2 提问层次分析（基于Bloom认知目标分类）
#### 2.3 互动模式分析（IRE/IRF）

### 三、教学亮点
（至少3点具体的教学优势）

### 四、改进建议
（至少3条可操作的改进建议）

### 五、专业发展方向
（基于数据分析提出2-3个教师专业发展方向）

用 Markdown 格式输出，专业但平易近人，约500-800字。"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一位资深教育研究者，擅长基于课堂数据分析为教师提供专业的教学反思支持。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"生成教学反思报告时出现异常: {str(e)}"
