from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from keyboards import user_kb, admin_kb
from messages import main_menu_txt
from repo import Repo
from messages import rules_txt, faq_txt
from states.user_states import SendMessageState, SearchBin, TopUpState

router = Router()
repo = Repo()

@router.message(F.text == '💳Market')
async def market(message: Message):

    await message.delete()
    await message.answer(main_menu_txt, parse_mode='HTML', reply_markup=await user_kb.categories_kb())

@router.callback_query(F.data.startswith('category_'))
async def select_category(callback: CallbackQuery):
    category = callback.data.split('_')[1]
    
    await callback.message.answer(f'<b>---{category.upper()} CARDS---</b>', 
                                  reply_markup=await user_kb.cards_kb(category, user_id=callback.from_user.id), 
                                  parse_mode='HTML')

@router.message(F.text == '❓FAQ')
async def faq(message: Message):
    await message.answer(faq_txt, parse_mode='HTML')

@router.message(F.text == '🔮 Rules')
async def rules(message: Message):
    await message.answer(rules_txt, parse_mode='HTML')

@router.callback_query(user_kb.Pagination.filter())
async def pagination_cart(callback: CallbackQuery, callback_data: user_kb.Pagination):
    cards = await repo.get_cards_from_category(callback_data.category)
    
    page_num = int(callback_data.page)
    page = page_num if page_num >= 0 else 0
    
    if callback_data.action == 'next':
        page = page_num + 1 if page_num < (len(cards) - 1) else page_num
    
    if callback_data.action == 'prev':
        page = page_num - 1 if page_num > 0 else page_num
    
    keyboard = await user_kb.cards_kb(callback_data.category, page=page, user_id=callback.from_user.id)
    
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@router.callback_query(F.data.startswith('card_'))
async def cards(callback: CallbackQuery):
    card = callback.data.split('_')[1]
    category = callback.data.split('_')[2]
    
    get_card = await repo.get_card(card)
    user = await repo.get_user(callback.from_user.id)
    
    if get_card:
        if user.balance >= get_card.price:
            price = get_card.price * (1 - user.discount / 100)
            await repo.user_unbalance(callback.from_user.id, price)
            await repo.add_cart_to_user(callback.from_user.id, get_card.card, category)
            await repo.delete_card(get_card.card)
            
            refresh_user = await repo.get_user(callback.from_user.id)
            
            await callback.answer(f'The card is purchased✅\nBalance: {refresh_user.balance}$', show_alert=True)
            await callback.message.edit_reply_markup(reply_markup=await user_kb.cards_kb(category, user_id=callback.from_user.id))
            await callback.message.answer(f'<b>➖➖➖✅Purchased Card➖➖➖\n\nCard: {get_card.card} | {get_card.category.name}</b>', parse_mode='HTML')
        else:
            await callback.answer('You lack balance❌')
    
    else:
        await callback.answer('The card is out of stock📛')

@router.message(F.text == '💰My account')
async def account(message: Message):
    user = await repo.get_user(message.from_user.id)
    
    await message.answer(f'<b><em>---🧾My Account🧾---</em></b>\n\n➖➖➖➖➖\n💰<b>Balance</b>💰: <b>{user.balance}$</b>\n➖➖➖➖➖\n\n🆔: <em>{user.user_id}</em>\n<b>Username: {user.username}</b>', parse_mode='HTML', reply_markup=user_kb.my_account)
    
@router.callback_query(F.data == 'my_cards')
async def my_cards(callback: CallbackQuery):
    user = await repo.get_user(callback.from_user.id)
    
    cards = ''
    
    for card in user.card:
        cards += f'💳 {card.card} | {card.category}\n\n'
        
    await callback.message.answer(f'<b>➖➖➖➖➖💳My cards💳➖➖➖➖➖\n\n{cards}</b>', parse_mode='HTML')
    
@router.callback_query(F.data == 'top_up')
async def top_up(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TopUpState.amount)
    await callback.message.answer('<b>Enter the amount to be replenished:</b>', parse_mode='HTML')

@router.message(TopUpState.amount)
async def top_up_amount(message: Message, state: FSMContext):
    try:
        if float(message.text) <= 1:
            await message.answer('Minimum deposit is above <b>1$</b>📛', parse_mode='HTML')
        else:
            amount = message.text
            await message.answer(f'Amount: {amount}')
    except ValueError:
        await message.answer('The amount is wrong⛔')
        
    await state.clear()

@router.message(F.text == '💬Support')
async def support(message: Message, state: FSMContext):
    await state.set_state(SendMessageState.message)
    await message.answer('Send message to support:')

@router.message(SendMessageState.message)
async def send_message_to_support(message: Message, state: FSMContext):
    for admin in ADMIN_IDS:
        await message.bot.send_message(admin, f'➖➖➖➖➖\n<b>Username: @{message.from_user.username}</b>\n<b>🆔: <em>{message.from_user.id}</em></b>\n➖➖➖➖➖\n\nMessage: {message.text}', 
                                       parse_mode='HTML', reply_markup=admin_kb.reply_user(message.from_user.id))
    
    await message.answer('Message sent, please wait for a reply.✅')
    await state.clear()

@router.callback_query(F.data == 'search')
async def bin_search(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SearchBin.card)
    sent_message = await callback.message.answer('<b><em>--- 🔎 BIN Search ---</em></b>\nType the 6 digit bin you want to look for.', 
                                  parse_mode='HTML', reply_markup=user_kb.bin_search_kb)
    
    await state.update_data(message_id=sent_message.message_id)

@router.message(SearchBin.card)
async def bin_search_state(message: Message, state: FSMContext):
    data = await state.get_data()
    cards = await repo.get_card_in_six_digt(message.text)
    await message.bot.delete_message(message.from_user.id, data['message_id'])
    await message.answer(f'<b>---CARDS---</b>', parse_mode='HTML', reply_markup=await user_kb.get_cards_in_digt(cards, message.text, user_id=message.from_user.id))
    await state.clear()

@router.callback_query(user_kb.PaginationS.filter())
async def pagination_search_card(callback: CallbackQuery, callback_data: user_kb.PaginationS):
    cards = await repo.get_card_in_six_digt(callback_data.search_card)
    
    page_num = int(callback_data.page)
    page = page_num if page_num >= 0 else 0
    
    if callback_data.action == 'nextS':
        page = page_num + 1 if page_num < (len(cards) - 1) else page_num
    
    if callback_data.action == 'prevS':
        page = page_num - 1 if page_num > 0 else page_num
    
    keyboard = await user_kb.get_cards_in_digt(cards, callback_data.search_card, page=page, user_id=callback.from_user.id)
    
    await callback.message.edit_reply_markup(reply_markup=keyboard)

@router.callback_query(F.data.startswith('search_card_'))
async def search_cards(callback: CallbackQuery):
    card = callback.data.split('_')[2]
    search_card = callback.data.split('_')[4]
    
    get_card = await repo.get_card(card)
    user = await repo.get_user(callback.from_user.id)

    if get_card:
        if user.balance >= get_card.price:
            price = get_card.price * (1 - user.discount / 100)
            await repo.user_unbalance(callback.from_user.id, price)
            await repo.add_cart_to_user(callback.from_user.id, card, get_card.category.name)
            await repo.delete_card(get_card.card)
            
            refresh_user = await repo.get_user(callback.from_user.id)
            cards = await repo.get_card_in_six_digt(search_card)
            
            await callback.answer(f'The card is purchased✅\nBalance: {refresh_user.balance}$', show_alert=True)
            await callback.message.edit_reply_markup(reply_markup=await user_kb.get_cards_in_digt(cards, search_card, user_id=callback.from_user.id))
            await callback.message.answer(f'<b>➖➖➖✅Purchased Card➖➖➖\n\nCard: {get_card.card} | {get_card.category.name}</b>', parse_mode='HTML')
        else:
            await callback.answer('You lack balance❌')
    
    else:
        await callback.answer('The card is out of stock📛')
    
@router.callback_query(F.data == 'cancel_search')
async def cancel_search(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    await callback.message.delete()
    await callback.answer()