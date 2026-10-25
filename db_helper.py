import sqlite3
import json
import os

DB_PATH = "mlmapp.db"

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
        CREATE TABLE IF NOT EXISTS user_session (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS local_userdata (
            username TEXT PRIMARY KEY,
            favourites TEXT,
            schedule TEXT,
            preferences TEXT
        )
    """)
    conn.commit()

    c.execute("SELECT COUNT(*) FROM mlmdata")
    if c.fetchone()[0] == 0 and os.path.exists(sql_dump_path):
        with open(sql_dump_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            # Clean PostgreSQL specific syntax for SQLite compatibility
            clean_script = sql_script.replace('"public".', '').replace('"pref.chord"', 'pref_chord')
            c.executescript(clean_script)
        conn.commit()
    conn.close()

def get_all_songs(search_text=""):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    if search_text.strip():
        term = f"%{search_text.strip()}%"
        c.execute("""
            SELECT id, title1, title2, vvsongno, key, choavbl, timesignature 
            FROM mlmdata 
            WHERE title1 LIKE ? OR title2 LIKE ? OR vvsongno = ?
            ORDER BY title1 ASC
        """, (term, term, search_text.strip()))
    else:
        c.execute("SELECT id, title1, title2, vvsongno, key, choavbl, timesignature FROM mlmdata ORDER BY title1 ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_song_by_id(song_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM mlmdata WHERE id = ?", (song_id,))
    row = c.fetchone()
    conn.close()
    return row

def save_user_state(username, favs, sched, prefs):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO local_userdata (username, favourites, schedule, preferences)
        VALUES (?, ?, ?, ?)
    """, (username, json.dumps(favs), json.dumps(sched), json.dumps(prefs)))
    conn.commit()
    conn.close()

def load_user_state(username):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT favourites, schedule, preferences FROM local_userdata WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0]), json.loads(row[1]), json.loads(row[2])
    return [], [], {}
