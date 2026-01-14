"""Упрощенная обработка сообщений от клиентов - любое сообщение/фото = заявка"""
from aiogram import Router, F, Bot
from aiogram.types import Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging

from messages import LEAD_RECEIVED, format_lead_for_manager
from keyboards import get_main_keyboard
from database import save_lead
from config import MANAGER_CHAT_ID

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.photo)
async def handle_photo(message: Message, state: FSMContext, bot: Bot):
    """Обработка фото от клиента - создаем заявку"""
    logger.info(f"Получено фото от пользователя {message.from_user.id}")
    
    # Получаем file_id фото
    photo = message.photo[-1]  # Берем фото наибольшего размера
    file_id = photo.file_id
    
    # Получаем caption если есть
    caption = message.caption or ""
    
    username = message.from_user.username
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Пытаемся сохранить заявку в БД
    lead_id = None
    try:
        lead_id = await save_lead(
            telegram_user_id=user_id,
            username=username,
            photos=[file_id],
            message_text=caption if caption else None
        )
        logger.info(f"Создана заявка #{lead_id} с фото от пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении заявки в БД: {e}")
    
    # Отправляем заявку менеджеру (даже если сохранение в БД не удалось)
    try:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        manager_message = format_lead_for_manager(
            username=username,
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            message_text=caption if caption else None,
            created_at=created_at,
            photo_count=1
        )
        
        # Отправляем текст заявки
        await bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=manager_message
        )
        
        # Отправляем фото
        await bot.send_photo(
            chat_id=MANAGER_CHAT_ID,
            photo=file_id
        )
        
        logger.info(f"Заявка с фото отправлена менеджеру от пользователя {user_id}")
        
        # Подтверждаем клиенту
        await message.answer(
            LEAD_RECEIVED,
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке заявки менеджеру: {e}")
        await message.answer(
            "Произошла ошибка при отправке заявки. Пожалуйста, попробуйте еще раз или свяжитесь с менеджером напрямую.",
            reply_markup=get_main_keyboard()
        )


@router.message(F.text)
async def handle_text(message: Message, state: FSMContext, bot: Bot):
    """Обработка текстового сообщения от клиента - создаем заявку"""
    text = message.text.strip()
    
    # Пропускаем команды и кнопки меню (они обрабатываются другими handlers)
    if text in ["Примеры работ", "Наш адрес и режим работы", "Позвонить менеджеру"]:
        return
    
    # Пропускаем команды начинающиеся с /start
    if text.startswith("/start"):
        return
    
    logger.info(f"Получено текстовое сообщение от пользователя {message.from_user.id}: {text[:50]}")
    
    username = message.from_user.username
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Пытаемся сохранить заявку в БД
    lead_id = None
    try:
        lead_id = await save_lead(
            telegram_user_id=user_id,
            username=username,
            message_text=text
        )
        logger.info(f"Создана заявка #{lead_id} с текстом от пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при сохранении заявки в БД: {e}")
    
    # Отправляем заявку менеджеру (даже если сохранение в БД не удалось)
    try:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        manager_message = format_lead_for_manager(
            username=username,
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            message_text=text,
            created_at=created_at,
            photo_count=0
        )
        
        await bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=manager_message
        )
        
        logger.info(f"Заявка с текстом отправлена менеджеру от пользователя {user_id}")
        
        # Подтверждаем клиенту
        await message.answer(
            LEAD_RECEIVED,
            reply_markup=get_main_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка при отправке заявки менеджеру: {e}")
        await message.answer(
            "Произошла ошибка при отправке заявки. Пожалуйста, попробуйте еще раз или свяжитесь с менеджером напрямую.",
            reply_markup=get_main_keyboard()
        )
