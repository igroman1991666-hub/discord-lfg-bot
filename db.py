import sqlite3
import time

DB_PATH = "lfg.db"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS lfg (
                message_id INTEGER PRIMARY KEY,
                mode       TEXT    NOT NULL,
                slots      INTEGER NOT NULL,
                players    TEXT    NOT NULL,
                created_at INTEGER NOT NULL
            )
        """)


def create_lfg(message_id, mode, slots, players):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT INTO lfg (message_id, mode, slots, players, created_at) VALUES (?, ?, ?, ?, ?)",
            (
                message_id,
                mode,
                slots,
                ",".join(str(p) for p in players),
                int(time.time()),
            ),
        )


def get_lfg(message_id):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute(
            "SELECT mode, slots, players FROM lfg WHERE message_id = ?",
            (message_id,),
        ).fetchone()

    if row is None:
        return None

    mode, slots, players = row
    return {
        "mode": mode,
        "slots": slots,
        "players": [int(x) for x in players.split(",") if x],
    }


def update_players(message_id, players):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE lfg SET players = ? WHERE message_id = ?",
            (",".join(str(p) for p in players), message_id),
        )


def delete_lfg(message_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM lfg WHERE message_id = ?", (message_id,))


def delete_old(max_age_seconds=21600):
    cutoff = int(time.time()) - max_age_seconds
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("DELETE FROM lfg WHERE created_at < ?", (cutoff,))
        return cursor.rowcount