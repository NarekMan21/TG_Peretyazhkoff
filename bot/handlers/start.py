"""Обработчик команды /start и главного меню"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import OrderStates
from messages import START_MESSAGE, SHOW_PORTFOLIO, SHOW_ADDRESS, SHOW_PHONE
from keyboards import (
    get_main_keyboard,
    get_item_type_keyboard,
    get_back_keyboard
)

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Получена команда /start от пользователя {message.from_user.id}")
    
    # Проверяем, есть ли параметр в команде (например, /start calculate)
    command_parts = message.text.split()
    if len(command_parts) > 1 and command_parts[1] == "calculate":
        # Если перешли по кнопке из канала, сразу открываем расчет стоимости
        await state.set_state(OrderStates.choose_item_type)
        await message.answer(
            "Выберите, какую мебель нужно обновить:",
            reply_markup=get_item_type_keyboard()
        )
    else:
        # Обычный /start - показываем главное меню
        await state.set_state(OrderStates.start)
        await message.answer(
            START_MESSAGE,
            reply_markup=get_main_keyboard()
        )


@router.message(F.text == "Рассчитать стоимость по фото")
async def start_calculation(message: Message, state: FSMContext):
    """Начать расчет стоимости"""
    await state.set_state(OrderStates.choose_item_type)
    await message.answer(
        "Выберите, какую мебель нужно обновить:",
        reply_markup=get_item_type_keyboard()
    )


@router.message(F.text == "Примеры работ")
async def show_portfolio(message: Message, state: FSMContext):
    """Показать примеры работ"""
    await message.answer(
        SHOW_PORTFOLIO,
        reply_markup=get_back_keyboard()
    )


@router.message(F.text == "Наш адрес и режим работы")
async def show_address(message: Message, state: FSMContext):
    """Показать адрес и режим работы"""
    await message.answer(
        SHOW_ADDRESS,
        reply_markup=get_back_keyboard()
    )


@router.message(F.text == "Позвонить менеджеру")
async def show_phone(message: Message, state: FSMContext):
    """Показать телефон менеджера"""
    await message.answer(
        SHOW_PHONE,
        reply_markup=get_back_keyboard()
    )


@router.message(F.text == "Назад")
async def back_to_main(message: Message, state: FSMContext):
    """Вернуться в главное меню"""
    await state.set_state(OrderStates.start)
    await message.answer(
        START_MESSAGE,
        reply_markup=get_main_keyboard()
    )

