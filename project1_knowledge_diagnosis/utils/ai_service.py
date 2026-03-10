"""
AI服务模块 - 调用大语言模型进行智能批阅与推荐
支持 OpenAI API 及兼容接口（如智谱、DeepSeek等）
支持 Demo 演示模式（无需 API Key）
"""
import json
import os
import random
import time
from openai import OpenAI


def get_client(api_key: str = None, base_url: str = None):
    """获取 OpenAI 兼容客户端"""
    key = api_key or os.getenv("OPENAI_API_KEY", "")
    url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    return OpenAI(api_key=key, base_url=url)


# ============ Demo 模式模拟函数 ============

def _similarity_score(student_answer: str, reference: str, full_score: float) -> float:
    """简单的文本相似度评分（基于关键词重叠）"""
    if not student_answer or student_answer.strip() in ['不知道', '不会', '']:
        return 0
    ref_chars = set(reference)
    stu_chars = set(student_answer)
    overlap = len(ref_chars & stu_chars) / max(len(ref_chars), 1)
    length_ratio = min(len(student_answer) / max(len(reference), 1), 1.0)
    raw = (overlap * 0.6 + length_ratio * 0.4) * full_score
    return round(min(raw * random.uniform(0.85, 1.1), full_score), 1)


def demo_grade_answer(question: str, reference: str, student_answer: str, full_score: float) -> dict:
    """Demo模式：基于规则的智能批阅模拟"""
    time.sleep(0.3)  # 模拟延迟

    if not student_answer or student_answer.strip() in ['不知道', '不会', '']:
        return {
            "score": 0, "error_type": "未作答",
            "comment": "学生未作答或回答内容为空，无法进行评分。建议教师关注该学生是否理解题意。",
            "improvement": "建议从基础概念开始复习，可以先阅读教材中相关章节的基本定义。"
        }

    score = _similarity_score(student_answer, reference, full_score)
    ratio = score / full_score

    if ratio >= 0.85:
        error_type = "完全正确"
        comment = f"回答准确完整，能正确理解并表述「{question[:10]}」的核心概念。知识掌握扎实，表述清晰。"
        improvement = "可以尝试更深入地思考该知识点的延伸应用和跨学科联系。"
    elif ratio >= 0.7:
        error_type = "表述不完整"
        comment = f"基本理解正确，但回答不够完整，遗漏了部分关键要点。建议完善对细节的掌握。"
        improvement = "建议对照教材补充遗漏的知识要点，注意答题的完整性和条理性。"
    elif ratio >= 0.5:
        error_type = "理解偏差"
        comment = f"对核心概念有一定理解，但存在部分偏差。部分表述与参考答案有出入，需要进一步巩固。"
        improvement = "建议重新学习相关知识点，结合具体例子加深理解，避免似是而非的记忆。"
    elif ratio >= 0.25:
        error_type = "概念混淆"
        comment = f"回答体现了部分相关知识，但关键概念存在混淆。可能将不同知识点混为一谈。"
        improvement = "建议制作知识点对比表，厘清易混淆概念之间的区别和联系。"
    else:
        error_type = "知识缺失"
        comment = f"回答内容与正确答案差距较大，该知识点掌握不足，需要系统性地补充学习。"
        improvement = "建议从基础开始系统复习，可以观看相关教学视频或请教老师。"

    return {"score": score, "error_type": error_type, "comment": comment, "improvement": improvement}


def demo_generate_learning_recommendation(student_name: str, weak_points: list) -> str:
    """Demo模式：生成个性化学习推荐"""
    time.sleep(0.5)

    sections = []
    sections.append(f"# 📚 {student_name} 个性化学习方案\n")
    sections.append(f"基于知识诊断结果，为 **{student_name}** 量身定制以下学习建议：\n")

    for wp in weak_points:
        kp = wp['knowledge_point']
        mastery = wp['mastery']
        level = "薄弱" if mastery < 0.6 else "需巩固"

        sections.append(f"## 📌 {kp}（当前掌握度：{mastery:.0%}，{level}）\n")
        sections.append(f"### 1. 核心知识要点回顾")
        sections.append(f"- {kp}是本学科的重要基础概念，理解它需要掌握其定义、原理和应用场景")
        sections.append(f"- 重点关注：概念的准确表述、关键过程的步骤、与其他知识点的联系\n")
        sections.append(f"### 2. 推荐学习资源")
        sections.append(f"- 📖 **教材精读**：重点阅读教材中「{kp}」相关章节，标注关键术语")
        sections.append(f"- 🎬 **微课视频**：搜索「{kp} + 讲解」观看3-5分钟的精讲视频")
        sections.append(f"- 📝 **思维导图**：绘制「{kp}」知识结构图，梳理概念之间的关系\n")
        sections.append(f"### 3. 练习建议")
        sections.append(f"- 完成教材课后练习中与「{kp}」相关的基础题（3-5道）")
        sections.append(f"- 尝试用自己的话向他人讲解「{kp}」（费曼学习法）")
        sections.append(f"- 收集2-3个与「{kp}」相关的生活实例\n")
        sections.append(f"### 4. 学习策略")
        if mastery < 0.4:
            sections.append(f"- ⏰ 建议每天投入 **20分钟** 专项复习")
            sections.append(f"- 采用「理解→记忆→应用」的渐进式学习路径")
        else:
            sections.append(f"- ⏰ 建议每周安排 **2次** 巩固练习")
            sections.append(f"- 采用「查漏→补缺→强化」的针对性学习策略")
        sections.append("")

    sections.append("---\n")
    sections.append("💡 **学习提示**：建议按照薄弱程度从高到低逐个攻克，每完成一个知识点的学习后进行自测。")

    return "\n".join(sections)


def demo_generate_class_summary(class_stats: dict) -> str:
    """Demo模式：生成班级分析总结"""
    time.sleep(0.3)
    total = class_stats.get('total_students', 0)
    avg = class_stats.get('avg_score', 0)
    km = class_stats.get('knowledge_mastery', {})
    et = class_stats.get('error_types', {})

    weak_kps = [k for k, v in km.items() if v < 0.6]
    strong_kps = [k for k, v in km.items() if v >= 0.8]
    top_errors = sorted(et.items(), key=lambda x: -x[1])[:3]

    return f"""## 📊 班级学情分析报告

### 一、整体状况
本班共 **{total}** 名学生参与测评，班级平均得分率为 **{avg:.0%}**。
整体来看，{"大部分学生基础掌握较好" if avg >= 0.7 else "部分知识点仍需加强"}。

### 二、优势与亮点
{f"- 知识点 **{'、'.join(strong_kps)}** 班级掌握良好（达标率≥80%）" if strong_kps else "- 各知识点还需整体提升"}
- 学生整体答题参与度高，无大面积空白卷现象

### 三、薄弱环节
{f"- 知识点 **{'、'.join(weak_kps)}** 是班级共同薄弱项，需要重点复习" if weak_kps else "- 各知识点达标情况尚可"}
- 高频错误类型：{', '.join([f'**{e[0]}**({e[1]}次)' for e in top_errors]) if top_errors else '无明显集中错误'}

### 四、教学改进建议
1. {"针对薄弱知识点安排专项复习课" if weak_kps else "保持当前教学节奏"}
2. 增加课堂练习反馈环节，及时发现和纠正学生的理解偏差
3. 采用分层教学策略，对不同水平的学生提供差异化指导
4. 鼓励学生之间互助学习，发挥优秀学生的带动作用
"""


def grade_answer(client, model: str, question: str, reference: str,
                 student_answer: str, full_score: float) -> dict:
    """
    AI智能批阅单道主观题
    返回: {"score": float, "error_type": str, "comment": str, "improvement": str}
    """
    prompt = f"""你是一位经验丰富的中学教师，请对以下学生的主观题作答进行批阅。

【题目】{question}
【参考答案】{reference}
【学生作答】{student_answer}
【满分】{full_score}分

请严格按照以下JSON格式返回批阅结果（不要输出其他内容）：
{{
    "score": <得分，0到{full_score}之间的数字>,
    "error_type": "<错误类型，从以下选择：概念混淆/知识缺失/表述不完整/理解偏差/完全正确/未作答>",
    "comment": "<详细评语，指出优点和不足，50-100字>",
    "improvement": "<改进建议，针对性的学习建议，30-80字>"
}}"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一位专业的教育评估专家，擅长对学生作答进行精准评价。请始终以JSON格式返回结果。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        content = response.choices[0].message.content.strip()
        # 尝试提取JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        result = json.loads(content)
        # 确保分数在合理范围内
        result["score"] = max(0, min(full_score, float(result.get("score", 0))))
        return result
    except Exception as e:
        return {
            "score": 0,
            "error_type": "评阅异常",
            "comment": f"AI批阅出现异常: {str(e)}",
            "improvement": "请人工复核此题"
        }


def generate_learning_recommendation(client, model: str, student_name: str,
                                      weak_points: list) -> str:
    """
    根据学生的薄弱知识点生成个性化学习推荐
    weak_points: [{"knowledge_point": str, "mastery": float, "errors": str}]
    """
    points_desc = "\n".join([
        f"- {p['knowledge_point']}：掌握度{p['mastery']:.0%}，主要问题：{p['errors']}"
        for p in weak_points
    ])

    prompt = f"""你是一位教育AI助手，请根据以下学生的知识诊断结果，生成个性化学习建议。

【学生】{student_name}
【薄弱知识点分析】
{points_desc}

请针对每个薄弱知识点，提供：
1. 核心知识要点回顾
2. 推荐的学习资源类型（如微课视频、教材章节、练习题等）
3. 具体的练习建议
4. 学习策略提示

请用清晰的结构化文本输出，使用 Markdown 格式。"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一位专业的教育技术顾问，擅长基于学习分析数据为学生制定个性化学习方案。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"生成学习推荐时出现异常: {str(e)}"


def generate_class_summary(client, model: str, class_stats: dict) -> str:
    """
    生成班级整体分析总结
    """
    prompt = f"""你是一位教育数据分析专家，请根据以下班级作答统计数据，撰写一份简洁的班级分析报告。

【班级统计数据】
- 学生总数：{class_stats.get('total_students', 0)}
- 平均分：{class_stats.get('avg_score', 0):.1f}
- 最高分：{class_stats.get('max_score', 0):.1f}
- 最低分：{class_stats.get('min_score', 0):.1f}
- 各知识点达标率：{json.dumps(class_stats.get('knowledge_mastery', {}), ensure_ascii=False)}
- 高频错误类型：{json.dumps(class_stats.get('error_types', {}), ensure_ascii=False)}

请从以下角度分析：
1. 班级整体学习状况概述
2. 突出的优势与亮点
3. 需要关注的薄弱环节
4. 教学改进建议

用 Markdown 格式输出，简洁专业，200字左右。"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一位教育数据分析专家。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"生成班级分析时出现异常: {str(e)}"
