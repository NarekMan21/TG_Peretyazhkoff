"""Все текстовые сообщения бота"""
from typing import Optional

# Приветствие при /start
START_MESSAGE = """Здравствуйте! 👋

Вас приветствует фабрика по перетяжке мебели Перетяжкофф в Ростове-на-Дону.

Профессиональная перетяжка и ремонт мягкой мебели.
Собственный чистый цех, профессиональное оборудование, импортные ткани, гарантия 18–36 месяцев.

Напишите мне, что вас интересует, или отправьте фото мебели — я передам вашу заявку менеджеру! 📸"""

# Примеры работ
SHOW_PORTFOLIO = """Примеры наших работ вы можете посмотреть на сайте в разделе «Примеры работ» или в нашем Телеграм-канале.

https://xn--e1aadqubirva0j.xn--p1ai/rostovnadonu/#examples"""

# Адрес и режим работы
SHOW_ADDRESS = """Наш офис и цех:
Ростов-на-Дону, ул. 2-я Кольцевая, 93/24.
Работаем ежедневно с 9:00 до 23:00.
Телефон: +7 (951) 505-75-00 (есть WhatsApp)."""

# Телефон менеджера
SHOW_PHONE = """Вы можете связаться с менеджером Перетяжкофф по телефону:
+7 (951) 505-75-00
или написать в WhatsApp: https://wa.me/+79515057500"""

# Сообщение после получения заявки
LEAD_RECEIVED = """Спасибо! Ваша заявка передана менеджеру Перетяжкофф.

В течение 15–30 минут наш менеджер свяжется с вами для уточнения деталей, подбора ткани и согласования даты выезда.

Если у вас есть вопросы, напишите мне — я передам их менеджеру! 💬"""

# Сообщение для менеджера
def format_lead_for_manager(
    username: Optional[str],
    user_id: int,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    message_text: Optional[str] = None,
    item_type: Optional[str] = None,
    district: Optional[str] = None,
    phone: Optional[str] = None,
    created_at: str = "",
    photo_count: int = 0
) -> str:
    """Форматировать заявку для отправки менеджеру"""
    # Формируем имя пользователя
    user_name_parts = []
    if first_name:
        user_name_parts.append(first_name)
    if last_name:
        user_name_parts.append(last_name)
    full_name = " ".join(user_name_parts).strip() if user_name_parts else None
    
    # Форматируем информацию о клиенте
    if username:
        # Если есть username, показываем его как ссылку
        client_info = f"👤 Клиент: @{username}"
        if full_name:
            client_info += f" ({full_name})"
        client_info += f"\n   ID: {user_id}"
        client_info += f"\n   💬 Ответить: tg://user?id={user_id}"
    else:
        # Если нет username, показываем имя и ссылку для ответа
        if full_name:
            client_info = f"👤 Клиент: {full_name}"
        else:
            client_info = f"👤 Клиент: (имя не указано)"
        client_info += f"\n   ID: {user_id}"
        client_info += f"\n   💬 Ответить: tg://user?id={user_id}"
    
    parts = [
        "📋 Новая заявка от бота Перетяжкофф",
        "",
        client_info,
        f"📅 Дата: {created_at}",
    ]
    
    if message_text:
        parts.append(f"💬 Сообщение: {message_text}")
    if item_type:
        parts.append(f"🪑 Тип мебели: {item_type}")
    if district:
        parts.append(f"📍 Район: {district}")
    if phone:
        parts.append(f"📞 Телефон: {phone}")
    
    if photo_count > 0:
        parts.append(f"\n📸 Фото ({photo_count} шт.):")
    else:
        parts.append("\n📸 Фото не приложены")
    
    return "\n".join(parts)

# Ошибки
ERROR_INVALID_PHONE = "Пожалуйста, укажите номер телефона в правильном формате (например: +7 951 505-75-00 или 89515057500)."
