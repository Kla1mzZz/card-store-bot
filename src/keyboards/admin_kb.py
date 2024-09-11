from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from repo import Repo

repo = Repo()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Add cards from .txt💳💳💳'), KeyboardButton(text='Delete card❌')],
        [KeyboardButton(text='Add category📃'), KeyboardButton(text='Delete category❌')],
        [KeyboardButton(text='Add balance💵'), KeyboardButton(text='Give discount✉'), KeyboardButton(text='Remove discount❌')]
    ], resize_keyboard=True)


async def get_categories():
    categories = await repo.get_categories()
    
    btns = [[KeyboardButton(text=category.name)] for category in categories]
    
    
    return ReplyKeyboardMarkup(keyboard=btns, resize_keyboard=True)

def reply_user(user_id):
    btns = [[InlineKeyboardButton(text='Reply', callback_data='reply_' + str(user_id))]]
    
    return InlineKeyboardMarkup(inline_keyboard=btns)