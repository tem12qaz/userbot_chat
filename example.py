import asyncio
from datetime import datetime

from main import UserbotPool


class UserbotPoolOverride(UserbotPool):  # наследуем класс и перегружаем методы
    async def on_bot_blocked(self, event_id: int):
        # этот код выполнится при блокировке бота
        print(f'{event_id} bot restricted')

    async def on_bot_left_chat(self, event_id: int):
        # этот код выполнится при передаче прав и выходе из чата
        print(f'{event_id} bot left chat')


async def main():
    pool = UserbotPoolOverride()  # создаем экземпляр (singleton)
    await pool.init(loop=loop)  # инициализируем бд

    # добавление нового бота в систему
    bot_id = await pool.add_bot(
        session_path='test.session', # путь к файлу сессии

        # api_id api_hash password брать из файла json при покупке
        api_id=1,
        api_hash='hash',
        password='2fapsswd', # пароль 2fa от аккаунта телеграм

        proxy_ip='1.1.1.1',
        proxy_port=80,
        proxy_user='login',
        proxy_pass='password',
    )

    # удаление бота
    await pool.delete_bot(bot_id=bot_id)

    # добавим бота повторно
    bot_id = await pool.add_bot(
        session_path='test.session',  # путь к файлу сессии

        # api_id api_hash password брать из файла json при покупке
        api_id=1,
        api_hash='hash',
        password='2fapsswd',  # пароль 2fa от аккаунта телеграм

        proxy_ip='1.1.1.1',
        proxy_port=80,
        proxy_user='login',
        proxy_pass='password',
    )

    # создание чата
    result = await pool.create_chat(
        event_id=1, name='test_name', date=datetime.now()
    )
    # result = {event_id: ссылка на вступление} если успешно
    # result = {event_id: 'bot_blocked'} если бот заблокирован
    print(result)

if __name__ == '__main__':
    loop = asyncio.new_event_loop()  # создаем новый eventloop, если нет существующего
    loop.create_task(main())
    loop.run_forever()



