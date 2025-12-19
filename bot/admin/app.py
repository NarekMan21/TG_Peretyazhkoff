"""Flask приложение для админ-панели"""
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
import sqlite3
import json
from datetime import datetime
import sys
import os
import requests
import io
import base64
import asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import DB_PATH, BOT_TOKEN
from content_publisher import publish_case_to_channel, publish_workshop_post_to_channel

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
    
    @app.route('/')
    def root():
        """Редирект с корня на админ-панель"""
        from flask import redirect
        return redirect('/admin')
    
    @app.route('/favicon.ico')
    def favicon():
        """Возвращает favicon"""
        # Простой SVG favicon с эмодзи дивана
        from flask import Response
        svg_icon = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
            <text y="0.9em" font-size="90">🛋️</text>
        </svg>'''
        return Response(svg_icon, mimetype='image/svg+xml')
    
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
        
        # Проверяем, что это не тестовый file_id
        if file_id.startswith('file_id') and file_id[7:].isdigit():
            # Это тестовый file_id типа "file_id1", "file_id2" и т.д.
            # Возвращаем placeholder изображение
            from flask import Response
            placeholder_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
                <rect width="400" height="300" fill="#f0f0f0"/>
                <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" font-family="Arial" font-size="16" fill="#999">
                    Фото недоступно (тестовый file_id)
                </text>
            </svg>'''
            return Response(placeholder_svg, mimetype='image/svg+xml')
        
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
                error_description = file_info.get('description', 'Неизвестная ошибка')
                # Возвращаем placeholder при ошибке
                from flask import Response
                placeholder_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
                    <rect width="400" height="300" fill="#f0f0f0"/>
                    <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" font-family="Arial" font-size="14" fill="#999">
                        Фото недоступно: {error_description}
                    </text>
                </svg>'''
                return Response(placeholder_svg, mimetype='image/svg+xml')
            
            file_path = file_info['result']['file_path']
            
            # Скачиваем файл
            file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
            file_response = requests.get(file_url, timeout=10)
            
            if file_response.status_code != 200:
                from flask import Response
                placeholder_svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
                    <rect width="400" height="300" fill="#f0f0f0"/>
                    <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" font-family="Arial" font-size="14" fill="#999">
                        Ошибка загрузки файла
                    </text>
                </svg>'''
                return Response(placeholder_svg, mimetype='image/svg+xml')
            
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
            # Возвращаем placeholder при любой ошибке
            from flask import Response
            placeholder_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="300" viewBox="0 0 400 300">
                <rect width="400" height="300" fill="#f0f0f0"/>
                <text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" font-family="Arial" font-size="12" fill="#999">
                    Ошибка: {str(e)[:50]}
                </text>
            </svg>'''
            return Response(placeholder_svg, mimetype='image/svg+xml')
    
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
    
    # ========== Роуты для работы с кейсами ==========
    
    @app.route('/admin/cases')
    def cases_list():
        """Список кейсов"""
        conn = get_db_connection()
        
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page
        
        cases = conn.execute("""
            SELECT * FROM cases 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (per_page, offset)).fetchall()
        
        total = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
        total_pages = (total + per_page - 1) // per_page
        
        conn.close()
        
        return render_template('cases.html',
                             cases=cases,
                             page=page,
                             total_pages=total_pages,
                             total=total)
    
    @app.route('/admin/cases/new', methods=['GET', 'POST'])
    def case_new():
        """Создать новый кейс"""
        if request.method == 'POST':
            conn = get_db_connection()
            
            # Обработка фото - разбиваем по строкам и фильтруем пустые
            photos_text = request.form.get('photos', '')
            photos_list = [p.strip() for p in photos_text.split('\n') if p.strip()]
            photos_json = json.dumps(photos_list)
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            conn.execute("""
                INSERT INTO cases (
                    title, description_before, description_after,
                    fabric_type, filler_type, price, client_review,
                    photos, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                request.form['title'],
                request.form.get('description_before', ''),
                request.form.get('description_after', ''),
                request.form.get('fabric_type', ''),
                request.form.get('filler_type', ''),
                float(request.form['price']) if request.form.get('price') else None,
                request.form.get('client_review', ''),
                photos_json,
                created_at
            ))
            
            conn.commit()
            conn.close()
            
            return redirect(url_for('cases_list'))
        
        return render_template('case_form.html')
    
    @app.route('/admin/cases/<int:case_id>')
    def case_detail(case_id):
        """Детальная страница кейса"""
        conn = get_db_connection()
        case = conn.execute("""
            SELECT * FROM cases WHERE id = ?
        """, (case_id,)).fetchone()
        conn.close()
        
        if not case:
            return "Кейс не найден", 404
        
        photos = json.loads(case['photos']) if case['photos'] else []
        
        return render_template('case_detail.html',
                             case=case,
                             photos=photos)
    
    @app.route('/admin/cases/<int:case_id>/publish', methods=['POST'])
    def case_publish(case_id):
        """Опубликовать кейс в канал"""
        try:
            # Проверяем, есть ли запущенный event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Если loop уже запущен, используем create_task
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, publish_case_to_channel(case_id))
                    message_id = future.result(timeout=30)
            else:
                # Если loop не запущен, используем run
                message_id = asyncio.run(publish_case_to_channel(case_id))
            
            if message_id:
                # Отмечаем как опубликованный в БД
                conn = get_db_connection()
                published_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute("""
                    UPDATE cases SET published = 1, published_at = ? WHERE id = ?
                """, (published_at, case_id))
                conn.commit()
                conn.close()
                
                return jsonify({'success': True, 'message_id': message_id})
            else:
                return jsonify({'success': False, 'error': 'Ошибка публикации. Проверьте логи и настройки канала.'}), 500
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return jsonify({'success': False, 'error': f'{str(e)}\n{error_trace}'}), 500
    
    @app.route('/admin/cases/<int:case_id>/delete', methods=['POST'])
    def case_delete(case_id):
        """Удалить кейс"""
        conn = get_db_connection()
        conn.execute("DELETE FROM cases WHERE id = ?", (case_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('cases_list'))
    
    # ========== Роуты для работы с постами "из цеха" ==========
    
    @app.route('/admin/workshop')
    def workshop_list():
        """Список постов из цеха"""
        conn = get_db_connection()
        
        page = request.args.get('page', 1, type=int)
        per_page = 20
        offset = (page - 1) * per_page
        
        posts = conn.execute("""
            SELECT * FROM workshop_posts 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (per_page, offset)).fetchall()
        
        total = conn.execute("SELECT COUNT(*) FROM workshop_posts").fetchone()[0]
        total_pages = (total + per_page - 1) // per_page
        
        conn.close()
        
        return render_template('workshop_posts.html',
                             posts=posts,
                             page=page,
                             total_pages=total_pages,
                             total=total)
    
    @app.route('/admin/workshop/new', methods=['GET', 'POST'])
    def workshop_new():
        """Создать новый пост из цеха"""
        if request.method == 'POST':
            conn = get_db_connection()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            conn.execute("""
                INSERT INTO workshop_posts (
                    title, description, media_type, media_file_id, created_at
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                request.form['title'],
                request.form.get('description', ''),
                request.form.get('media_type', 'photo'),
                request.form.get('media_file_id', ''),
                created_at
            ))
            
            conn.commit()
            conn.close()
            
            return redirect(url_for('workshop_list'))
        
        return render_template('workshop_form.html')
    
    @app.route('/admin/workshop/<int:post_id>')
    def workshop_detail(post_id):
        """Детальная страница поста из цеха"""
        conn = get_db_connection()
        post = conn.execute("""
            SELECT * FROM workshop_posts WHERE id = ?
        """, (post_id,)).fetchone()
        conn.close()
        
        if not post:
            return "Пост не найден", 404
        
        return render_template('workshop_detail.html', post=post)
    
    @app.route('/admin/workshop/<int:post_id>/publish', methods=['POST'])
    def workshop_publish(post_id):
        """Опубликовать пост "из цеха" в канал"""
        try:
            # Проверяем, есть ли запущенный event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Если loop уже запущен, используем create_task
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, publish_workshop_post_to_channel(post_id))
                    message_id = future.result(timeout=30)
            else:
                # Если loop не запущен, используем run
                message_id = asyncio.run(publish_workshop_post_to_channel(post_id))
            
            if message_id:
                # Отмечаем как опубликованный в БД
                conn = get_db_connection()
                published_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                conn.execute("""
                    UPDATE workshop_posts SET published = 1, published_at = ? WHERE id = ?
                """, (published_at, post_id))
                conn.commit()
                conn.close()
                
                return jsonify({'success': True, 'message_id': message_id})
            else:
                return jsonify({'success': False, 'error': 'Ошибка публикации. Проверьте логи и настройки канала.'}), 500
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            return jsonify({'success': False, 'error': f'{str(e)}\n{error_trace}'}), 500
    
    @app.route('/admin/workshop/<int:post_id>/delete', methods=['POST'])
    def workshop_delete(post_id):
        """Удалить пост из цеха"""
        conn = get_db_connection()
        conn.execute("DELETE FROM workshop_posts WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('workshop_list'))
    
    return app

