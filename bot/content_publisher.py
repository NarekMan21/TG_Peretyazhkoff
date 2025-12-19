"""Модуль для публикации контента в Telegram-канал"""
import logging
from typing import Optional, List
from aiogram import Bot
from aiogram.types import InputMediaPhoto, InputMediaVideo, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.exceptions import TelegramBadRequest, TelegramAPIError

from config import BOT_TOKEN, CHANNEL_ID
from database import get_case, get_workshop_post

logger = logging.getLogger(__name__)


class ContentPublisher:
    """Класс для публикации контента в Telegram-канал"""
    
    BOT_USERNAME = "peretiazhkoff_bot"  # Username бота без @
    
    def __init__(self):
        self.bot = Bot(token=BOT_TOKEN)
        self.channel_id = CHANNEL_ID
    
    async def close(self):
        """Закрыть сессию бота"""
        await self.bot.session.close()
    
    def _get_calculate_button(self) -> InlineKeyboardMarkup:
        """Создать inline-клавиатуру с кнопкой 'Рассчитать стоимость по фото'"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="Рассчитать стоимость по фото",
                url=f"https://t.me/{self.BOT_USERNAME}?start=calculate"
            )]
        ])
        return keyboard
    
    async def publish_case(self, case_id: int) -> Optional[int]:
        """Опубликовать кейс в канал
        
        Args:
            case_id: ID кейса из БД
            
        Returns:
            int: ID сообщения в канале или None при ошибке
        """
        if not self.channel_id:
            logger.error("CHANNEL_ID не установлен в конфигурации")
            return None
        
        case = await get_case(case_id)
        if not case:
            logger.error(f"Кейс с ID {case_id} не найден")
            return None
        
        try:
            # Формируем текст поста
            text = self._format_case_text(case)
            
            # Если есть фото, отправляем медиа-группу
            if case.get('photos') and len(case['photos']) > 0:
                media_group = []
                photos = case['photos']
                
                # Первое фото с текстом
                if photos[0].startswith('http') or photos[0].startswith('file'):
                    # Если это URL или путь к файлу
                    media_group.append(InputMediaPhoto(
                        media=FSInputFile(photos[0]) if not photos[0].startswith('http') else photos[0],
                        caption=text,
                        parse_mode='HTML'
                    ))
                else:
                    # Если это file_id из Telegram
                    media_group.append(InputMediaPhoto(
                        media=photos[0],
                        caption=text,
                        parse_mode='HTML'
                    ))
                
                # Остальные фото без текста
                for photo in photos[1:]:
                    if photo.startswith('http') or photo.startswith('file'):
                        media_group.append(InputMediaPhoto(
                            media=FSInputFile(photo) if not photo.startswith('http') else photo
                        ))
                    else:
                        media_group.append(InputMediaPhoto(media=photo))
                
                # Отправляем медиа-группу
                messages = await self.bot.send_media_group(
                    chat_id=self.channel_id,
                    media=media_group
                )
                message_id = messages[0].message_id if messages else None
                
                # Добавляем кнопку к первому сообщению медиа-группы
                if message_id:
                    try:
                        # Редактируем caption первого сообщения, добавляя кнопку
                        await self.bot.edit_message_caption(
                            chat_id=self.channel_id,
                            message_id=message_id,
                            caption=text,
                            parse_mode='HTML',
                            reply_markup=self._get_calculate_button()
                        )
                    except Exception as e:
                        logger.warning(f"Не удалось добавить кнопку к медиа-группе: {e}")
                        # Если не получилось, отправляем отдельное сообщение с кнопкой
                        try:
                            await self.bot.send_message(
                                chat_id=self.channel_id,
                                text="💬 Хотите рассчитать стоимость?",
                                reply_markup=self._get_calculate_button(),
                                reply_to_message_id=message_id
                            )
                        except Exception as e2:
                            logger.error(f"Не удалось отправить сообщение с кнопкой: {e2}")
            else:
                # Если фото нет, отправляем только текст
                message = await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=text,
                    parse_mode='HTML',
                    reply_markup=self._get_calculate_button()
                )
                message_id = message.message_id
            
            logger.info(f"Кейс {case_id} успешно опубликован в канал. Message ID: {message_id}")
            return message_id
            
        except TelegramBadRequest as e:
            logger.error(f"Ошибка Telegram API при публикации кейса {case_id}: {e}")
            return None
        except TelegramAPIError as e:
            logger.error(f"Ошибка API при публикации кейса {case_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при публикации кейса {case_id}: {e}")
            return None
    
    async def publish_workshop_post(self, post_id: int) -> Optional[int]:
        """Опубликовать пост "из цеха" в канал
        
        Args:
            post_id: ID поста из БД
            
        Returns:
            int: ID сообщения в канале или None при ошибке
        """
        if not self.channel_id:
            logger.error("CHANNEL_ID не установлен в конфигурации")
            return None
        
        post = await get_workshop_post(post_id)
        if not post:
            logger.error(f"Пост с ID {post_id} не найден")
            return None
        
        try:
            # Формируем текст поста
            text = self._format_workshop_post_text(post)
            
            # Отправляем в зависимости от типа медиа
            if post['media_type'] == 'video':
                if post['media_file_id']:
                    if post['media_file_id'].startswith('http') or post['media_file_id'].startswith('file'):
                        media = FSInputFile(post['media_file_id']) if not post['media_file_id'].startswith('http') else post['media_file_id']
                    else:
                        media = post['media_file_id']
                    
                    message = await self.bot.send_video(
                        chat_id=self.channel_id,
                        video=media,
                        caption=text,
                        parse_mode='HTML',
                        reply_markup=self._get_calculate_button()
                    )
                else:
                    # Если нет видео, отправляем только текст
                    message = await self.bot.send_message(
                        chat_id=self.channel_id,
                        text=text,
                        parse_mode='HTML',
                        reply_markup=self._get_calculate_button()
                    )
            else:
                # Фото по умолчанию
                if post['media_file_id']:
                    if post['media_file_id'].startswith('http') or post['media_file_id'].startswith('file'):
                        media = FSInputFile(post['media_file_id']) if not post['media_file_id'].startswith('http') else post['media_file_id']
                    else:
                        media = post['media_file_id']
                    
                    message = await self.bot.send_photo(
                        chat_id=self.channel_id,
                        photo=media,
                        caption=text,
                        parse_mode='HTML',
                        reply_markup=self._get_calculate_button()
                    )
                else:
                    # Если нет фото, отправляем только текст
                    message = await self.bot.send_message(
                        chat_id=self.channel_id,
                        text=text,
                        parse_mode='HTML',
                        reply_markup=self._get_calculate_button()
                    )
            
            logger.info(f"Пост {post_id} успешно опубликован в канал. Message ID: {message.message_id}")
            return message.message_id
            
        except TelegramBadRequest as e:
            logger.error(f"Ошибка Telegram API при публикации поста {post_id}: {e}")
            return None
        except TelegramAPIError as e:
            logger.error(f"Ошибка API при публикации поста {post_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при публикации поста {post_id}: {e}")
            return None
    
    def _format_case_text(self, case: dict) -> str:
        """Форматировать текст кейса для публикации"""
        text_parts = []
        
        # Заголовок
        text_parts.append(f"<b>{case['title']}</b>\n")
        
        # Что было
        if case.get('description_before'):
            text_parts.append(f"<b>Что было:</b>\n{case['description_before']}\n")
        
        # Что сделали
        if case.get('description_after'):
            text_parts.append(f"<b>Что сделали:</b>\n{case['description_after']}\n")
        
        # Материалы
        materials = []
        if case.get('fabric_type'):
            materials.append(f"Ткань: {case['fabric_type']}")
        if case.get('filler_type'):
            materials.append(f"Наполнитель: {case['filler_type']}")
        
        if materials:
            text_parts.append(f"<b>Материалы:</b>\n" + "\n".join(materials) + "\n")
        
        # Цена
        if case.get('price'):
            text_parts.append(f"<b>Стоимость:</b> {case['price']:.0f} ₽\n")
        
        # Отзыв клиента
        if case.get('client_review'):
            text_parts.append(f"<b>Отзыв клиента:</b>\n<i>«{case['client_review']}»</i>\n")
        
        # Хештеги
        text_parts.append("\n#Перетяжкофф #ПеретяжкаМебели #РостовНаДону")
        
        return "\n".join(text_parts)
    
    def _format_workshop_post_text(self, post: dict) -> str:
        """Форматировать текст поста "из цеха" для публикации"""
        text_parts = []
        
        # Заголовок
        if post.get('title'):
            text_parts.append(f"<b>{post['title']}</b>\n")
        
        # Описание
        if post.get('description'):
            text_parts.append(post['description'])
        
        # Хештеги
        text_parts.append("\n#Перетяжкофф #ИзЦеха #Производство")
        
        return "\n".join(text_parts)


# Функция для удобного использования
async def publish_case_to_channel(case_id: int) -> Optional[int]:
    """Опубликовать кейс в канал (удобная функция)"""
    publisher = ContentPublisher()
    try:
        result = await publisher.publish_case(case_id)
        return result
    finally:
        await publisher.close()


async def publish_workshop_post_to_channel(post_id: int) -> Optional[int]:
    """Опубликовать пост "из цеха" в канал (удобная функция)"""
    publisher = ContentPublisher()
    try:
        result = await publisher.publish_workshop_post(post_id)
        return result
    finally:
        await publisher.close()
