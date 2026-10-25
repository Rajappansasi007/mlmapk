import sqlite3
import json
import os
import requests

DB_PATH = "mlmapp.db"

# Replace with your actual Supabase URL & Key if live cloud sync is enabled
SUPABASE_URL = ""
SUPABASE_KEY = ""

def init_db(sql_dump_path="preloaded_data.sql"):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS mlmdata (
            id INTEGER PRIMARY KEY,
            title1 TEXT,
            lyrics TEXT,
            lyricseng TEXT,
            title2 TEXT,
            choavbl INTEGER,
            key TEXT,
            min_maj TEXT,
            auth TEXT,
            bpm TEXT,
            rhythm TEXT,
            timesignature TEXT,
            tags TEXT,
            ytlink TEXT,
            vvsongno TEXT,
            chords TEXT,
            pref_chord TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS app_users (
            username TEXT PRIMARY KEY,
            password TEXT,
            favourites TEXT,
            schedule TEXT,
            preferences TEXT,
            status TEXT,
            role TEXT,
            email TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS song_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            submission_type TEXT,
            submitted_by TEXT,
            title1 TEXT,
            title2 TEXT,
            song_title TEXT,
            raw_lyrics TEXT,
            raw_chords TEXT,
            meta_key TEXT,
            meta_bpm TEXT,
            meta_auth TEXT,
            meta_sig TEXT,
            meta_rhythm TEXT,
            meta_tags TEXT,
            admin_comments TEXT,
            status TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS session_state (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    conn.commit()

    # Preload from local SQL if table is empty
    c.execute("SELECT COUNT(*) FROM mlmdata")
    if c.fetchone()[0] == 0 and os.path.exists(sql_dump_path):
        with open(sql_dump_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            clean_script = sql_script.replace('"public".', '').replace('"pref.chord"', 'pref_chord')
            c.executescript(clean_script)
        conn.commit()

    # Ensure default admin account exists
    c.execute("SELECT COUNT(*) FROM app_users WHERE username = 'admin'")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO app_users (username, password, favourites, schedule, preferences, status, role, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, ('admin', 'admin123', json.dumps([]), json.dumps([]), json.dumps({}), 'active', 'admin', 'admin@mlm.com'))
        conn.commit()

    conn.close()

def get_current_user():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT value FROM session_state WHERE key = 'current_user'")
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def set_current_user(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if username:
        c.execute("INSERT OR REPLACE INTO session_state (key, value) VALUES ('current_user', ?)", (username,))
    else:
        c.execute("DELETE FROM session_state WHERE key = 'current_user'")
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT username, password, role, status FROM app_users WHERE LOWER(username) = ?", (username.lower().strip(),))
    row = c.fetchone()
    conn.close()
    if row and row[1] == password:
        return {"username": row[0], "role": row[2], "status": row[3]}
    return None

def create_user(username, email, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO app_users (username, password, favourites, schedule, preferences, status, role, email)
            VALUES (?, ?, ?, ?, ?, 'active', 'user', ?)
        """, (username.strip(), password.strip(), json.dumps([]), json.dumps([]), json.dumps({}), email.strip()))
        conn.commit()
        conn.close()
        return True, "Account registered successfully!"
    except Exception as e:
        conn.close()
        return False, f"Username already exists: {e}"

def load_user_data(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT favourites, schedule, preferences, role FROM app_users WHERE LOWER(username) = ?", (username.lower().strip(),))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0]), json.loads(row[1]), json.loads(row[2]), row[3]
    return [], [], {}, "user"

def save_user_data(username, favs, sched, prefs):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE app_users 
        SET favourites = ?, schedule = ?, preferences = ? 
        WHERE LOWER(username) = ?
    """, (json.dumps(favs), json.dumps(sched), json.dumps(prefs), username.lower().strip()))
    conn.commit()
    conn.close()

def get_all_songs_catalog():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, title1, title2, vvsongno, key, choavbl, timesignature, min_maj, tags FROM mlmdata ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_song_detail(song_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM mlmdata WHERE id = ?", (song_id,))
    row = c.fetchone()
    conn.close()
    return row

def update_song_meta_db(song_id, key_val, bpm_val, auth_val, sig_val, rhythm_val, tag_val):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        UPDATE mlmdata 
        SET key = COALESCE(?, key),
            bpm = COALESCE(?, bpm),
            auth = COALESCE(?, auth),
            timesignature = COALESCE(?, timesignature),
            rhythm = COALESCE(?, rhythm),
            tags = COALESCE(?, tags)
        WHERE id = ?
    """, (key_val, bpm_val, auth_val, sig_val, rhythm_val, tag_val, song_id))
    conn.commit()
    conn.close()

def insert_song_submission(payload):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO song_submissions (
            submission_type, submitted_by, title1, title2, song_title,
            raw_lyrics, raw_chords, meta_key, meta_bpm, meta_auth,
            meta_sig, meta_rhythm, meta_tags, admin_comments, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending')
    """, (
        payload.get("submission_type"), payload.get("submitted_by"),
        payload.get("title1"), payload.get("title2"), payload.get("song_title"),
        payload.get("raw_lyrics"), payload.get("raw_chords"),
        payload.get("meta_key"), payload.get("meta_bpm"), payload.get("meta_auth"),
        payload.get("meta_sig"), payload.get("meta_rhythm"), payload.get("meta_tags"),
        payload.get("admin_comments"),
    ))
    conn.commit()
    conn.close()

def get_pending_submissions():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM song_submissions WHERE status = 'pending'")
    rows = c.fetchall()
    conn.close()
    return rows

def resolve_submission_db(sub_id, status_val):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE song_submissions SET status = ? WHERE id = ?", (status_val, sub_id))
    conn.commit()
    conn.close()
