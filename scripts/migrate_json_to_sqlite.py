import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
DB_PATH = DATA_DIR / "bot.db"

def migrate():
    print(f"Connecting to {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Migrate allowed_users.json
    allowed_file = DATA_DIR / "allowed_users.json"
    if allowed_file.exists():
        print("Migrating allowed_users...")
        with open(allowed_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for uid in data.get("user_ids", []):
                cursor.execute('INSERT INTO allowed_users (type, value) VALUES (?, ?)', ("id", str(uid)))
            for uname in data.get("usernames", []):
                cursor.execute('INSERT INTO allowed_users (type, value) VALUES (?, ?)', ("username", uname.lower()))
    
    # Migrate custom_keywords.json
    keywords_file = DATA_DIR / "custom_keywords.json"
    if keywords_file.exists():
        print("Migrating keywords...")
        with open(keywords_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for cat in ["spam", "toxic", "sticker"]:
                for kw in data.get(cat, []):
                    cursor.execute('INSERT INTO keywords (word, category, response) VALUES (?, ?, ?)', (kw, cat, None))
            for item in data.get("pattern", []):
                if isinstance(item, dict):
                    word = item.get("word")
                    resp = item.get("response")
                else:
                    word = item
                    resp = None
                if word:
                    cursor.execute('INSERT INTO keywords (word, category, response) VALUES (?, ?, ?)', (word, "pattern", resp))

    # Migrate dashboard_stats.json
    stats_file = DATA_DIR / "dashboard_stats.json"
    if stats_file.exists():
        print("Migrating stats...")
        with open(stats_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            cursor.execute('''
                INSERT INTO stats (id, total_messages_scanned, spam_toxic_blocked)
                VALUES (1, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    total_messages_scanned = excluded.total_messages_scanned,
                    spam_toxic_blocked = excluded.spam_toxic_blocked
            ''', (data.get("total_messages_scanned", 0), data.get("spam_toxic_blocked", 0)))
            
            for act in data.get("recent_activity", []):
                cursor.execute('INSERT INTO activity_logs (time, type, text, username) VALUES (?, ?, ?, ?)', 
                    (act.get("time"), act.get("type"), act.get("text"), act.get("username")))
                    
            for uid, vdata in data.get("violations", {}).items():
                cursor.execute('''
                    INSERT INTO user_violations (user_id, username, strikes, last_violation)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id) DO NOTHING
                ''', (str(uid), vdata.get("username", ""), vdata.get("strikes", 0), vdata.get("last_violation", "")))

    # Migrate groups.json
    groups_file = DATA_DIR / "groups.json"
    if groups_file.exists():
        print("Migrating groups...")
        with open(groups_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for gid, gdata in data.items():
                cursor.execute('INSERT INTO groups (id, title) VALUES (?, ?) ON CONFLICT(id) DO NOTHING', (str(gid), gdata.get("title", "")))

    # Migrate users.json
    users_file = DATA_DIR / "users.json"
    if users_file.exists():
        print("Migrating users...")
        with open(users_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for uid, udata in data.items():
                cursor.execute('INSERT INTO users (id, username) VALUES (?, ?) ON CONFLICT(id) DO NOTHING', (str(uid), udata.get("username", "")))

    # Migrate scheduled_messages.json
    sched_file = DATA_DIR / "scheduled_messages.json"
    if sched_file.exists():
        print("Migrating scheduled messages...")
        with open(sched_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for msg in data:
                cursor.execute('''
                    INSERT INTO scheduled_messages 
                    (id, message, chat_ids, send_at, status, created_at, file_path, file_type, sent_at, results, error)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO NOTHING
                ''', (
                    msg.get("id"),
                    msg.get("message", ""),
                    json.dumps(msg.get("chatIds", [])),
                    msg.get("sendAt", ""),
                    msg.get("status", "pending"),
                    msg.get("createdAt", datetime.now().isoformat()),
                    msg.get("file_path"),
                    msg.get("file_type"),
                    msg.get("sentAt"),
                    json.dumps(msg.get("results")) if msg.get("results") else None,
                    msg.get("error")
                ))

    # Migrate settings.json
    settings_file = DATA_DIR / "settings.json"
    if settings_file.exists():
        print("Migrating settings...")
        with open(settings_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k, v in data.items():
                cursor.execute('''
                    INSERT INTO settings (key, value) VALUES (?, ?)
                    ON CONFLICT(key) DO UPDATE SET value = excluded.value
                ''', (k, json.dumps(v)))

    # Migrate otps.json
    otps_file = DATA_DIR / "otps.json"
    if otps_file.exists():
        print("Migrating otps...")
        with open(otps_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for uid, odata in data.items():
                expires_at = odata.get("expires_at", 0) * 1000
                cursor.execute('''
                    INSERT INTO otps (user_id, otp, username, expires_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id) DO NOTHING
                ''', (str(uid), odata.get("otp", ""), odata.get("username", ""), expires_at))

    conn.commit()
    conn.close()
    print("Migration complete!")

if __name__ == "__main__":
    migrate()
