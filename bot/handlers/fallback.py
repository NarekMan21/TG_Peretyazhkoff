"""Fallback обработчик для необработанных сообщений"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
import logging

from states import OrderStates
from keyboards import get_main_keyboard

router = Router()
logger = logging.getLogger(__name__)


# Fallback НЕ должен обрабатывать сообщения в состоянии choose_item_type
# Используем фильтр для исключения этого состояния
@router.message(~StateFilter(OrderStates.choose_item_type))
async def fallback_handler(message: Message, state: FSMContext):
    """Обработчик для всех необработанных сообщений (кроме состояния choose_item_type)"""
    current_state = await state.get_state()
    
    # Логируем для отладки
    logger.info(f"Fallback обработчик: сообщение '{message.text}' от пользователя {message.from_user.id}, состояние: {current_state}")
    
    # Если пользователь в начальном состоянии, показываем главное меню
    if current_state == OrderStates.start or current_state is None:
        await state.set_state(OrderStates.start)
        await message.answer(
            "Пожалуйста, выберите действие из меню:",
            reply_markup=get_main_keyboard()
        )
    else:
        # В других состояниях просим следовать инструкциям
        await message.answer(
            "Пожалуйста, следуйте инструкциям бота. Используйте кнопки меню."
        )
