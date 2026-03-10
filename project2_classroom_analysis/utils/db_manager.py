"""
数据库管理模块 - 课堂互动分析数据存储
"""
import sqlite3
import os
import json
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "classroom.db")


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classroom_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_name TEXT NOT NULL,
            subject TEXT,
            grade TEXT,
            teacher_name TEXT,
            total_turns INTEGER DEFAULT 0,
            teacher_turns INTEGER DEFAULT 0,
            student_turns INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dialogue_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            turn_number INTEGER,
            role TEXT,
            content TEXT,
            FOREIGN KEY (session_id) REFERENCES classroom_sessions(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            analysis_type TEXT,
            result_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES classroom_sessions(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reflection_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            report_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES classroom_sessions(id)
        )
    """)

    conn.commit()
    conn.close()


def save_session(session_name, subject, grade, teacher_name, dialogues: list):
    """
    保存课堂记录
    dialogues: [{"role": "教师"/"学生", "content": "..."}]
    """
    conn = get_connection()
    cursor = conn.cursor()

    teacher_turns = sum(1 for d in dialogues if d['role'] == '教师')
    student_turns = sum(1 for d in dialogues if d['role'] == '学生')

    cursor.execute("""
        INSERT INTO classroom_sessions 
        (session_name, subject, grade, teacher_name, total_turns, teacher_turns, student_turns)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_name, subject, grade, teacher_name, len(dialogues), teacher_turns, student_turns))

    session_id = cursor.lastrowid

    for idx, d in enumerate(dialogues):
        cursor.execute("""
            INSERT INTO dialogue_records (session_id, turn_number, role, content)
            VALUES (?, ?, ?, ?)
        """, (session_id, idx + 1, d['role'], d['content']))

    conn.commit()
    conn.close()
    return session_id


def get_all_sessions():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM classroom_sessions ORDER BY created_at DESC", conn)
    conn.close()
    return df


def get_session_dialogues(session_id):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM dialogue_records WHERE session_id = ? ORDER BY turn_number",
        conn, params=(session_id,))
    conn.close()
    return df


def get_session_info(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM classroom_sessions WHERE id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_analysis_result(session_id, analysis_type, result_data: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analysis_results (session_id, analysis_type, result_data)
        VALUES (?, ?, ?)
    """, (session_id, analysis_type, json.dumps(result_data, ensure_ascii=False)))
    conn.commit()
    conn.close()


def get_analysis_result(session_id, analysis_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT result_data FROM analysis_results 
        WHERE session_id = ? AND analysis_type = ?
        ORDER BY created_at DESC LIMIT 1
    """, (session_id, analysis_type))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row['result_data'])
    return None


def save_reflection_report(session_id, report_content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO reflection_reports (session_id, report_content)
        VALUES (?, ?)
    """, (session_id, report_content))
    conn.commit()
    conn.close()


def get_reflection_report(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM reflection_reports WHERE session_id = ?
        ORDER BY created_at DESC LIMIT 1
    """, (session_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_analysis_for_comparison():
    """获取所有session的分析结果用于对比"""
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT cs.id, cs.session_name, cs.created_at, cs.teacher_turns, cs.student_turns,
               cs.total_turns, ar.analysis_type, ar.result_data
        FROM classroom_sessions cs
        LEFT JOIN analysis_results ar ON cs.id = ar.session_id
        ORDER BY cs.created_at
    """, conn)
    conn.close()
    return df


def delete_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM reflection_reports WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM analysis_results WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM dialogue_records WHERE session_id = ?", (session_id,))
    cursor.execute("DELETE FROM classroom_sessions WHERE id = ?", (session_id,))
    conn.commit()
    conn.close()
