"""
🗄️ Database - SQLite with aiosqlite
"""
import aiosqlite
import logging
from datetime import datetime
from config import DATABASE_URL

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.db_path = DATABASE_URL

    async def init(self):
        """Create tables if not exists"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id     INTEGER PRIMARY KEY,
                    username    TEXT,
                    full_name   TEXT,
                    language    TEXT DEFAULT 'uz',
                    region      TEXT DEFAULT NULL,
                    is_admin    INTEGER DEFAULT 0,
                    is_banned   INTEGER DEFAULT 0,
                    joined_at   TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_active TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS usage_stats (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     INTEGER,
                    action_type TEXT,  -- 'youtube', 'instagram', 'tiktok', 'music_search', 'lyrics'
                    created_at  TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS required_channels (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id  TEXT UNIQUE,
                    channel_name TEXT,
                    channel_link TEXT,
                    added_at    TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    user_id     INTEGER PRIMARY KEY,
                    added_by    INTEGER,
                    added_at    TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS song_cache (
                    user_id    INTEGER PRIMARY KEY,
                    artist     TEXT,
                    title      TEXT,
                    album      TEXT,
                    full_title TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE TABLE IF NOT EXISTS search_results (
                    user_id    INTEGER PRIMARY KEY,
                    results    TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
        logger.info("✅ Database initialized")

    # ─── USER METHODS ──────────────────────────────────────────────
    async def add_user(self, user_id: int, username: str, full_name: str, language: str = "uz"):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR IGNORE INTO users (user_id, username, full_name, language)
                VALUES (?, ?, ?, ?)
            """, (user_id, username, full_name, language))
            await db.commit()

    async def get_user(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                return await cursor.fetchone()

    async def update_user_language(self, user_id: int, language: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
            await db.commit()

    async def update_user_region(self, user_id: int, region: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("UPDATE users SET region = ? WHERE user_id = ?", (region, user_id))
            await db.commit()

    async def update_last_active(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()

    async def get_all_users(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT user_id FROM users WHERE is_banned = 0") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]

    async def get_user_count(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("SELECT COUNT(*) FROM users") as cursor:
                row = await cursor.fetchone()
                return row[0]

    async def get_active_today(self) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT COUNT(*) FROM users WHERE date(last_active) = date('now')"
            ) as cursor:
                row = await cursor.fetchone()
                return row[0]

    # ─── STATS METHODS ─────────────────────────────────────────────
    async def log_usage(self, user_id: int, action_type: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT INTO usage_stats (user_id, action_type) VALUES (?, ?)",
                (user_id, action_type)
            )
            await db.commit()

    async def get_usage_stats(self) -> dict:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT action_type, COUNT(*) as cnt
                FROM usage_stats
                GROUP BY action_type
                ORDER BY cnt DESC
            """) as cursor:
                rows = await cursor.fetchall()
                return {row[0]: row[1] for row in rows}

    async def get_region_stats(self) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT region, COUNT(*) as cnt
                FROM users
                WHERE region IS NOT NULL
                GROUP BY region
                ORDER BY cnt DESC
            """) as cursor:
                return await cursor.fetchall()

    # ─── ADMIN METHODS ─────────────────────────────────────────────
    async def is_admin(self, user_id: int) -> bool:
        from config import ADMIN_IDS
        if user_id in ADMIN_IDS:
            return True
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT user_id FROM admins WHERE user_id = ?", (user_id,)
            ) as cursor:
                return await cursor.fetchone() is not None

    async def add_admin(self, user_id: int, added_by: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?, ?)",
                (user_id, added_by)
            )
            await db.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
            await db.commit()

    async def remove_admin(self, user_id: int):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
            await db.execute("UPDATE users SET is_admin = 0 WHERE user_id = ?", (user_id,))
            await db.commit()

    # ─── SEARCH RESULTS METHODS ────────────────────────────────────
    async def save_search_results(self, user_id: int, results: list):
        import json
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO search_results (user_id, results, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (user_id, json.dumps(results, ensure_ascii=False)))
            await db.commit()

    async def get_search_results(self, user_id: int) -> list:
        import json
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT results FROM search_results WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return []

    # ─── SONG CACHE METHODS ────────────────────────────────────────
    async def save_song_cache(self, user_id: int, artist: str, title: str, album: str, full_title: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO song_cache (user_id, artist, title, album, full_title, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, artist, title, album, full_title))
            await db.commit()

    async def get_song_cache(self, user_id: int) -> dict | None:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                "SELECT * FROM song_cache WHERE user_id = ?", (user_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if row:
                    return dict(row)
                return None

    # ─── CHANNEL METHODS ───────────────────────────────────────────
    async def add_required_channel(self, channel_id: str, channel_name: str, channel_link: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT OR REPLACE INTO required_channels (channel_id, channel_name, channel_link)
                VALUES (?, ?, ?)
            """, (channel_id, channel_name, channel_link))
            await db.commit()

    async def remove_required_channel(self, channel_id: str):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "DELETE FROM required_channels WHERE channel_id = ?", (channel_id,)
            )
            await db.commit()

    async def get_required_channels(self) -> list:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("SELECT * FROM required_channels") as cursor:
                return await cursor.fetchall()
