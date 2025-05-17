import json
from pathlib import Path

DB_FILE = Path("db/users.json")

def read_users_from_db():
    if not DB_FILE.exists():
        return []
    with DB_FILE.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def write_users_to_db(users_dict):
    users = read_users_from_db()
    users.append(users_dict)
    with DB_FILE.open("w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

