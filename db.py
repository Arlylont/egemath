import sqlite3
import json
from datetime import date, timedelta

from config import DB_PATH, FREE_PRACTICE, FREE_VARIANTS

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.row_factory = sqlite3.Row


def init():
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_number INTEGER,
        variant_number INTEGER,
        part INTEGER,
        question TEXT,
        options TEXT,
        answer TEXT,
        solution TEXT
    );
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        name TEXT,
        sub_until TEXT
    );
    CREATE TABLE IF NOT EXISTS limits (
        user_id INTEGER,
        day TEXT,
        variants INTEGER DEFAULT 0,
        practice INTEGER DEFAULT 0,
        PRIMARY KEY (user_id, day)
    );
    CREATE TABLE IF NOT EXISTS attempts (
        user_id INTEGER,
        day TEXT,
        correct INTEGER
    );
    """)
    conn.commit()


def add_user(user_id, name):
    conn.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()


def get_user(user_id):
    return conn.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()


def is_subscribed(user_id):
    u = get_user(user_id)
    if not u or not u["sub_until"]:
        return False
    return u["sub_until"] >= date.today().isoformat()


def give_subscription(user_id, days):
    u = get_user(user_id)
    today = date.today()
    if u and u["sub_until"] and u["sub_until"] >= today.isoformat():
        start = date.fromisoformat(u["sub_until"])
    else:
        start = today
    until = (start + timedelta(days=days)).isoformat()
    conn.execute("UPDATE users SET sub_until = ? WHERE user_id = ?", (until, user_id))
    conn.commit()
    return until


def task_numbers():
    rows = conn.execute("SELECT DISTINCT task_number FROM tasks ORDER BY task_number").fetchall()
    return [r["task_number"] for r in rows]


def random_task(task_number):
    row = conn.execute(
        "SELECT * FROM tasks WHERE task_number = ? ORDER BY RANDOM() LIMIT 1", (task_number,)
    ).fetchone()
    return _to_dict(row)


def full_variant():
    tasks = []
    for n in task_numbers():
        t = random_task(n)
        if t:
            tasks.append(t)
    return tasks


def get_task(task_id):
    return _to_dict(conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone())


def _to_dict(row):
    if not row:
        return None
    t = dict(row)
    t["options"] = json.loads(t["options"]) if t["options"] else None
    return t


def seed_if_empty():
    if conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] > 0:
        return
    for t in json.load(open("tasks.json", encoding="utf-8")):
        options = json.dumps(t["options"], ensure_ascii=False) if t.get("options") else None
        conn.execute(
            "INSERT INTO tasks (task_number, variant_number, part, question, options, answer, solution) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (t["task_number"], t["variant_number"], t["part"], t["question"],
             options, str(t["answer"]), t.get("solution", "")),
        )
    conn.commit()


def norm(s):
    return str(s).strip().replace(",", ".").lower()


def _limit_row(user_id):
    today = date.today().isoformat()
    conn.execute("INSERT OR IGNORE INTO limits (user_id, day) VALUES (?, ?)", (user_id, today))
    conn.commit()
    return conn.execute("SELECT * FROM limits WHERE user_id = ? AND day = ?", (user_id, today)).fetchone()


def practice_left(user_id):
    if is_subscribed(user_id):
        return -1
    return FREE_PRACTICE - _limit_row(user_id)["practice"]


def variant_left(user_id):
    if is_subscribed(user_id):
        return -1
    return FREE_VARIANTS - _limit_row(user_id)["variants"]


def use_practice(user_id):
    today = date.today().isoformat()
    _limit_row(user_id)
    conn.execute("UPDATE limits SET practice = practice + 1 WHERE user_id = ? AND day = ?", (user_id, today))
    conn.commit()


def use_variant(user_id):
    today = date.today().isoformat()
    _limit_row(user_id)
    conn.execute("UPDATE limits SET variants = variants + 1 WHERE user_id = ? AND day = ?", (user_id, today))
    conn.commit()


def add_attempt(user_id, correct):
    conn.execute("INSERT INTO attempts (user_id, day, correct) VALUES (?, ?, ?)",
                 (user_id, date.today().isoformat(), 1 if correct else 0))
    conn.commit()


def stats():
    today = date.today().isoformat()
    users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    subs = conn.execute("SELECT COUNT(*) FROM users WHERE sub_until >= ?", (today,)).fetchone()[0]
    attempts = conn.execute("SELECT COUNT(*) FROM attempts WHERE day = ?", (today,)).fetchone()[0]
    return {"users": users, "subs": subs, "attempts_today": attempts}
