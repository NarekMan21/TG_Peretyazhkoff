"""Обработчики общих разделов (портфолио, адрес, телефон)"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from messages import SHOW_PORTFOLIO, SHOW_ADDRESS, SHOW_PHONE
from keyboards import get_main_keyboard

router = Router()


@router.message(F.text == "Примеры работ")
async def show_portfolio(message: Message, state: FSMContext):
    """Показать примеры работ"""
    await message.answer(
        SHOW_PORTFOLIO,
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "Наш адрес и режим работы")
async def show_address(message: Message, state: FSMContext):
    """Показать адрес и режим работы"""
    await message.answer(
        SHOW_ADDRESS,
        reply_markup=get_main_keyboard()
    )


@router.message(F.text == "Позвонить менеджеру")
async def show_phone(message: Message, state: FSMContext):
    """Показать телефон менеджера"""
    await message.answer(
        SHOW_PHONE,
        reply_markup=get_main_keyboard()
    )
