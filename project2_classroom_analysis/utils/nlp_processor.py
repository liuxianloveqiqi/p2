"""
NLP处理模块 - 中文分词、话语分析
"""
import jieba
import re
from collections import Counter


# 停用词表（常见中文停用词）
STOP_WORDS = set([
    '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一',
    '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着',
    '没有', '看', '好', '自己', '这', '他', '她', '它', '们', '那', '些',
    '什么', '怎么', '为什么', '哪', '吗', '呢', '吧', '啊', '呀', '哦',
    '嗯', '噢', '哈', '嘛', '哇', '唉', '对', '请', '把', '被', '从',
    '用', '来', '去', '过', '给', '让', '跟', '比', '而', '但', '但是',
    '如果', '因为', '所以', '虽然', '可是', '然后', '这个', '那个',
    '大家', '同学们', '同学', '老师', '大', '小', '多', '少', '能',
    '可以', '还', '又', '再', '已经', '正在', '可能', '应该', '不是',
    '下面', '现在', '今天', '我们', '你们', '他们', '非常', '得',
    '地', '之', '与', '及', '等', '以', '于', '或', '其', '更',
    '最', '此', '每', '各', '第', '做', '想', '知道', '觉得',
])


def parse_dialogue_text(text: str) -> list:
    """
    解析对话文本，自动区分教师和学生话语
    支持格式：
    - "教师: 内容" / "学生: 内容"
    - "教师：内容" / "学生：内容"
    - "T: 内容" / "S: 内容"
    """
    dialogues = []
    lines = text.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 匹配角色
        match = re.match(r'^(教师|老师|Teacher|T|teacher)\s*[:：]\s*(.+)', line, re.IGNORECASE)
        if match:
            dialogues.append({'role': '教师', 'content': match.group(2).strip()})
            continue

        match = re.match(r'^(学生|Student|S|student)\s*[:：]\s*(.+)', line, re.IGNORECASE)
        if match:
            dialogues.append({'role': '学生', 'content': match.group(2).strip()})
            continue

        # 无法识别的行跳过
        if dialogues:
            # 追加到最后一个对话
            dialogues[-1]['content'] += ' ' + line

    return dialogues


def compute_talk_ratio(dialogues: list) -> dict:
    """
    计算师生话语比例
    """
    teacher_words = sum(len(d['content']) for d in dialogues if d['role'] == '教师')
    student_words = sum(len(d['content']) for d in dialogues if d['role'] == '学生')
    total_words = teacher_words + student_words

    teacher_turns = sum(1 for d in dialogues if d['role'] == '教师')
    student_turns = sum(1 for d in dialogues if d['role'] == '学生')

    return {
        'teacher_words': teacher_words,
        'student_words': student_words,
        'total_words': total_words,
        'teacher_word_ratio': teacher_words / max(total_words, 1),
        'student_word_ratio': student_words / max(total_words, 1),
        'teacher_turns': teacher_turns,
        'student_turns': student_turns,
        'teacher_turn_ratio': teacher_turns / max(teacher_turns + student_turns, 1),
        'student_turn_ratio': student_turns / max(teacher_turns + student_turns, 1),
        'avg_teacher_length': teacher_words / max(teacher_turns, 1),
        'avg_student_length': student_words / max(student_turns, 1),
    }


def extract_teacher_questions(dialogues: list) -> list:
    """
    提取教师提问
    """
    questions = []
    for d in dialogues:
        if d['role'] == '教师':
            # 匹配中文问句
            sentences = re.split(r'[。！!]', d['content'])
            for s in sentences:
                s = s.strip()
                if '？' in s or '?' in s or any(q in s for q in ['什么', '怎么', '为什么', '哪', '吗', '是否', '能否', '请']):
                    if len(s) > 3:
                        questions.append(s.replace('？', '').replace('?', '').strip())
    return questions


def _classify_third_turn(content: str) -> str:
    """
        判断教师第三轮话语应归为 IRE 还是 IRF。
        判定优先级：
      1. 含有问号 → F（最强信号：明确追问）
      2. 含有疑问词（作为实际提问使用）→ F
      3. 含有延续/引导词 → F
      4. 否则为终止性评价 → E

    返回值统一为完整模式标签（IRE/IRF），
    与页面统计逻辑保持一致，避免出现“全0”计数。
    """
    # 信号1：含问号 → 必然是追问，IRF
    if '？' in content or '?' in content:
        return 'IRF'

    # 信号2：含疑问词（排除固定短语"什么是"之类的陈述性用法）
    question_words = ['什么', '怎么', '为什么', '哪些', '哪', '如何', '几个', '多少', '是否', '能否']
    if any(qw in content for qw in question_words):
        return 'IRF'

    # 信号3：含延续/引导词 → IRF
    continuation_words = ['还有', '那么', '进一步', '继续', '接下来', '下一步', '再想想',
                          '能不能', '可不可以', '谁来', '哪位', '请同学', '我们来', '试着']
    if any(cw in content for cw in continuation_words):
        return 'IRF'

    # 默认：终止性评价 → IRE
    return 'IRE'


def normalize_pattern_type(pattern_type: str) -> str:
    """
    统一模式类型标签，兼容历史版本中的 E/F 写法。
    """
    mapping = {
        'E': 'IRE',
        'F': 'IRF',
        'IRE': 'IRE',
        'IRF': 'IRF',
        'IR': 'IR',
    }
    return mapping.get(pattern_type, pattern_type)


def count_interaction_pattern_types(patterns: list) -> dict:
    """
    统计 IRE/IRF/IR 数量，并对历史类型标签做兼容。
    """
    normalized = [normalize_pattern_type(p.get('type', '')) for p in patterns]
    return {
        'ire_count': sum(1 for t in normalized if t == 'IRE'),
        'irf_count': sum(1 for t in normalized if t == 'IRF'),
        'ir_count': sum(1 for t in normalized if t == 'IR'),
    }


def analyze_ire_patterns(dialogues: list) -> list:
    """
    分析IRE/IRF互动模式
    I: Initiation (教师发起)
    R: Response (学生回应)
    E: Evaluation / F: Feedback (教师评价/反馈)
    """
    patterns = []
    i = 0
    while i < len(dialogues):
        if dialogues[i]['role'] == '教师':
            pattern = {'I': dialogues[i]['content'], 'R': [], 'E': None, 'type': 'incomplete'}

            # 查找学生回应
            j = i + 1
            while j < len(dialogues) and dialogues[j]['role'] == '学生':
                pattern['R'].append(dialogues[j]['content'])
                j += 1

            # 查找教师评价/反馈
            if j < len(dialogues) and dialogues[j]['role'] == '教师' and pattern['R']:
                content = dialogues[j]['content']
                pattern['E'] = content
                pattern['type'] = normalize_pattern_type(_classify_third_turn(content))

                i = j
                patterns.append(pattern)
                continue
            elif pattern['R']:
                pattern['type'] = 'IR'
                patterns.append(pattern)

        i += 1

    return patterns


def segment_and_count(texts: list, top_n: int = 50) -> list:
    """
    中文分词并统计词频
    返回: [(word, count), ...]
    """
    all_words = []
    for text in texts:
        words = jieba.cut(text)
        for w in words:
            w = w.strip()
            if len(w) >= 2 and w not in STOP_WORDS and not w.isdigit():
                all_words.append(w)

    counter = Counter(all_words)
    return counter.most_common(top_n)


def compute_interaction_metrics(dialogues: list) -> dict:
    """
    综合计算课堂互动指标
    """
    talk_ratio = compute_talk_ratio(dialogues)
    questions = extract_teacher_questions(dialogues)
    ire_patterns = analyze_ire_patterns(dialogues)
    pattern_counts = count_interaction_pattern_types(ire_patterns)

    return {
        **talk_ratio,
        'question_count': len(questions),
        'questions': questions,
        'ire_count': pattern_counts['ire_count'],
        'irf_count': pattern_counts['irf_count'],
        'ir_count': pattern_counts['ir_count'],
        'total_patterns': len(ire_patterns),
        'patterns': ire_patterns,
        'teacher_dominance': talk_ratio['teacher_word_ratio'],
    }
