"""
数据处理模块 - 数据清洗、统计分析
"""
import pandas as pd
import numpy as np


def validate_upload_data(df: pd.DataFrame) -> tuple:
    """
    验证上传数据格式
    返回: (is_valid: bool, message: str)
    """
    required_columns = ['学生姓名', '题目编号', '题目内容', '所属知识点', '学生作答', '参考答案']
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        return False, f"缺少必要列: {', '.join(missing)}"

    if df.empty:
        return False, "数据为空"

    if '满分' not in df.columns:
        df['满分'] = 10

    return True, "数据格式验证通过"


def compute_student_knowledge_mastery(grading_df: pd.DataFrame) -> pd.DataFrame:
    """
    计算每个学生在各知识点的掌握度
    返回: DataFrame with columns [student_name, knowledge_point, score_rate, error_types]
    """
    if grading_df.empty:
        return pd.DataFrame()

    result = grading_df.groupby(['student_name', 'knowledge_point']).agg(
        total_score=('score', 'sum'),
        total_full=('full_score', 'sum'),
        error_types=('error_type', lambda x: ', '.join(set(x.dropna())))
    ).reset_index()

    result['score_rate'] = result['total_score'] / result['total_full'].replace(0, 1)
    result['score_rate'] = result['score_rate'].clip(0, 1)

    return result


def compute_class_stats(grading_df: pd.DataFrame) -> dict:
    """
    计算班级整体统计数据
    """
    if grading_df.empty:
        return {}

    # 每个学生的总得分率
    student_scores = grading_df.groupby('student_name').agg(
        total_score=('score', 'sum'),
        total_full=('full_score', 'sum')
    ).reset_index()
    student_scores['score_rate'] = student_scores['total_score'] / student_scores['total_full'].replace(0, 1)

    # 各知识点达标率（得分率>=60%算达标）
    kp_mastery = grading_df.groupby('knowledge_point').agg(
        avg_rate=('score', lambda x: x.sum() / grading_df.loc[x.index, 'full_score'].sum())
    ).reset_index()
    knowledge_mastery = dict(zip(kp_mastery['knowledge_point'], kp_mastery['avg_rate']))

    # 错误类型统计
    error_counts = grading_df['error_type'].value_counts().to_dict()

    return {
        'total_students': student_scores.shape[0],
        'avg_score': student_scores['score_rate'].mean(),
        'max_score': student_scores['score_rate'].max(),
        'min_score': student_scores['score_rate'].min(),
        'student_scores': student_scores,
        'knowledge_mastery': knowledge_mastery,
        'error_types': error_counts
    }


def get_student_weak_points(mastery_df: pd.DataFrame, student_name: str,
                             threshold: float = 0.8) -> list:
    """
    获取学生的薄弱知识点
    """
    student_data = mastery_df[mastery_df['student_name'] == student_name]
    weak = student_data[student_data['score_rate'] < threshold]

    return [
        {
            'knowledge_point': row['knowledge_point'],
            'mastery': row['score_rate'],
            'errors': row['error_types']
        }
        for _, row in weak.iterrows()
    ]
