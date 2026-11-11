import hashlib
import hmac
import secrets
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "users.db"
ITERATIONS = 310_000

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY COLLATE NOCASE, salt BLOB NOT NULL, password_hash BLOB NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    return conn

def register_user(username: str, password: str):
    username = username.strip()
    if len(username) < 3 or len(username) > 40:
        return False, "Username must be between 3 and 40 characters."
    if not all(ch.isalnum() or ch in "._-" for ch in username):
        return False, "Use only letters, numbers, dots, underscores, or hyphens in the username."
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."
    salt = secrets.token_bytes(16)
    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    try:
        with _connect() as conn:
            conn.execute("INSERT INTO users (username, salt, password_hash) VALUES (?, ?, ?)", (username, salt, password_hash))
        return True, "Account created. You can now sign in."
    except sqlite3.IntegrityError:
        return False, "That username is already registered. Please sign in instead."

def verify_user(username: str, password: str) -> bool:
    with _connect() as conn:
        row = conn.execute("SELECT salt, password_hash FROM users WHERE username = ?", (username.strip(),)).fetchone()
    if not row:
        return False
    salt, expected_hash = row
    actual_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return hmac.compare_digest(actual_hash, expected_hash)

def show_login_page():
    import streamlit as st

    st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #eef4ff 0%, #f8faff 55%, #edf7f6 100%); }
    [data-testid="stHeader"] { background: transparent; }
    .login-brand { text-align:center; margin: 2.2rem 0 1.3rem; }
    .login-brand .mark { display:inline-block; background:#173b70; color:white; padding:13px 17px; border-radius:16px; font-size:25px; }
    .login-brand h1 { color:#142b4a; font-size:2rem; margin:.8rem 0 .25rem; }
    .login-brand p { color:#61738a; margin:0; }
    div[data-testid="stForm"] { background:white; border:1px solid #e1e8f0; padding:1.4rem; border-radius:16px; box-shadow:0 12px 35px rgba(25,50,80,.08); }
    .login-foot { text-align:center; color:#7b8796; font-size:.82rem; margin-top:1.3rem; }
    </style>
    <div class="login-brand"><div class="mark">🔎</div><h1>Research Intelligence</h1><p>Sign in to your AI-powered research workspace</p></div>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.15, 1])
    with center:
        login_tab, register_tab = st.tabs(["Sign in", "Create account"])
        with login_tab:
            with st.form("login_form"):
                st.subheader("Welcome back")
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="Enter your password")
                submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
            if submitted:
                if verify_user(username, password):
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username.strip()
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        with register_tab:
            with st.form("register_form"):
                st.subheader("Create your account")
                new_username = st.text_input("Choose a username", placeholder="At least 3 characters")
                new_password = st.text_input("Create password", type="password", placeholder="At least 8 characters")
                confirm_password = st.text_input("Confirm password", type="password")
                submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    ok, message = register_user(new_username, new_password)
                    (st.success if ok else st.error)(message)
        st.markdown(
    """
    <div class="login-foot">
        Your account credentials are stored locally in this project's SQLite database.
    </div>
    """,
    unsafe_allow_html=True
)