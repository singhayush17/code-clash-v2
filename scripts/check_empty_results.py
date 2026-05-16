"""Find exercises whose solution returns 0 rows against the seed data."""
import sqlite3, sys, importlib, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.sql_practice import LESSONS, SEED, SCHEMA

def build_db():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    for table, rows in SEED.items():
        if not rows:
            continue
        placeholders = ", ".join(["?"] * len(rows[0]))
        for row in rows:
            conn.execute(f"INSERT INTO {table} VALUES ({placeholders})", row)
    conn.commit()
    return conn

def check_all():
    conn = build_db()
    empty = []
    errors = []
    for lesson in LESSONS:
        for i, task in enumerate(lesson.tasks, 1):
            sol = task.solution.strip()
            if not sol:
                continue
            # Skip DDL tasks that create/alter/drop (they won't return rows)
            upper = sol.upper()
            if any(upper.startswith(kw) for kw in ("CREATE", "ALTER", "DROP", "INSERT", "UPDATE", "DELETE")):
                continue
            # For multi-statement solutions, only check if the last statement is a SELECT
            stmts = [s.strip() for s in sol.split(";") if s.strip()]
            last = stmts[-1].upper() if stmts else ""
            if not last.startswith("SELECT") and not last.startswith("WITH"):
                continue
            try:
                # Execute in a fresh connection to avoid side effects
                test_conn = build_db()
                # Execute any setup statements first
                for s in stmts[:-1]:
                    test_conn.execute(s)
                cursor = test_conn.execute(stmts[-1])
                rows = cursor.fetchall()
                if len(rows) == 0:
                    empty.append((lesson.id, lesson.title, i, task.id, task.prompt[:80]))
                test_conn.close()
            except Exception as e:
                errors.append((lesson.id, i, task.id, str(e)[:80]))

    conn.close()

    print("=" * 80)
    print(f"EXERCISES WITH 0 RESULT ROWS ({len(empty)} found)")
    print("=" * 80)
    for lid, ltitle, idx, tid, prompt in empty:
        print(f"\n  Chapter: {ltitle} ({lid})")
        print(f"  Task #{idx}: {tid}")
        print(f"  Prompt: {prompt}...")

    if errors:
        print(f"\n\nERRORS ({len(errors)}):")
        for lid, idx, tid, err in errors:
            print(f"  {lid} #{idx} ({tid}): {err}")

    if not empty:
        print("\n  ✅ All exercises return at least 1 row!")

    return len(empty)

if __name__ == "__main__":
    sys.exit(check_all())
