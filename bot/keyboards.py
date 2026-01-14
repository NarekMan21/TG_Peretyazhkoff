"""Клавиатуры бота"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Простое главное меню
def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню с простыми кнопками"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Примеры работ")],
            [KeyboardButton(text="Наш адрес и режим работы")],
            [KeyboardButton(text="Позвонить менеджеру")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Напишите сообщение или отправьте фото"
    )
    return keyboard
