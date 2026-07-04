from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _utc_now():
    return datetime.now(timezone.utc).isoformat()


def _hash_password(password: str, salt: str | None = None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return salt, digest.hex()


def _verify_password(password: str, salt: str, password_hash: str):
    _, candidate_hash = _hash_password(password, salt=salt)
    return hmac.compare_digest(candidate_hash, password_hash)


class SQLiteSessionStore:
    def __init__(self, database_path="fitness_coach.db"):
        self.database_path = Path(database_path)
        if self.database_path.parent != Path("."):
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self):
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self):
        with self._connect() as connection:
            connection.executescript(
                """
                PRAGMA journal_mode = WAL;

                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    password_salt TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS access_tokens (
                    token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS messages (
                    user_id INTEGER PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS training_plans (
                    user_id INTEGER PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS profiles (
                    user_id INTEGER PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS feedback_logs (
                    user_id INTEGER PRIMARY KEY,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
                """
            )

    def create_user(self, username: str, email: str, password: str):
        username = username.strip()
        email = email.strip().lower()
        if not username:
            raise ValueError("用户名不能为空。")
        if "@" not in email:
            raise ValueError("邮箱格式不正确。")
        if len(password) < 6:
            raise ValueError("密码至少需要 6 位。")

        salt, password_hash = _hash_password(password)
        try:
            with self._connect() as connection:
                cursor = connection.execute(
                    """
                    INSERT INTO users (username, email, password_hash, password_salt, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (username, email, password_hash, salt, _utc_now()),
                )
                user_id = cursor.lastrowid
        except sqlite3.IntegrityError as error:
            raise ValueError("该邮箱已注册。") from error

        return self.get_user_by_id(user_id)

    def authenticate_user(self, email: str, password: str):
        email = email.strip().lower()
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row is None:
            return None
        if not _verify_password(password, row["password_salt"], row["password_hash"]):
            return None
        return self._public_user(row)

    def create_access_token(self, user_id: int):
        token = secrets.token_urlsafe(32)
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO access_tokens (token, user_id, created_at)
                VALUES (?, ?, ?)
                """,
                (token, user_id, _utc_now()),
            )
        return token

    def get_user_by_token(self, token: str | None):
        if not token:
            return None
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT users.*
                FROM users
                JOIN access_tokens ON access_tokens.user_id = users.id
                WHERE access_tokens.token = ?
                """,
                (token,),
            ).fetchone()
        return self._public_user(row) if row else None

    def get_user_by_id(self, user_id: int):
        with self._connect() as connection:
            row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return self._public_user(row) if row else None

    def revoke_token(self, token: str):
        with self._connect() as connection:
            connection.execute("DELETE FROM access_tokens WHERE token = ?", (token,))

    def get_messages(self, user_id):
        return self._load_json("messages", user_id, [])

    def get_training_plan(self, user_id):
        return self._load_json("training_plans", user_id, {})

    def save_session(self, user_id, messages, training_plan):
        self._save_json("messages", user_id, messages)
        self._save_json("training_plans", user_id, training_plan)

    def clear_training_plan(self, user_id):
        self._save_json("training_plans", user_id, {})

    def get_profile(self, user_id):
        return self._load_json("profiles", user_id, {})

    def get_feedback_log(self, user_id):
        return self._load_json("feedback_logs", user_id, [])

    def save_fitness_state(self, user_id, profile, feedback_log):
        self._save_json("profiles", user_id, profile)
        self._save_json("feedback_logs", user_id, feedback_log)

    def _load_json(self, table_name: str, user_id, default):
        with self._connect() as connection:
            row = connection.execute(
                f"SELECT payload FROM {table_name} WHERE user_id = ?",
                (int(user_id),),
            ).fetchone()
        if row is None:
            return default
        return json.loads(row["payload"])

    def _save_json(self, table_name: str, user_id, payload):
        with self._connect() as connection:
            connection.execute(
                f"""
                INSERT INTO {table_name} (user_id, payload, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (int(user_id), json.dumps(payload, ensure_ascii=False), _utc_now()),
            )

    @staticmethod
    def _public_user(row):
        return {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "created_at": row["created_at"],
        }


def create_session_store():
    database_path = os.getenv("DATABASE_PATH", "fitness_coach.db")
    return SQLiteSessionStore(database_path)
