# app/database.py
import sqlite3
import json
import os
import hashlib
import time
from typing import Optional, List, Dict, Any
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "career_compass.db")


def _get_conn():
    # allow usage across threads for development; change in prod
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def _ensure_schema():
    conn = _get_conn()
    cur = conn.cursor()

    # Users table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # History / analyses table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            jd_text TEXT,
            resume_text TEXT,
            analysis_result TEXT, -- stored as JSON string
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """
    )

    conn.commit()
    conn.close()


# run schema ensure on import
_ensure_schema()


# --------------------------
# Helpers
# --------------------------
def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _hash_password(password: str, salt: Optional[str] = None) -> str:
    """Return hex sha256 of (salt + password). If no salt given, use fixed app salt."""
    # using a fixed app salt here for simplicity; in prod use per-user salts and bcrypt/argon2
    app_salt = "career_compass_v1_salt_"  # small constant salt
    s = (salt or app_salt) + password
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _row_to_user(row) -> Dict[str, Any]:
    id_, name, email, _, created_at = row
    return {"id": id_, "name": name, "email": email, "created_at": created_at}


def _row_to_history(row) -> Dict[str, Any]:
    id_, user_id, jd_text, resume_text, analysis_result_txt, created_at = row
    try:
        ar = json.loads(analysis_result_txt) if analysis_result_txt else None
    except Exception:
        ar = None
    return {
        "id": id_,
        "user_id": user_id,
        "jd_text": jd_text,
        "resume_text": resume_text,
        "analysis_result": ar,
        "created_at": created_at,
    }


# --------------------------
# Public API used by main.py
# --------------------------
def register_user(name: str, email: str, password: str) -> Dict[str, Any]:
    """
    Register a new user.
    Returns { success: bool, message: str, user: {...} (on success) }
    """
    conn = _get_conn()
    cur = conn.cursor()
    created_at = _now_iso()
    password_hash = _hash_password(password)

    try:
        cur.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (name, email.lower().strip(), password_hash, created_at),
        )
        conn.commit()
        user_id = cur.lastrowid
        user = {"id": user_id, "name": name, "email": email.lower().strip(), "created_at": created_at}
        return {"success": True, "message": "Registered", "user": user}
    except sqlite3.IntegrityError as e:
        return {"success": False, "message": "Email already registered"}
    except Exception as e:
        return {"success": False, "message": f"Registration failed: {str(e)}"}
    finally:
        conn.close()


def login_user(email: str, password: str) -> Dict[str, Any]:
    """
    Login a user.
    Returns { success: bool, user: {...}, message: str } on success
    """
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, email, password_hash, created_at FROM users WHERE email = ?", (email.lower().strip(),))
        row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Invalid credentials"}
        user_id, name, email_db, stored_hash, created_at = row
        if _hash_password(password) != stored_hash:
            return {"success": False, "message": "Invalid credentials"}
        user = {"id": user_id, "name": name, "email": email_db, "created_at": created_at}
        return {"success": True, "message": "Login successful", "user": user}
    except Exception as e:
        return {"success": False, "message": f"Login error: {str(e)}"}
    finally:
        conn.close()


def save_analysis(user_id: int, jd_text: str, resume_text: str, analysis_result: dict) -> Dict[str, Any]:
    """
    Save analysis result to history.
    Returns { success: bool, history_id: int, message: str }
    """
    conn = _get_conn()
    cur = conn.cursor()
    created_at = _now_iso()
    try:
        ar_txt = json.dumps(analysis_result)
        cur.execute(
            "INSERT INTO history (user_id, jd_text, resume_text, analysis_result, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, jd_text, resume_text, ar_txt, created_at),
        )
        conn.commit()
        hid = cur.lastrowid
        return {"success": True, "history_id": hid, "message": "Saved"}
    except Exception as e:
        return {"success": False, "message": f"Save failed: {str(e)}"}
    finally:
        conn.close()


def get_user_history(user_id: int, limit: int = 50) -> Dict[str, Any]:
    """
    Fetch user's history entries, newest first.
    Returns { success: bool, history: [...] }
    """
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, user_id, jd_text, resume_text, analysis_result, created_at FROM history WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        )
        rows = cur.fetchall()
        hist = [_row_to_history(r) for r in rows]
        return {"success": True, "history": hist}
    except Exception as e:
        return {"success": False, "message": f"Fetch failed: {str(e)}", "history": []}
    finally:
        conn.close()


def delete_history_entry(history_id: int, user_id: int) -> Dict[str, Any]:
    """
    Delete a history entry if it belongs to user_id.
    Returns { success: bool, message: str }
    """
    conn = _get_conn()
    cur = conn.cursor()
    try:
        # ensure ownership
        cur.execute("SELECT user_id FROM history WHERE id = ?", (history_id,))
        row = cur.fetchone()
        if not row:
            return {"success": False, "message": "Entry not found"}
        owner_id = row[0]
        if owner_id != int(user_id):
            return {"success": False, "message": "Unauthorized"}
        cur.execute("DELETE FROM history WHERE id = ?", (history_id,))
        conn.commit()
        return {"success": True, "message": "Deleted"}
    except Exception as e:
        return {"success": False, "message": f"Delete failed: {str(e)}"}
    finally:
        conn.close()


# --------------------------
# Admin endpoints helpers
# --------------------------
def get_all_users() -> Dict[str, Any]:
    """
    Return all users for admin view.
    Response: { success: True, users: [...] }
    """
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, email, password_hash, created_at FROM users ORDER BY created_at DESC")
        rows = cur.fetchall()
        users = []
        for r in rows:
            users.append(_row_to_user(r))
        return {"success": True, "users": users}
    except Exception as e:
        return {"success": False, "message": f"Failed to fetch users: {str(e)}", "users": []}
    finally:
        conn.close()


def get_all_history(limit: int = 500) -> Dict[str, Any]:
    """
    Return all history entries (for admins).
    Response: { success: True, history: [...] }
    """
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT h.id, h.user_id, h.jd_text, h.resume_text, h.analysis_result, h.created_at, u.name, u.email "
            "FROM history h LEFT JOIN users u ON u.id = h.user_id ORDER BY h.created_at DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        out = []
        for row in rows:
            hid, uid, jd_text, resume_text, ar_txt, created_at, uname, uemail = row
            try:
                ar = json.loads(ar_txt) if ar_txt else None
            except Exception:
                ar = None
            out.append({
                "id": hid,
                "user_id": uid,
                "user_name": uname,
                "user_email": uemail,
                "jd_text": jd_text,
                "resume_text": resume_text,
                "analysis_result": ar,
                "created_at": created_at,
            })
        return {"success": True, "history": out}
    except Exception as e:
        return {"success": False, "message": f"Failed to fetch history: {str(e)}", "history": []}
    finally:
        conn.close()


def get_user_details(user_id: int) -> Dict[str, Any]:
    """
    Return user info + history for admin user details page.
    Response: { success: True, user: {...}, history: [...] }
    """
    conn = _get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, email, password_hash, created_at FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            return {"success": False, "message": "User not found"}
        user = _row_to_user(row)

        cur.execute(
            "SELECT id, user_id, jd_text, resume_text, analysis_result, created_at FROM history WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        rows = cur.fetchall()
        history = [_row_to_history(r) for r in rows]
        # add a quick count for frontend convenience
        user["history_count"] = len(history)
        return {"success": True, "user": user, "history": history}
    except Exception as e:
        return {"success": False, "message": f"Failed to get user details: {str(e)}"}
    finally:
        conn.close()
