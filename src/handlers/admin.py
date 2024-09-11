import time
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards import admin_kb
from repo import Repo
from config import ADMIN_IDS
from states.admin_states import AddCategory, SendMesasgeToUser, UserBalanceState, DeleteCategory, DeleteCard, AddCardsFromTxt, GiveDiscount, RemoveDiscount
from handlers.utils import format_file_lines

router = Router()
repo = Repo()

@router.message(F.text == 'Add category📃')
async def add_category(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        await state.set_state(AddCategory.name)
        await message.answer('Enter category name:')

@router.message(AddCategory.name)
async def add_category_name(message: Message, state: FSMContext):
    if message.text == 'Delete category❌':
        await message.answer('Incorrect category name❌')
        await state.clear()
    else:
        await repo.add_category(message.text)
        
        await message.answer('Category added✅')
        
        await state.clear()

@router.message(F.text == 'Delete card❌')
async def delete_card(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        await state.set_state(DeleteCard.card)
        await message.answer('Enter card:')

@router.message(DeleteCard.card)
async def delete_card_state(message: Message, state: FSMContext):
    if await repo.get_card(message.text):
        await repo.delete_card(message.text)
        await message.answer('Card deleted✅')
    else:
        await message.answer('There is no such card📛')
        
    await state.clear()
        
@router.callback_query(F.data.startswith('reply_'))
async def reply_user(callback: CallbackQuery, state: FSMContext):
    user_id = callback.data.split('_')[1]
    await state.set_state(SendMesasgeToUser.message)
    await state.update_data(user_id=user_id)
    await callback.message.answer('Enter a message to the user: ')
    
@router.message(SendMesasgeToUser.message)
async def send_message_to_user(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer('Message sent✅')
    await message.bot.send_message(data['user_id'], f'<b>💬Support: {message.text}</b>', parse_mode='HTML')
    
    await state.clear()

@router.message(F.text == 'Add balance💵')
async def add_to_balance(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        await state.set_state(UserBalanceState.user_id)
        await message.answer('Enter user id:')

@router.message(UserBalanceState.user_id)
async def add_to_balance_user_id(message: Message, state: FSMContext):
    try:
        await state.set_state(UserBalanceState.balance)
        await state.update_data(user_id=int(message.text))
        
        await message.answer('Enter the amount:')
    except ValueError:
        await message.answer('Invalid user ID❌')
        await state.clear()

@router.message(UserBalanceState.balance)
async def add_to_user_balance(message: Message, state: FSMContext):
    data = await state.get_data()
    
    await repo.add_to_user_balance(int(data['user_id']), float(message.text))
    await message.answer('Amount added✅')
    
    await state.clear()

@router.message(F.text == 'Delete category❌')
async def delete_category(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        await state.set_state(DeleteCategory.category)
        
        await message.answer('Enter category:', reply_markup=await admin_kb.get_categories())

@router.message(DeleteCategory.category)
async def delete_category_state(message: Message, state: FSMContext):
    for category in await repo.get_categories():
        if message.text == category.name:
            await repo.delete_category(str(message.text))
            await message.answer('Category deleted✅', reply_markup=admin_kb.main_kb)
            return

    await message.answer('Category not found❌', reply_markup=admin_kb.main_kb)
    await state.clear()

@router.message(F.text == 'Add cards from .txt💳💳💳')
async def add_cards_from_txt(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        await state.set_state(AddCardsFromTxt.category)
        await message.answer('Enter category:', reply_markup=await admin_kb.get_categories())

@router.message(AddCardsFromTxt.category)
async def add_cards_from_txt_category(message: Message, state: FSMContext):
    for category in await repo.get_categories():
        if message.text == category.name:
            await state.update_data(category=message.text)
            await state.set_state(AddCardsFromTxt.cards)
            await message.answer('Send .txt file📃:', reply_markup=admin_kb.main_kb)
            return

    await message.answer('Category not found❌', reply_markup=admin_kb.main_kb)
    await state.clear()

@router.message(AddCardsFromTxt.cards)
async def add_cards_from_txt_cards(message: Message, state: FSMContext):
    try:
        file_id = message.document.file_id
        file = await message.bot.get_file(file_id)
        
        if message.document.file_name.split('.')[1] == 'txt':
            await message.bot.download_file(file.file_path, './cards1.txt')
            
            await message.answer('Enter price:')
            await state.set_state(AddCardsFromTxt.price)
        else:
            await message.answer('Send the file in .txt format:')
    except:
        await message.answer('Send the correct file📛')
        await state.clear()

@router.message(AddCardsFromTxt.price)
async def add_cards_from_txt_price(message: Message, state: FSMContext):
    start_time = time.time() 
    data = await state.get_data()
    
    cards = await format_file_lines('cards1.txt')
    for card in cards:
        await repo.create_card(card, float(message.text), data['category'])

    end_time = time.time()
    execution_time = end_time - start_time

    await message.answer(f'Cards added✅\nExecution time: {execution_time:.2f} seconds⌚')
    await state.clear()

@router.message(F.text == 'Give discount✉')
async def give_discount_start(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        await state.set_state(GiveDiscount.user_id)
        await message.answer('Enter user ID for discount:')

@router.message(GiveDiscount.user_id)
async def give_discount_user(message: Message, state: FSMContext):
    try:
        user_id = int(message.text.strip())
        
        if await repo.get_user(user_id):
            await state.update_data(user_id=user_id)
            await state.set_state(GiveDiscount.discount)
            await message.answer('Enter discount percentage (e.g., 10 for 10%):')
        else:
            await message.answer('User not found❌')
            await state.clear()
    except ValueError:
        await message.answer('Invalid user ID❌')
        await state.clear()

@router.message(GiveDiscount.discount)
async def give_discount_value(message: Message, state: FSMContext):
    try:
        discount = float(message.text)
        if not 0 < discount <= 100:
            raise ValueError("Discount must be between 0 and 100")

        data = await state.get_data()
        user_id = data['user_id']

        await repo.apply_user_discount(user_id, discount)

        await message.answer(f'Discount of {discount}% applied to user with ID {user_id}✅')
        await message.bot.send_message(user_id, f"You've been given a discount <b>{discount}%</b>💖", parse_mode='HTML')
        await state.clear()

    except ValueError:
        await message.answer('Please enter a valid discount percentage between 0 and 100❌')
        await state.clear()

@router.message(F.text == 'Remove discount❌')
async def remove_discount_start(message: Message, state: FSMContext):
    if message.from_user.id in ADMIN_IDS:
        await state.set_state(RemoveDiscount.user_id)
        await message.answer('Enter user ID to remove discount:')

@router.message(RemoveDiscount.user_id)
async def remove_discount_user(message: Message, state: FSMContext):
    try:
        user_id = int(message.text.strip())
        
        if await repo.get_user(user_id):
            await repo.remove_user_discount(user_id)
            await message.answer(f'Discount removed from user with ID {user_id}✅')
            await state.clear()
        else:
            await message.answer('User not found❌')
            await state.clear()
    except ValueError:
        await message.answer('Invalid user ID❌')
        await state.clear()