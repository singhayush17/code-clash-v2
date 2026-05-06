"""
Verify that multi-column ORDER BY exercises actually require
all sort columns to produce the correct result.

For each task with ORDER BY x, y (or more), check:
1. Does the result set have ties in column x that require y to disambiguate?
2. Would ORDER BY x alone (dropping y) produce an ambiguous/different result?
"""

import sys
import os
import re
import sqlite3

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.sql_practice import LESSONS, build_connection, split_sql, is_result_statement


def extract_order_columns(sql: str) -> list[str] | None:
    """Extract the ORDER BY clause columns from a SQL statement."""
    match = re.search(r'\bORDER\s+BY\s+(.+?)(?:\s+LIMIT\s+|\s*;?\s*$)', sql, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    clause = match.group(1).strip().rstrip(';')
    # Split by comma, but be careful with nested parens
    parts = []
    depth = 0
    current = []
    for ch in clause:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == ',' and depth == 0:
            parts.append(''.join(current).strip())
            current = []
            continue
        current.append(ch)
    parts.append(''.join(current).strip())
    return parts


def run_query(conn_factory, sql: str):
    """Run a SQL query and return (columns, rows)."""
    conn = conn_factory()
    try:
        statements = split_sql(sql)
        for stmt in statements[:-1]:
            conn.executescript(stmt + ";")
        final = statements[-1]
        if is_result_statement(final):
            cursor = conn.execute(final)
            columns = [d[0] for d in cursor.description or []]
            rows = [tuple(row) for row in cursor.fetchall()]
            return columns, rows
        else:
            conn.executescript(final + ";")
            return [], []
    finally:
        conn.close()


def strip_order_by(sql: str) -> str:
    """Remove ORDER BY clause from SQL."""
    return re.sub(r'\bORDER\s+BY\s+.+?(?=\s+LIMIT\s+|\s*;?\s*$)', '', sql, flags=re.IGNORECASE | re.DOTALL)


def modify_order_by(sql: str, new_order: str) -> str:
    """Replace ORDER BY clause in SQL."""
    return re.sub(
        r'\bORDER\s+BY\s+.+?(?=\s+LIMIT\s+|\s*;?\s*$)',
        f'ORDER BY {new_order}',
        sql,
        flags=re.IGNORECASE | re.DOTALL,
    )


def check_task(lesson, task):
    """Check if multi-column ORDER BY is necessary for this task."""
    solution = task.solution
    order_cols = extract_order_columns(solution)

    if not order_cols or len(order_cols) < 2:
        return None  # Single or no ORDER BY - nothing to check

    # Run the full solution
    try:
        full_cols, full_rows = run_query(build_connection, solution)
    except Exception as e:
        return {"task": task.id, "error": f"Solution failed: {e}"}

    if len(full_rows) <= 1:
        return None  # 0-1 rows, ordering doesn't matter

    issues = []

    # Check: does ORDER BY with only the first column produce the same result?
    first_col_only = order_cols[0]
    try:
        modified_sql = modify_order_by(solution, first_col_only)
        _, partial_rows = run_query(build_connection, modified_sql)

        if partial_rows == full_rows:
            issues.append(
                f"ORDER BY {first_col_only} alone produces the same result as "
                f"ORDER BY {', '.join(order_cols)}. "
                f"Secondary sort column(s) [{', '.join(order_cols[1:])}] are unnecessary."
            )
    except Exception:
        pass

    # For each pair of adjacent sort columns, check if there are ties
    # that require the next column
    # Find which result columns correspond to order columns
    for i, col_expr in enumerate(order_cols[:-1]):
        next_col = order_cols[i + 1]
        # Try dropping this specific secondary column and all after it
        partial_order = ', '.join(order_cols[:i + 1])
        try:
            modified_sql = modify_order_by(solution, partial_order)
            _, partial_rows = run_query(build_connection, modified_sql)
            if partial_rows == full_rows:
                remaining = order_cols[i + 1:]
                issues.append(
                    f"ORDER BY {partial_order} is sufficient. "
                    f"Column(s) [{', '.join(remaining)}] don't affect ordering."
                )
                break  # No need to check further
        except Exception:
            pass

    # Check: would wrong direction on first column still produce same result?
    first_clean = order_cols[0].strip()
    if ' DESC' in first_clean.upper():
        flipped = re.sub(r'\s+DESC\b', '', first_clean, flags=re.IGNORECASE)
    else:
        flipped = first_clean.split()[0] + ' DESC' if first_clean.split() else first_clean
    try:
        wrong_order = ', '.join([flipped] + order_cols[1:])
        modified_sql = modify_order_by(solution, wrong_order)
        _, wrong_rows = run_query(build_connection, modified_sql)
        if wrong_rows == full_rows:
            issues.append(
                f"WRONG direction on first column ({flipped} instead of {order_cols[0]}) "
                f"produces the same result! The sort direction doesn't matter."
            )
    except Exception:
        pass

    if issues:
        return {
            "lesson": f"{lesson.id} (Ch {lesson.number}: {lesson.title})",
            "task": task.id,
            "prompt": task.prompt,
            "solution_order": f"ORDER BY {', '.join(order_cols)}",
            "rows": len(full_rows),
            "issues": issues,
        }
    return None


def main():
    print("=" * 80)
    print("VERIFYING MULTI-COLUMN ORDER BY EXERCISES")
    print("=" * 80)

    total_checked = 0
    problems = []

    for lesson in LESSONS:
        for task in lesson.tasks:
            order_cols = extract_order_columns(task.solution)
            if not order_cols or len(order_cols) < 2:
                continue

            total_checked += 1
            result = check_task(lesson, task)
            if result:
                problems.append(result)

    print(f"\nChecked {total_checked} exercises with multi-column ORDER BY.\n")

    if not problems:
        print("All exercises have meaningful multi-column ordering!")
    else:
        print(f"Found {len(problems)} exercises with unnecessary sort columns:\n")
        for i, p in enumerate(problems, 1):
            print(f"{'─' * 70}")
            print(f"  [{i}] {p['lesson']}")
            print(f"      Task: {p['task']}")
            print(f"      Prompt: {p['prompt']}")
            print(f"      {p['solution_order']} ({p['rows']} rows)")
            for issue in p['issues']:
                print(f"      ⚠ {issue}")
        print(f"{'─' * 70}")

    return len(problems)


if __name__ == "__main__":
    sys.exit(main())
