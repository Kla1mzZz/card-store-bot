from aiogram.fsm.state import StatesGroup, State

class AddCategory(StatesGroup):
    name = State()

class SendMesasgeToUser(StatesGroup):
    message = State()

class UserBalanceState(StatesGroup):
    user_id = State()
    balance = State()

class DeleteCategory(StatesGroup):
    category = State()

class DeleteCard(StatesGroup):
    card = State()

class AddCardsFromTxt(StatesGroup):
    category = State()
    cards = State()
    price = State()

class GiveDiscount(StatesGroup):
    user_id = State()
    discount = State() 

class RemoveDiscount(StatesGroup):
    user_id = State()