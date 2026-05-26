import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'n1_test.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section TEXT NOT NULL,
            q_type TEXT NOT NULL,
            question_text TEXT NOT NULL,
            options TEXT NOT NULL,
            answer INTEGER NOT NULL,
            explanation TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exam_date TEXT NOT NULL,
            mode TEXT NOT NULL,
            score INTEGER NOT NULL,
            total INTEGER NOT NULL,
            correct INTEGER NOT NULL,
            duration_seconds INTEGER DEFAULT 0,
            details TEXT DEFAULT '[]'
        );
        """)
        conn.commit()


def add_question(section, q_type, question_text, options, answer, explanation=''):
    with get_db() as conn:
        conn.execute(
            "INSERT INTO questions (section, q_type, question_text, options, answer, explanation) VALUES (?,?,?,?,?,?)",
            (section, q_type, question_text, options, answer, explanation)
        )
        conn.commit()


def get_questions_by_section(section, limit=None):
    with get_db() as conn:
        if limit:
            rows = conn.execute(
                "SELECT * FROM questions WHERE section=? ORDER BY RANDOM() LIMIT ?",
                (section, limit)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM questions WHERE section=? ORDER BY RANDOM()",
                (section,)
            ).fetchall()
        return [dict(r) for r in rows]


def get_exam_questions():
    """Assemble a full mock exam matching N1 structure."""
    config = [
        ('vocab', 'yomikata', 6),
        ('vocab', 'context', 7),
        ('vocab', 'paraphrase', 6),
        ('vocab', 'usage', 6),
        ('grammar', 'form', 10),
        ('grammar', 'order', 5),
        ('grammar', 'text_grammar', 5),
        ('reading', 'short', 4),
        ('reading', 'medium', 9),
        ('reading', 'long', 4),
        ('reading', 'integrated', 3),
        ('reading', 'opinion', 4),
        ('reading', 'search', 2),
    ]
    questions = []
    with get_db() as conn:
        for section, q_type, count in config:
            rows = conn.execute(
                "SELECT * FROM questions WHERE section=? AND q_type=? ORDER BY RANDOM() LIMIT ?",
                (section, q_type, count)
            ).fetchall()
            questions.extend([dict(r) for r in rows])
    return questions


def get_question_count():
    with get_db() as conn:
        r = conn.execute("SELECT COUNT(*) as c FROM questions").fetchone()
        return r['c']


def save_result(mode, score, total, correct, duration_seconds, details):
    from datetime import datetime
    with get_db() as conn:
        conn.execute(
            "INSERT INTO results (exam_date, mode, score, total, correct, duration_seconds, details) VALUES (?,?,?,?,?,?,?)",
            (datetime.now().isoformat(), mode, score, total, correct, duration_seconds, details)
        )
        conn.commit()


def get_history(limit=20):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM results ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def get_result(result_id):
    with get_db() as conn:
        r = conn.execute("SELECT * FROM results WHERE id=?", (result_id,)).fetchone()
        return dict(r) if r else None
