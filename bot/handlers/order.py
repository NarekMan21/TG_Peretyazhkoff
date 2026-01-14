"""Обработчики ветки оформления заявки"""
import json
from aiogram import Router, F, Bot
from aiogram.types import Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext

from states import OrderStates
from messages import (
    ASK_PHOTOS, ASK_DISTRICT, ASK_PHONE, get_price_message,
    PREMIUM_PROOF, LEAD_SAVED, ERROR_INVALID_PHONE, ERROR_NO_PHOTOS
)
from keyboards import get_item_type_keyboard, get_after_lead_keyboard, get_continue_after_photos_keyboard
from database import save_lead
from utils import validate_phone, normalize_phone
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import MANAGER_CHAT_ID

router = Router()

# Типы мебели
ITEM_TYPES = [
    "Стул", "Кресло", "Кухонный уголок",
    "Диван прямой", "Диван угловой", "Диван + кресло"
]


@router.message(OrderStates.choose_item_type, F.text.in_(ITEM_TYPES))
async def process_item_type(message: Message, state: FSMContext):
    """Обработка выбора типа мебели"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Обработка выбора типа мебели: {message.text} от пользователя {message.from_user.id}")
    
    item_type = message.text
    await state.update_data(item_type=item_type)
    await state.set_state(OrderStates.ask_photos)
    await message.answer(ASK_PHOTOS)


@router.message(OrderStates.choose_item_type, F.text == "Другое (написать менеджеру)")
async def other_item_type(message: Message, state: FSMContext):
    """Если выбрано 'Другое' - показать телефон менеджера"""
    from messages import SHOW_PHONE
    from keyboards import get_back_keyboard
    await message.answer(
        SHOW_PHONE,
        reply_markup=get_back_keyboard()
    )


@router.message(OrderStates.ask_photos, F.photo)
async def process_photos(message: Message, state: FSMContext):
    """Обработка получения фото"""
    data = await state.get_data()
    
    # Получаем file_id фото
    photo = message.photo[-1]  # Берем фото наибольшего размера
    file_id = photo.file_id
    
    # Сохраняем фото в состоянии
    photos = data.get("photos", [])
    photos.append(file_id)
    await state.update_data(photos=photos)
    
    # Если это первое фото, подтверждаем получение
    if len(photos) == 1:
        await message.answer(
            "✅ Фото получено. Можете отправить ещё фото или нажмите кнопку ниже для перехода к следующему шагу.",
            reply_markup=get_continue_after_photos_keyboard()
        )
    else:
        await message.answer(
            f"✅ Получено {len(photos)} фото. Можете отправить ещё или нажмите кнопку ниже для перехода к следующему шагу.",
            reply_markup=get_continue_after_photos_keyboard()
        )


@router.message(OrderStates.ask_photos, F.text == "✅ Готово, перейти дальше")
async def continue_after_photos(message: Message, state: FSMContext):
    """Обработка нажатия кнопки продолжения"""
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if not photos:
        await message.answer(ERROR_NO_PHOTOS)
        return
    
    # Переходим к следующему шагу
    await state.set_state(OrderStates.ask_district)
    await message.answer(ASK_DISTRICT)


@router.message(OrderStates.ask_photos)
async def process_photos_text(message: Message, state: FSMContext):
    """Обработка текста в состоянии ожидания фото - переходим к следующему шагу если фото есть"""
    data = await state.get_data()
    photos = data.get("photos", [])
    
    if not photos:
        await message.answer(ERROR_NO_PHOTOS)
        return
    
    # Если фото есть, переходим к следующему шагу
    await state.set_state(OrderStates.ask_district)
    await message.answer(ASK_DISTRICT)


@router.message(OrderStates.ask_district)
async def process_district(message: Message, state: FSMContext):
    """Обработка ввода района"""
    district = message.text.strip()
    
    if not district:
        await message.answer("Пожалуйста, укажите район.")
        return
    
    await state.update_data(district=district)
    await state.set_state(OrderStates.ask_phone)
    await message.answer(ASK_PHONE)


@router.message(OrderStates.ask_phone)
async def process_phone(message: Message, state: FSMContext, bot: Bot):
    """Обработка ввода телефона"""
    phone = message.text.strip()
    
    # Валидация телефона
    if not validate_phone(phone):
        await message.answer(ERROR_INVALID_PHONE)
        return
    
    # Нормализуем телефон
    normalized_phone = normalize_phone(phone)
    
    # Получаем все данные из состояния
    data = await state.get_data()
    item_type = data.get("item_type")
    district = data.get("district")
    photos = data.get("photos", [])
    
    if not photos:
        await message.answer(ERROR_NO_PHOTOS)
        await state.set_state(OrderStates.ask_photos)
        return
    
    # Показываем цены
    price_message = get_price_message(item_type)
    await message.answer(price_message)
    
    # Показываем премиум-блок
    await message.answer(PREMIUM_PROOF)
    
    # Сохраняем заявку в БД
    username = message.from_user.username
    user_id = message.from_user.id
    
    lead_id = await save_lead(
        telegram_user_id=user_id,
        username=username,
        item_type=item_type,
        district=district,
        phone=normalized_phone,
        photos=photos
    )
    
    # Отправляем заявку менеджеру
    from messages import format_lead_for_manager
    from datetime import datetime
    
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    manager_message = format_lead_for_manager(
        username=username or "без username",
        user_id=user_id,
        item_type=item_type,
        district=district,
        phone=normalized_phone,
        created_at=created_at,
        photo_count=len(photos)
    )
    
    # Отправляем текст заявки
    await bot.send_message(
        chat_id=MANAGER_CHAT_ID,
        text=manager_message
    )
    
    # Отправляем фото медиа-группой
    if photos:
        media_group = [
            InputMediaPhoto(media=file_id) for file_id in photos
        ]
        await bot.send_media_group(
            chat_id=MANAGER_CHAT_ID,
            media=media_group
        )
    
    # Завершаем заявку
    await message.answer(
        LEAD_SAVED.replace("<номер>", normalized_phone),
        reply_markup=get_after_lead_keyboard()
    )
    
    # Очищаем данные состояния
    await state.clear()

