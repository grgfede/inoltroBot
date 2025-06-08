import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

async def init_db():
    conn = await asyncpg.connect(DB_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS user_settings (
            user_id BIGINT PRIMARY KEY,
            bot_token TEXT NOT NULL,
            source_channel_id BIGINT NOT NULL,
            dest_channel_id BIGINT NOT NULL
        );
    """)
    await conn.close()

async def save_user_settings(user_id, bot_token, source_id, dest_id):
    conn = await asyncpg.connect(DB_URL)
    await conn.execute("""
        INSERT INTO user_settings (user_id, bot_token, source_channel_id, dest_channel_id)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (user_id) DO UPDATE SET
        bot_token = EXCLUDED.bot_token,
        source_channel_id = EXCLUDED.source_channel_id,
        dest_channel_id = EXCLUDED.dest_channel_id;
    """, user_id, bot_token, source_id, dest_id)
    await conn.close()

async def get_user_settings(user_id):
    conn = await asyncpg.connect(DB_URL)
    row = await conn.fetchrow("SELECT * FROM user_settings WHERE user_id = $1", user_id)
    await conn.close()
    return row
