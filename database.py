import sqlite3
import json
import bcrypt
import os

DB_PATH = os.path.join(os.path.expanduser("~"), "mlm_local_data.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # 1. Users Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS app_users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        favourites TEXT DEFAULT '[]',
        schedule TEXT DEFAULT '[]',
        preferences TEXT DEFAULT '{}',
        status TEXT DEFAULT 'active',
        role TEXT DEFAULT 'user',
        email TEXT DEFAULT ''
    )
    """)

    # 2. Songs Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title1 TEXT,
        title2 TEXT,
        auth TEXT,
        lyrics TEXT,
        lyricseng TEXT,
        tags TEXT,
        key TEXT,
        bpm TEXT,
        rhythm TEXT,
        chords TEXT,
        ytlink TEXT
    )
    """)

    # 3. Submissions Table
    c.execute("""
    CREATE TABLE IF NOT EXISTS song_submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title1 TEXT,
        lyrics TEXT,
        submitted_by TEXT,
        status TEXT DEFAULT 'pending'
    )
    """)

    # Create default admin if not exists
    c.execute("SELECT * FROM app_users WHERE username = 'admin'")
    if not c.fetchone():
        hashed = bcrypt.hashpw("Mlm@dm1n@1987".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        c.execute("""
            INSERT INTO app_users (username, password, role, status)
            VALUES ('admin', ?, 'admin', 'active')
        """, (hashed,))

    conn.commit()
    conn.close()

# --- User Operations ---
def verify_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM app_users WHERE lower(username) = ?", (username.lower().strip(),))
    row = c.fetchone()
    conn.close()
    if row and bcrypt.checkpw(password.encode('utf-8'), row['password'].encode('utf-8')):
        return dict(row)
    return None

# --- Song Operations ---
def fetch_songs(search_query=""):
    conn = get_connection()
    c = conn.cursor()
    if search_query:
        query = f"%{search_query.strip()}%"
        c.execute("""
            SELECT * FROM songs 
            WHERE title1 LIKE ? OR title2 LIKE ? OR lyricseng LIKE ? OR tags LIKE ?
        """, (query, query, query, query))
    else:
        c.execute("SELECT * FROM songs")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def add_song(data):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO songs (title1, title2, auth, lyrics, lyricseng, tags, key, bpm, rhythm, chords, ytlink)
        VALUES (:title1, :title2, :auth, :lyrics, :lyricseng, :tags, :key, :bpm, :rhythm, :chords, :ytlink)
    """, data)
    conn.commit()
    conn.close()
  
