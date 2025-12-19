"""Flask приложение для админ-панели"""
from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import json
from datetime import datetime
import sys
import os
import requests
import io
import base64
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_PATH, BOT_TOKEN

def create_admin_app():
    """Создать Flask приложение для админ-панели"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    def get_db_connection():
        """Получить соединение с БД"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    @app.route('/admin')
    def index():
        """Главная страница - список заявок"""
        conn = get_db_connection()
        
        # Параметры пагинации
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page
        
        # Получаем заявки
        leads = conn.execute("""
            SELECT * FROM leads 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (per_page, offset)).fetchall()
        
        # Общее количество
        total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        total_pages = (total + per_page - 1) // per_page
        
        # Статистика по типам мебели
        stats = conn.execute("""
            SELECT item_type, COUNT(*) as count 
            FROM leads 
            GROUP BY item_type
        """).fetchall()
        
        conn.close()
        
        return render_template('leads.html', 
                             leads=leads,
                             page=page,
                             total_pages=total_pages,
                             stats=stats,
                             total=total)
    
    @app.route('/admin/lead/<int:lead_id>')
    def lead_detail(lead_id):
        """Детальная страница заявки"""
        conn = get_db_connection()
        lead = conn.execute("""
            SELECT * FROM leads WHERE id = ?
        """, (lead_id,)).fetchone()
        conn.close()
        
        if not lead:
            return "Заявка не найдена", 404
        
        # Парсим JSON с фото
        photos = json.loads(lead['photos']) if lead['photos'] else []
        
        return render_template('lead_detail.html', 
                             lead=lead,
                             photos=photos)
    
    @app.route('/admin/api/photo')
    def get_photo():
        """Получить фото по file_id через Telegram Bot API"""
        file_id = request.args.get('id')
        if not file_id:
            return "Не указан file_id", 400
        
        try:
            # Декодируем base64 если нужно
            try:
                file_id = base64.b64decode(file_id).decode('utf-8')
            except:
                pass  # Если не base64, используем как есть
            
            # Получаем информацию о файле
            file_info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile"
            file_info_response = requests.get(file_info_url, params={'file_id': file_id}, timeout=5)
            file_info = file_info_response.json()
            
            if not file_info.get('ok'):
                return "Файл не найден", 404
            
            file_path = file_info['result']['file_path']
            
            # Скачиваем файл
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            file_response = requests.get(file_url, timeout=10)
            
            if file_response.status_code != 200:
                return "Ошибка загрузки файла", 500
            
            # Определяем MIME тип
            mime_type = 'image/jpeg'
            if file_path.endswith('.png'):
                mime_type = 'image/png'
            elif file_path.endswith('.gif'):
                mime_type = 'image/gif'
            elif file_path.endswith('.webp'):
                mime_type = 'image/webp'
            
            # Возвращаем изображение
            return send_file(
                io.BytesIO(file_response.content),
                mimetype=mime_type,
                as_attachment=False
            )
        except Exception as e:
            return f"Ошибка: {str(e)}", 500
    
    @app.route('/admin/api/stats')
    def api_stats():
        """API для получения статистики"""
        conn = get_db_connection()
        
        # Общее количество заявок
        total = conn.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        
        # По типам мебели
        by_type = conn.execute("""
            SELECT item_type, COUNT(*) as count 
            FROM leads 
            GROUP BY item_type
        """).fetchall()
        
        # По дням (последние 7 дней)
        by_date = conn.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM leads
            WHERE created_at >= datetime('now', '-7 days')
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        """).fetchall()
        
        conn.close()
        
        return jsonify({
            'total': total,
            'by_type': {row[0]: row[1] for row in by_type},
            'by_date': [{'date': row[0], 'count': row[1]} for row in by_date]
        })
    
    return app

