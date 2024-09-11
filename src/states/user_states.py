from aiogram.fsm.state import State, StatesGroup

class SendMessageState(StatesGroup):
    message = State()

class SearchBin(StatesGroup):
    card = State()

class TopUpState(StatesGroup):
    amount = State()