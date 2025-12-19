"""Клавиатуры бота"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню с основными кнопками"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Рассчитать стоимость по фото")],
            [KeyboardButton(text="Примеры работ")],
            [KeyboardButton(text="Наш адрес и режим работы")],
            [KeyboardButton(text="Позвонить менеджеру")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    return keyboard

# Выбор типа мебели
def get_item_type_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для выбора типа мебели"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Стул")],
            [KeyboardButton(text="Кресло")],
            [KeyboardButton(text="Кухонный уголок")],
            [KeyboardButton(text="Диван прямой")],
            [KeyboardButton(text="Диван угловой")],
            [KeyboardButton(text="Диван + кресло")],
            [KeyboardButton(text="Другое (написать менеджеру)")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите тип мебели"
    )
    return keyboard

# Клавиатура после сохранения заявки
def get_after_lead_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура после сохранения заявки"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Оставить ещё одну заявку")],
            [KeyboardButton(text="Примеры работ")],
            [KeyboardButton(text="Наш адрес и режим работы")],
        ],
        resize_keyboard=True
    )
    return keyboard

# Кнопка "Назад" для дополнительных разделов
def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой "Назад" и "Рассчитать стоимость" """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Назад")],
            [KeyboardButton(text="Рассчитать стоимость по фото")],
        ],
        resize_keyboard=True
    )
    return keyboard

