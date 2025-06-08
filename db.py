import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

async def init_db():
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS user_channels (
            user_id BIGINT PRIMARY KEY,
            source_channel_id BIGINT NOT NULL,
            destination_channel_id BIGINT NOT NULL
        );
    """)
    await conn.close()

async def save_user_settings(user_id, source_id, dest_id):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute("""
        INSERT INTO user_channels (user_id, source_channel_id, destination_channel_id)
        VALUES ($1, $2, $3)
        ON CONFLICT (user_id) DO UPDATE SET
        source_channel_id = EXCLUDED.source_channel_id,
        destination_channel_id = EXCLUDED.destination_channel_id;
    """, user_id, source_id, dest_id)
    await conn.close()

async def get_user_settings(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    row = await conn.fetchrow("SELECT * FROM user_channels WHERE user_id = $1", user_id)
    await conn.close()
    return row
