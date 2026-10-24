import sqlite3
import hashlib
import os
import secrets

# Store local database in the app directory / user home
DB_PATH = os.path.join(os.path.expanduser("~"), "mlm_local_data.db")

# =============================================================================
# 🔐 PURE PYTHON SECURE PASSWORD HASHER (PBKDF2-HMAC-SHA256)
# =============================================================================
def hash_password(password: str) -> str:
    """Hashes a password using PBKDF2 with a randomly generated 16-byte salt."""
    salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode('utf-8'),
        salt=salt.encode('utf-8'),
        iterations=100000
    )
    # Stored as salt$hash
    return f"{salt}${key.hex()}"

def verify_password(stored_password_hash: str, provided_password: str) -> bool:
    """Verifies a plain text password against the stored salt$hash string."""
    try:
        salt, key_hex = stored_password_hash.split('$')
        computed_key = hashlib.pbkdf2_hmac(
            hash_name='sha256',
            password=provided_password.encode('utf-8'),
            salt=salt.encode('utf-8'),
            iterations=100000
        )
        # Use constant-time comparison to prevent timing attacks
        return secrets.compare_digest(computed_key.hex(), key_hex)
    except Exception:
        return False

# =============================================================================
# 🗄️ DATABASE CONNECTION & SCHEMA INITIALIZATION
# =============================================================================
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

    # Seed initial default admin if not already present
    c.execute("SELECT * FROM app_users WHERE username = 'admin'")
    if not c.fetchone():
        admin_hash = hash_password("Mlm@dm1n@1987")
        c.execute("""
            INSERT INTO app_users (username, password, role, status, email)
            VALUES ('admin', ?, 'admin', 'active', 'admin@mlm.com')
        """, (admin_hash,))

    conn.commit()
    conn.close()

# =============================================================================
# 👤 USER AUTHENTICATION & MANAGEMENT
# =============================================================================
def verify_user(username: str, password: str):
    """Authenticates user credentials against local SQLite records."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM app_users WHERE lower(username) = ?", (username.lower().strip(),))
    row = c.fetchone()
    conn.close()

    if row and verify_password(row['password'], password):
        return dict(row)
    return None

def register_user(username: str, password: str, email: str = ""):
    """Registers a new user locally."""
    conn = get_connection()
    c = conn.cursor()
    hashed = hash_password(password)
    try:
        c.execute("""
            INSERT INTO app_users (username, password, email, role, status)
            VALUES (?, ?, ?, 'user', 'active')
        """, (username.strip(), hashed, email.strip()))
        conn.commit()
        return True, "User registered successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()

# =============================================================================
# 🎵 SONG DATA ACCESS
# =============================================================================
def fetch_songs(search_query: str = ""):
    """Fetches songs filtered by title, tags, or lyrics."""
    conn = get_connection()
    c = conn.cursor()
    if search_query:
        query = f"%{search_query.strip()}%"
        c.execute("""
            SELECT * FROM songs 
            WHERE title1 LIKE ? OR title2 LIKE ? OR lyricseng LIKE ? OR tags LIKE ?
        """, (query, query, query, query))
    else:
        c.execute("SELECT * FROM songs ORDER BY id DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

def add_song(data: dict):
    """Adds a new song entry to local SQLite."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO songs (title1, title2, auth, lyrics, lyricseng, tags, key, bpm, rhythm, chords, ytlink)
        VALUES (:title1, :title2, :auth, :lyrics, :lyricseng, :tags, :key, :bpm, :rhythm, :chords, :ytlink)
    """, data)
    conn.commit()
    conn.close()
