"""Обработчик команды /start - упрощенная версия"""
from aiogram import Router, F, Bot
from aiogram.types import Message, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging

from messages import START_MESSAGE, format_lead_for_manager
from keyboards import get_main_keyboard
from database import save_lead
from config import MANAGER_CHAT_ID

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text.startswith("/start"))
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    """Обработчик команды /start - обрабатывает обычный /start и deep linking"""
    # Очищаем состояние
    await state.clear()
    
    # Парсим параметры из команды /start (например, /start calculate или /start?calculate)
    command_text = message.text
    start_param = None
    
    # Обрабатываем формат /start параметр или /start?параметр
    if " " in command_text:
        # Формат: /start calculate
        parts = command_text.split(maxsplit=1)
        if len(parts) > 1:
            start_param = parts[1].strip()
    elif "?" in command_text:
        # Формат: /start?calculate (редко используется в Telegram, но на всякий случай)
        parts = command_text.split("?", 1)
        if len(parts) > 1:
            start_param = parts[1].strip()
    
    username = message.from_user.username
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Формируем текст заявки в зависимости от наличия параметра
    if start_param:
        source_text = f"Пользователь перешел в бота по ссылке (параметр: {start_param})"
        logger.info(f"Получена команда /start с параметром '{start_param}' от пользователя {user_id}")
    else:
        source_text = "Пользователь перешел в бота через /start"
        logger.info(f"Получена команда /start от пользователя {user_id}")
    
    # Пытаемся сохранить заявку в БД
    lead_id = None
    try:
        lead_id = await save_lead(
            telegram_user_id=user_id,
            username=username,
            message_text=source_text
        )
        logger.info(f"Создана заявка #{lead_id} от пользователя {user_id}")
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
            message_text=source_text,
            created_at=created_at,
            photo_count=0
        )
        
        await bot.send_message(
            chat_id=MANAGER_CHAT_ID,
            text=manager_message
        )
        logger.info(f"Заявка отправлена менеджеру от пользователя {user_id}")
    except Exception as e:
        logger.error(f"Ошибка при отправке заявки менеджеру: {e}")
    
    # Показываем приветствие
    await message.answer(
        START_MESSAGE,
        reply_markup=get_main_keyboard()
    )
