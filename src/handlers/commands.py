from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import user_kb, admin_kb
from messages import faq_txt
from repo import Repo
from config import ADMIN_IDS

router = Router()
repo = Repo()

@router.message(F.text == '/start')
async def start(message: Message):
    if message.from_user.id in ADMIN_IDS:
        await message.answer(f'Welcome {message.from_user.username}', reply_markup=admin_kb.main_kb, parse_mode='HTML')
        
    elif message.from_user.id in await repo.get_users_id():
        await message.answer(faq_txt, reply_markup=user_kb.main_kb, parse_mode='HTML')
        
    else:
        await repo.add_user(message.from_user.id, str(message.from_user.username))
        await message.answer(faq_txt, reply_markup=user_kb.main_kb, parse_mode='HTML')
