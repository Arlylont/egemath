import json

import db


def load_tasks():
    db.init()
    db.conn.execute("DELETE FROM tasks")

    tasks = json.load(open("tasks.json", encoding="utf-8"))
    for t in tasks:
        options = json.dumps(t["options"], ensure_ascii=False) if t.get("options") else None
        db.conn.execute(
            "INSERT INTO tasks (task_number, variant_number, part, question, options, answer, solution) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (t["task_number"], t["variant_number"], t["part"], t["question"],
             options, str(t["answer"]), t.get("solution", "")),
        )
    db.conn.commit()
    print(f"Загружено заданий: {len(tasks)}")


if __name__ == "__main__":
    load_tasks()
