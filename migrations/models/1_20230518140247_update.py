from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "userbot" ADD "password" VARCHAR(256);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "userbot" DROP COLUMN "password";"""
