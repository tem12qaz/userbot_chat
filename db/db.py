from tortoise import Tortoise


database_uri = 'sqlite://db/db.sqlite3'

TORTOISE_ORM = {
    "connections": {"default": database_uri},
    "apps": {
        "models": {
            "models": ["db.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def db_init():
    await Tortoise.init(
        db_url=database_uri,
        modules={'models': ['db.models']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()
