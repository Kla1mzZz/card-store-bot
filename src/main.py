import asyncio
from aiogram import Dispatcher, Bot
from config import TOKEN

from handlers import commands, user, admin
from repo import Repo

repo = Repo()

async def main():
    bot = Bot(str(TOKEN))
    dp = Dispatcher()
    
    dp.include_routers(admin.router, user.router, commands.router)
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    print('Bot starting')
    asyncio.run(repo.create_tables())
    asyncio.run(main())
    print('Bot stoped')