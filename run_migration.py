"""
Run a .sql migration file against the DB configured in .env, using the
same mysql-connector-python driver the app itself already depends on.
Sidesteps needing the `mysql` CLI on PATH.

Usage:
    python run_migration.py sql\04_phase1_expansion.sql
    python run_migration.py sql\05_phase2_expansion.sql
"""

import sys
import os
import re
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

if len(sys.argv) != 2:
    print("Usage: python run_migration.py <path_to_sql_file>")
    sys.exit(1)

sql_path = sys.argv[1]
if not os.path.exists(sql_path):
    print(f"File not found: {sql_path}")
    sys.exit(1)

with open(sql_path, "r", encoding="utf-8") as f:
    raw_sql = f.read()

lines = [line for line in raw_sql.splitlines() if not line.strip().startswith("--")]
cleaned = "\n".join(lines)
statements = [s.strip() for s in cleaned.split(";") if s.strip()]

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "dalal_street_pro"),
)
cursor = conn.cursor()

print(f"Running {len(statements)} statement(s) from {sql_path} ...")
ok, failed = 0, 0
for i, stmt in enumerate(statements, 1):
    preview = re.sub(r"\s+", " ", stmt)[:80]
    try:
        cursor.execute(stmt)
        conn.commit()
        print(f"  [{i}/{len(statements)}] OK: {preview}...")
        ok += 1
    except mysql.connector.Error as e:
        if e.errno in (1060, 1061, 1050):
            print(f"  [{i}/{len(statements)}] SKIP (already applied): {preview}...")
            ok += 1
        else:
            print(f"  [{i}/{len(statements)}] FAILED: {preview}...")
            print(f"      -> {e}")
            failed += 1

cursor.close()
conn.close()
print(f"\nDone: {ok} succeeded/skipped, {failed} failed.")
if failed:
    sys.exit(1)
