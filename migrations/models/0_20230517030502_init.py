from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "userbot" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "api_id" VARCHAR(64) NOT NULL,
    "api_hash" VARCHAR(128) NOT NULL,
    "session_path" VARCHAR(512) NOT NULL,
    "proxy_ip" VARCHAR(16),
    "proxy_port" INT,
    "proxy_user" VARCHAR(128),
    "proxy_pass" VARCHAR(128)
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSON NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
