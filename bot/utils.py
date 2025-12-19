"""Утилиты для бота"""
import re
from typing import Optional
from messages import PRICES


def validate_phone(phone: str) -> bool:
    """Валидация номера телефона (гибкая, принимает разные форматы)
    
    Принимает форматы:
    - +7 951 505-75-00
    - 89515057500
    - 8 (951) 505-75-00
    - +79515057500
    - 7 951 505 75 00
    """
    # Удаляем все пробелы, дефисы, скобки
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Проверяем, что остались только цифры и возможно + в начале
    if not re.match(r'^\+?\d+$', cleaned):
        return False
    
    # Убираем + если есть
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Проверяем, что номер начинается с 7 или 8 и имеет правильную длину
    if cleaned.startswith('7') and len(cleaned) == 11:
        return True
    if cleaned.startswith('8') and len(cleaned) == 11:
        return True
    
    return False


def normalize_phone(phone: str) -> str:
    """Нормализовать номер телефона к формату +7 XXX XXX-XX-XX"""
    # Удаляем все пробелы, дефисы, скобки
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Убираем + если есть
    if cleaned.startswith('+'):
        cleaned = cleaned[1:]
    
    # Заменяем 8 на 7 в начале
    if cleaned.startswith('8'):
        cleaned = '7' + cleaned[1:]
    
    # Форматируем: +7 XXX XXX-XX-XX
    if len(cleaned) == 11 and cleaned.startswith('7'):
        return f"+7 {cleaned[1:4]} {cleaned[4:7]}-{cleaned[7:9]}-{cleaned[9:11]}"
    
    return phone  # Возвращаем как есть, если не удалось нормализовать


def get_price_by_item_type(item_type: str) -> int:
    """Получить цену по типу мебели"""
    return PRICES.get(item_type, 0)


def format_phone_for_display(phone: str) -> str:
    """Форматировать телефон для отображения"""
    normalized = normalize_phone(phone)
    return normalized

