"""Работа с базой данных SQLite.

Здесь хранится схема БД и функции для инициализации/сохранения истории.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path("app/data/diagnostics.db")


def get_connection() -> sqlite3.Connection:
    """Создать подключение к БД (если файла нет — создать)."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    """Создать таблицы БД, если их нет."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS symptoms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conditions TEXT NOT NULL,
                diagnosis TEXT NOT NULL,
                probability INTEGER NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                FOREIGN KEY(rule_id) REFERENCES rules(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_info TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def save_history(car_info: dict[str, Any], symptoms: list[str], result: dict[str, Any]) -> None:
    """Сохранить историю диагностики."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO history (car_info, symptoms, result, created_at)
            VALUES (?, ?, ?, datetime('now'))
            """,
            (
                json.dumps(car_info, ensure_ascii=False),
                json.dumps(symptoms, ensure_ascii=False),
                json.dumps(result, ensure_ascii=False),
            ),
        )
        conn.commit()
