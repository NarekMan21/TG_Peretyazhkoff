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
        # Таблица заявок
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_user_id INTEGER NOT NULL,
                username TEXT,
                item_type TEXT NOT NULL,
                district TEXT NOT NULL,
                phone TEXT NOT NULL,
                photos TEXT NOT NULL,
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
        
        await db.commit()


async def save_lead(
    telegram_user_id: int,
    username: Optional[str],
    item_type: str,
    district: str,
    phone: str,
    photos: List[str]
) -> int:
    """Сохранить заявку в базу данных
    
    Returns:
        int: ID сохраненной заявки
    """
    async with aiosqlite.connect(DB_PATH) as db:
        photos_json = json.dumps(photos)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = await db.execute("""
            INSERT INTO leads (
                telegram_user_id, username, item_type, district, 
                phone, photos, created_at, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            telegram_user_id, username, item_type, district,
            phone, photos_json, created_at, "TelegramBot_Peretiazhkoff"
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
                lead['photos'] = json.loads(lead['photos'])
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
                lead['photos'] = json.loads(lead['photos'])
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
            GROUP BY item_type
        """) as cursor:
            rows = await cursor.fetchall()
            return {row[0]: row[1] for row in rows}

