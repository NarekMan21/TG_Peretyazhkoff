"""FSM состояния бота"""
from aiogram.fsm.state import State, StatesGroup


class OrderStates(StatesGroup):
    """Состояния для оформления заявки"""
    # Главное меню (начальное состояние)
    start = State()
    
    # Выбор типа мебели
    choose_item_type = State()
    
    # Ожидание фото
    ask_photos = State()
    
    # Ожидание района
    ask_district = State()
    
    # Ожидание телефона
    ask_phone = State()
    
    # Показ цен
    show_price_range = State()
    
    # Показ премиум-блока
    show_premium_proof = State()
    
    # Заявка сохранена
    lead_saved = State()

