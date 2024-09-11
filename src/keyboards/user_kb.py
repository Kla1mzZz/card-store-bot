from typing import Sequence
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from models import MarketCard
from repo import Repo

repo = Repo()

class Pagination(CallbackData, prefix='pag'):
    action: str
    page: int
    category: str
    user_id: int

async def cards_kb(category_name: str = 'None', page: int = 1, per_page: int = 5, user_id: int = 0):
    cards = await repo.get_cards_from_category(category_name)
    user = await repo.get_user(user_id)
    btns = []

    if cards:
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        cards_on_page = cards[start_index:end_index]

        for card in cards_on_page:
            original_price = card.price
            discounted_price = original_price

            if user.discount > 0:
                discounted_price = original_price * (1 - user.discount / 100)

            card_text = f"{card.card[:6]} -- {discounted_price:.1f}$💳"
            if user.discount > 0:
                card_text += f" (Discounted {user.discount}% from {original_price}$)"

            btns.append([InlineKeyboardButton(text=card_text, callback_data=f'card_{card.card.split("|")[0]}_{category_name}')])

        pagination_btns = []
        if page > 1:
            pagination_btns.append(
                InlineKeyboardButton(text='⬅', callback_data=Pagination(action='prev', page=page, category=category_name, user_id=user_id).pack())
            )
        if end_index < len(cards):
            pagination_btns.append(
                InlineKeyboardButton(text='➡', callback_data=Pagination(action='next', page=page, category=category_name, user_id=user_id).pack())
            )

        if pagination_btns:
            btns.append(pagination_btns)
    else:
        btns = [[InlineKeyboardButton(text='Empty', callback_data='empty')]]

    return InlineKeyboardMarkup(inline_keyboard=btns)



main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='💳Market'), KeyboardButton(text='💰My account')],
        [KeyboardButton(text='🔮 Rules'), KeyboardButton(text='❓FAQ')],
        [KeyboardButton(text='💬Support')]
    ], resize_keyboard=True)

async def categories_kb():
    categories = await repo.get_categories()
    
    search_button = InlineKeyboardButton(
        text='🔎BIN Search🔎',
        callback_data='search'
    )

    category_buttons = [
        InlineKeyboardButton(
            text=category.name,
            callback_data='category_' + category.name
        )
        for category in categories
    ]

    btns = [[search_button]] + [[button] for button in category_buttons]
    
    return InlineKeyboardMarkup(inline_keyboard=btns)

class PaginationS(CallbackData, prefix='pagS'):
    action: str
    page: int
    search_card: str
    user_id: int

async def get_cards_in_digt(cards: Sequence[MarketCard], search_card: str = 'None', page: int = 1, per_page: int = 5, user_id: int = 0):
    btns = []
    
    user = await repo.get_user(user_id)
    
    if cards:
        start_index = (page - 1) * per_page
        end_index = start_index + per_page
        cards_on_page = cards[start_index:end_index]
    
        for card in cards_on_page:
            discounted_price = card.price
            try:
                if user.discount > 0:
                    discounted_price = card.price * (1 - user.discount / 100)

                card_text = f"{card.card[:6]} -- {discounted_price:.1f}$💳"
                    
                if user.discount > 0:
                    card_text += f" (Discounted {user.discount}% from {card.price}$)"
            except UnboundLocalError:
                pass
            btns.append([InlineKeyboardButton(text=card_text, callback_data='search_card_' + card.card.split('|')[0] + '_' + card.category.name + '_' + search_card)])

        pagination_btns = []
        if page > 1:
            pagination_btns.append(InlineKeyboardButton(text='⬅', callback_data=PaginationS(action='prevS', page=page, search_card=search_card, user_id=user_id).pack()))
        if end_index < len(cards):
            pagination_btns.append(InlineKeyboardButton(text='➡', callback_data=PaginationS(action='nextS', page=page, search_card=search_card, user_id=user_id).pack()))
        
        if pagination_btns:
            btns.append(pagination_btns)
    else:
        btns = [[InlineKeyboardButton(text='Empty', callback_data='empty')]]

    return InlineKeyboardMarkup(inline_keyboard=btns)


bin_search_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='❌Cancel', callback_data='cancel_search')]
])

my_account = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='💵Top Up', callback_data='top_up')],
    [InlineKeyboardButton(text=f'My cards💳💳', callback_data='my_cards')],
    
])