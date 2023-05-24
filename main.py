import asyncio
from asyncio import AbstractEventLoop
from datetime import datetime

from telethon import TelegramClient, password
from telethon.errors import UserRestrictedError, UserDeactivatedBanError
from telethon.tl.functions.account import GetPasswordRequest
from telethon.tl.functions.channels import EditCreatorRequest, CreateChannelRequest,GetParticipantsRequest
from telethon.tl.functions.messages import ExportChatInviteRequest
from telethon.tl.types import ChannelParticipantsSearch

from db import db
from db.models import Userbot


class UserbotPool:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance: UserbotPool = super(UserbotPool, cls).__new__(cls)
            cls.instance.loop: AbstractEventLoop = None
            cls.instance.pool: list[int] = []
            cls.instance.running: dict[int: TelegramClient] = {}
        return cls.instance

    async def _get_and_shift_bot(self) -> Userbot:
        bot_id = self.pool.pop(0)
        self.pool.append(bot_id)
        bot = await Userbot.get(id=bot_id)
        return bot

    async def init(self, loop: AbstractEventLoop) -> None:
        await db.db_init()
        self.pool = await Userbot.all().values_list('id', flat=True)
        self.loop = loop

    async def create_chat(self, event_id: int, name: str, date: datetime) -> dict[int: str]:
        bot = await self._get_and_shift_bot()
        if bot.proxy_ip and bot.proxy_port and bot.proxy_user and bot.proxy_pass:
            proxy = {
                'proxy_type': 'socks5',
                'addr': bot.proxy_ip,
                'port': bot.proxy_port,
                'username': bot.proxy_user,
                'password': bot.proxy_pass,
                'rdns': True
            }
        else:
            proxy = None

        if bot.id not in self.running.keys():
            client = TelegramClient(
                bot.session_path, int(bot.api_id), bot.api_hash,
                proxy=proxy
            )
            await client.connect()
            self.running[bot.id] = client
        else:
            client = self.running[bot.id]

        try:
            update = await client(CreateChannelRequest(
                megagroup=True,
                title=name + ' ' + date.strftime('%d.%m.%Y'),
                about=name + ' ' + date.strftime('%d.%m.%Y'),
            ))
            chat_id = update.updates[1].channel_id
            update = await client(ExportChatInviteRequest(
                peer=chat_id
            ))
            link = update.link

        except (UserRestrictedError, UserDeactivatedBanError):
            await self.delete_bot(bot.id)
            await self.on_bot_blocked(event_id)
            return {event_id: 'bot_blocked'}

        async def wait_user_add_supergroup():
            while True:
                users = await client(GetParticipantsRequest(chat_id, ChannelParticipantsSearch(''), limit=2, offset=0, hash=0))
                users = users.participants
                if len(users) > 1:
                    user_id = users[0].user_id
                    pwd = await client(GetPasswordRequest())
                    pwd_2 = password.compute_check(pwd, bot.password)
                    try:
                        update = await client(EditCreatorRequest(
                            chat_id,
                            user_id,
                            pwd_2
                        ))
                        await client.delete_dialog(chat_id)
                        await self.on_bot_left_chat(event_id)
                        return
                    except (UserRestrictedError, UserDeactivatedBanError):
                        await self.delete_bot(bot.id)
                        await self.on_bot_blocked(event_id)
                        return
                await asyncio.sleep(1)

        self.loop.create_task(wait_user_add_supergroup())

        return {event_id: link}

    async def add_bot(self, session_path: str, api_id: int | str, api_hash: str, password: str,
                      proxy_ip: str = None, proxy_port: int = None,
                      proxy_user: str = None, proxy_pass: str = None) -> int:
        userbot = await Userbot.create(
            api_id=api_id,
            api_hash=api_hash,
            session_path=session_path,
            password=password,
            proxy_ip=proxy_ip,
            proxy_port=proxy_port,
            proxy_user=proxy_user,
            proxy_pass=proxy_pass
        )
        self.pool.append(userbot.id)

        return userbot.id

    async def delete_bot(self, bot_id: int):
        bot = await Userbot.get(id=bot_id)
        await bot.delete()
        self.pool.remove(bot_id)
        if bot_id in self.running.keys():
            client = self.running.pop(bot_id)
            await client.disconnect()

    async def on_bot_left_chat(self, event_id: int):
        pass

    async def on_bot_blocked(self, event_id: int):
        pass

