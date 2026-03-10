"""
数据库管理模块 - 使用 SQLite 存储作答数据与批阅结果
"""
import sqlite3
import os
import json
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "diagnosis.db")


def get_connection():
    """获取数据库连接"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            question_id TEXT,
            question_content TEXT,
            knowledge_point TEXT,
            student_answer TEXT,
            reference_answer TEXT,
            full_score REAL DEFAULT 10,
            upload_batch TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS grading_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            answer_id INTEGER,
            score REAL,
            error_type TEXT,
            comment TEXT,
            improvement TEXT,
            graded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (answer_id) REFERENCES student_answers(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT,
            knowledge_point TEXT,
            mastery_level REAL,
            recommendation TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_answers(df: pd.DataFrame, batch_id: str):
    """保存上传的作答数据"""
    conn = get_connection()
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO student_answers 
            (student_name, question_id, question_content, knowledge_point,
             student_answer, reference_answer, full_score, upload_batch)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row.get('学生姓名', ''),
            str(row.get('题目编号', '')),
            row.get('题目内容', ''),
            row.get('所属知识点', ''),
            row.get('学生作答', ''),
            row.get('参考答案', ''),
            row.get('满分', 10),
            batch_id
        ))
    conn.commit()
    conn.close()


def get_all_answers():
    """获取所有作答记录"""
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM student_answers ORDER BY student_name, question_id", conn)
    conn.close()
    return df


def get_ungraded_answers():
    """获取未批阅的作答"""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT sa.* FROM student_answers sa
        LEFT JOIN grading_results gr ON sa.id = gr.answer_id
        WHERE gr.id IS NULL
        ORDER BY sa.student_name, sa.question_id
    """, conn)
    conn.close()
    return df


def save_grading_result(answer_id, score, error_type, comment, improvement):
    """保存批阅结果"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO grading_results (answer_id, score, error_type, comment, improvement)
        VALUES (?, ?, ?, ?, ?)
    """, (answer_id, score, error_type, comment, improvement))
    conn.commit()
    conn.close()


def get_grading_results():
    """获取所有批阅结果（关联作答数据）"""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT sa.student_name, sa.question_id, sa.question_content,
               sa.knowledge_point, sa.student_answer, sa.reference_answer,
               sa.full_score, gr.score, gr.error_type, gr.comment, gr.improvement
        FROM student_answers sa
        JOIN grading_results gr ON sa.id = gr.answer_id
        ORDER BY sa.student_name, sa.question_id
    """, conn)
    conn.close()
    return df


def save_recommendation(student_name, knowledge_point, mastery_level, recommendation):
    """保存学习推荐"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO learning_recommendations 
        (student_name, knowledge_point, mastery_level, recommendation)
        VALUES (?, ?, ?, ?)
    """, (student_name, knowledge_point, mastery_level, recommendation))
    conn.commit()
    conn.close()


def get_recommendations(student_name=None):
    """获取学习推荐"""
    conn = get_connection()
    if student_name:
        df = pd.read_sql_query(
            "SELECT * FROM learning_recommendations WHERE student_name = ? ORDER BY mastery_level",
            conn, params=(student_name,))
    else:
        df = pd.read_sql_query("SELECT * FROM learning_recommendations ORDER BY student_name, mastery_level", conn)
    conn.close()
    return df


def clear_all_data():
    """清空所有数据"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM learning_recommendations")
    cursor.execute("DELETE FROM grading_results")
    cursor.execute("DELETE FROM student_answers")
    conn.commit()
    conn.close()
