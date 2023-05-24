from tortoise import fields
from tortoise.models import Model


# from keyboards.inline.keyboards import go_to_chat_keyboard


class Userbot(Model):
    id = fields.IntField(pk=True)
    api_id = fields.CharField(64)
    api_hash = fields.CharField(128)
    session_path = fields.CharField(512)
    password = fields.CharField(256, null=True)
    proxy_ip = fields.CharField(16, null=True)
    proxy_port = fields.IntField(null=True)
    proxy_user = fields.CharField(128, null=True)
    proxy_pass = fields.CharField(128, null=True)

