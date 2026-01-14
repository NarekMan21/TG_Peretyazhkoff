"""Работа с базой данных SQLite"""
import aiosqlite
import json
from datetime import datetime
from typing import Optional, List, Dict
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import DB_PATH


async def init_db():
    """Инициализация базы данных - создание таблиц"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Проверяем существующую схему таблицы leads
        needs_migration = False
        try:
            async with db.execute("PRAGMA table_info(leads)") as cursor:
                columns_info = await cursor.fetchall()
                if columns_info:
                    # Проверяем, есть ли колонка message_text и какие ограничения NOT NULL есть
                    column_names = [row[1] for row in columns_info]
                    if 'message_text' not in column_names:
                        needs_migration = True
                    # Проверяем NOT NULL ограничения для item_type, district, phone
                    for col_info in columns_info:
                        col_name = col_info[1]
                        not_null = col_info[3]  # 3-й элемент - NOT NULL флаг
                        if col_name in ['item_type', 'district', 'phone'] and not_null:
                            needs_migration = True
                            break
        except Exception:
            # Таблица не существует или ошибка - создадим новую
            pass
        
        # Если нужна миграция, пересоздаем таблицу
        if needs_migration:
            try:
                # Создаем временную таблицу с правильной схемой
                await db.execute("""
                    CREATE TABLE IF NOT EXISTS leads_new (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        telegram_user_id INTEGER NOT NULL,
                        username TEXT,
                        item_type TEXT,
                        district TEXT,
                        phone TEXT,
                        photos TEXT,
                        message_text TEXT,
                        created_at TEXT NOT NULL,
                        source TEXT DEFAULT 'TelegramBot_Peretiazhkoff'
                    )
                """)
                
                # Копируем данные из старой таблицы (если она существует)
                try:
                    await db.execute("""
                        INSERT INTO leads_new 
                        (id, telegram_user_id, username, item_type, district, phone, photos, created_at, source)
                        SELECT id, telegram_user_id, username, item_type, district, phone, photos, created_at, source
                        FROM leads
                    """)
                except Exception:
                    # Если ошибка при копировании - просто продолжаем с пустой таблицей
                    pass
                
                # Удаляем старую таблицу
                await db.execute("DROP TABLE IF EXISTS leads")
                
                # Переименовываем новую таблицу
                await db.execute("ALTER TABLE leads_new RENAME TO leads")
                
                await db.commit()
            except Exception as e:
                # Если миграция не удалась, создадим таблицу заново
                await db.execute("DROP TABLE IF EXISTS leads")
                await db.execute("DROP TABLE IF EXISTS leads_new")
        
        # Создаем таблицу с правильной схемой (если её еще нет)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL,
                username TEXT,
                item_type TEXT,
                district TEXT,
                phone TEXT,
                photos TEXT,
                message_text TEXT,
                created_at TEXT NOT NULL,
                source TEXT DEFAULT 'TelegramBot_Peretiazhkoff'
            )
        """)
        
        # Индекс для быстрого поиска по user_id
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id ON leads(telegram_user_id)
        """)
        
        # Индекс для сортировки по дате
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at ON leads(created_at)
        """)
        
        # Таблица кейсов (истории диванов)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description_before TEXT,
                description_after TEXT,
                fabric_type TEXT,
                filler_type TEXT,
                price REAL,
                client_review TEXT,
                photos TEXT,
                published BOOLEAN DEFAULT 0,
                published_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        
        # Таблица постов "из цеха"
        await db.execute("""
            CREATE TABLE IF NOT EXISTS workshop_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                media_type TEXT NOT NULL,
                media_file_id TEXT,
                published BOOLEAN DEFAULT 0,
                published_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
            )
        """)
        
        # Индексы для кейсов и постов
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_cases_published ON cases(published)
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_workshop_published ON workshop_posts(published)
        """)
        
        await db.commit()


async def save_lead(
    telegram_user_id: int,
    username: Optional[str],
    item_type: Optional[str] = None,
    district: Optional[str] = None,
    phone: Optional[str] = None,
    photos: Optional[List[str]] = None,
    message_text: Optional[str] = None
) -> int:
    """Сохранить заявку в базу данных (упрощенная версия - все поля опциональны)
    
    Returns:
        int: ID сохраненной заявки
    """
    async with aiosqlite.connect(DB_PATH) as db:
        photos_json = json.dumps(photos or [])
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = await db.execute("""
            INSERT INTO leads (
                telegram_user_id, username, item_type, district, 
                phone, photos, message_text, created_at, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            telegram_user_id, username, item_type, district,
            phone, photos_json, message_text, created_at, "TelegramBot_Peretiazhkoff"
        ))
        
        await db.commit()
        return cursor.lastrowid


async def get_lead(lead_id: int) -> Optional[Dict]:
    """Получить заявку по ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM leads WHERE id = ?
        """, (lead_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                lead = dict(row)
                lead['photos'] = json.loads(lead['photos']) if lead['photos'] else []
                return lead
            return None


async def get_all_leads(limit: int = 100, offset: int = 0) -> List[Dict]:
    """Получить все заявки с пагинацией"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM leads 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, offset)) as cursor:
            rows = await cursor.fetchall()
            leads = []
            for row in rows:
                lead = dict(row)
                lead['photos'] = json.loads(lead['photos']) if lead['photos'] else []
                leads.append(lead)
            return leads


async def get_leads_count() -> int:
    """Получить общее количество заявок"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM leads") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0


async def get_leads_by_item_type() -> Dict[str, int]:
    """Получить статистику по типам мебели"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT item_type, COUNT(*) as count 
            FROM leads 
            WHERE item_type IS NOT NULL
            GROUP BY item_type
        """) as cursor:
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}


# ========== Функции для работы с кейсами ==========

async def save_case(
    title: str,
    description_before: Optional[str] = None,
    description_after: Optional[str] = None,
    fabric_type: Optional[str] = None,
    filler_type: Optional[str] = None,
    price: Optional[float] = None,
    client_review: Optional[str] = None,
    photos: Optional[List[str]] = None
) -> int:
    """Сохранить кейс в базу данных
    
    Returns:
        int: ID сохраненного кейса
    """
    async with aiosqlite.connect(DB_PATH) as db:
        photos_json = json.dumps(photos or [])
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = await db.execute("""
            INSERT INTO cases (
                title, description_before, description_after,
                fabric_type, filler_type, price, client_review,
                photos, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            title, description_before, description_after,
            fabric_type, filler_type, price, client_review,
            photos_json, created_at
        ))
        
        await db.commit()
        return cursor.lastrowid


async def get_case(case_id: int) -> Optional[Dict]:
    """Получить кейс по ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM cases WHERE id = ?
        """, (case_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                case = dict(row)
                case['photos'] = json.loads(case['photos']) if case['photos'] else []
                return case
            return None


async def get_all_cases(limit: int = 100, offset: int = 0, published_only: bool = False) -> List[Dict]:
    """Получить все кейсы с пагинацией"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM cases"
        params = []
        
        if published_only:
            query += " WHERE published = 1"
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            cases = []
            for row in rows:
                case = dict(row)
                case['photos'] = json.loads(case['photos']) if case['photos'] else []
                cases.append(case)
            return cases


async def update_case(
    case_id: int,
    title: Optional[str] = None,
    description_before: Optional[str] = None,
    description_after: Optional[str] = None,
    fabric_type: Optional[str] = None,
    filler_type: Optional[str] = None,
    price: Optional[float] = None,
    client_review: Optional[str] = None,
    photos: Optional[List[str]] = None
) -> bool:
    """Обновить кейс"""
    async with aiosqlite.connect(DB_PATH) as db:
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description_before is not None:
            updates.append("description_before = ?")
            params.append(description_before)
        if description_after is not None:
            updates.append("description_after = ?")
            params.append(description_after)
        if fabric_type is not None:
            updates.append("fabric_type = ?")
            params.append(fabric_type)
        if filler_type is not None:
            updates.append("filler_type = ?")
            params.append(filler_type)
        if price is not None:
            updates.append("price = ?")
            params.append(price)
        if client_review is not None:
            updates.append("client_review = ?")
            params.append(client_review)
        if photos is not None:
            updates.append("photos = ?")
            params.append(json.dumps(photos))
        
        if not updates:
            return False
        
        updates.append("updated_at = ?")
        params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        params.append(case_id)
        
        await db.execute(f"""
            UPDATE cases SET {', '.join(updates)} WHERE id = ?
        """, params)
        await db.commit()
        return True


async def mark_case_published(case_id: int) -> bool:
    """Отметить кейс как опубликованный"""
    async with aiosqlite.connect(DB_PATH) as db:
        published_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await db.execute("""
            UPDATE cases SET published = 1, published_at = ? WHERE id = ?
        """, (published_at, case_id))
        await db.commit()
        return True


async def delete_case(case_id: int) -> bool:
    """Удалить кейс"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM cases WHERE id = ?", (case_id,))
        await db.commit()
        return True


# ========== Функции для работы с постами "из цеха" ==========

async def save_workshop_post(
    title: str,
    description: Optional[str] = None,
    media_type: str = "photo",
    media_file_id: Optional[str] = None
) -> int:
    """Сохранить пост "из цеха" в базу данных
    
    Args:
        title: Заголовок поста
        description: Описание
        media_type: Тип медиа (photo, video)
        media_file_id: file_id медиа из Telegram
    
    Returns:
        int: ID сохраненного поста
    """
    async with aiosqlite.connect(DB_PATH) as db:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = await db.execute("""
            INSERT INTO workshop_posts (
                title, description, media_type, media_file_id, created_at
            ) VALUES (?, ?, ?, ?, ?)
        """, (title, description, media_type, media_file_id, created_at))
        
        await db.commit()
        return cursor.lastrowid


async def get_workshop_post(post_id: int) -> Optional[Dict]:
    """Получить пост "из цеха" по ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM workshop_posts WHERE id = ?
        """, (post_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None


async def get_all_workshop_posts(limit: int = 100, offset: int = 0, published_only: bool = False) -> List[Dict]:
    """Получить все посты "из цеха" с пагинацией"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        query = "SELECT * FROM workshop_posts"
        params = []
        
        if published_only:
            query += " WHERE published = 1"
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def update_workshop_post(
    post_id: int,
    title: Optional[str] = None,
    description: Optional[str] = None,
    media_type: Optional[str] = None,
    media_file_id: Optional[str] = None
) -> bool:
    """Обновить пост "из цеха" """
    async with aiosqlite.connect(DB_PATH) as db:
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if media_type is not None:
            updates.append("media_type = ?")
            params.append(media_type)
        if media_file_id is not None:
            updates.append("media_file_id = ?")
            params.append(media_file_id)
        
        if not updates:
            return False
        
        updates.append("updated_at = ?")
        params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        params.append(post_id)
        
        await db.execute(f"""
            UPDATE workshop_posts SET {', '.join(updates)} WHERE id = ?
        """, params)
        await db.commit()
        return True


async def mark_workshop_post_published(post_id: int) -> bool:
    """Отметить пост "из цеха" как опубликованный"""
    async with aiosqlite.connect(DB_PATH) as db:
        published_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        await db.execute("""
            UPDATE workshop_posts SET published = 1, published_at = ? WHERE id = ?
        """, (published_at, post_id))
        await db.commit()
        return True


async def delete_workshop_post(post_id: int) -> bool:
    """Удалить пост "из цеха" """
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM workshop_posts WHERE id = ?", (post_id,))
        await db.commit()
        return True
