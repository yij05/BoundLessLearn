from flask import request, render_template, redirect, url_for, session, flash
from flask import Blueprint
import os, uuid
import datetime
from utils import db
from werkzeug.utils import secure_filename

# 產生筆記服務藍圖
note_bp = Blueprint('note_bp', __name__)

# 獲取所有筆記
def get_all_notes():
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT n.*, p.url 
        FROM T03_note n 
        LEFT JOIN T04_photos p ON n.note_id = p.note_id 
        ORDER BY n.note_id
    ''')
    notes = cursor.fetchall()
    
    notes_with_comments_count = []
    for note in notes:
        comments_count = get_comments_count(note[0])  # 使用筆記ID
        notes_with_comments_count.append((note, comments_count))

    cursor.close()
    conn.close()
    
    return notes_with_comments_count


# 獲取特定筆記的評論數量
def get_comments_count(note_id):
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM T05_comments WHERE note_id = %s', (note_id,))
    comments_count = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    
    return comments_count

# 筆記清單
@note_bp.route('/list', methods=['GET'])
def note_list():
    notes = get_all_notes()
    return render_template('note_list.html', notes=notes, get_comments=get_comments)

# 筆記新增表單
@note_bp.route('/create/form', methods=['GET'])
def note_create_form():
    return render_template('note_create_form.html')

# 檢查檔案擴展名是否合法
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 儲存上傳的圖片，並生成隨機的檔案名稱
import uuid

# 儲存上傳的圖片，並生成符合 UUID 格式的檔案名稱
def save_photo(photo):
    if photo and allowed_file(photo.filename):
        # 生成隨機的 UUID 檔案名稱，並保留原始副檔名
        ext = photo.filename.rsplit('.', 1)[1].lower()  # 獲取原始檔案的副檔名
        filename = f"{uuid.uuid4()}.{ext}"  # 生成符合格式的檔案名稱
        
        upload_folder = 'static/photos'
        os.makedirs(upload_folder, exist_ok=True)
        photo_path = os.path.join(upload_folder, filename)
        
        # 儲存圖片
        photo.save(photo_path)
        return filename  # 返回生成的檔案名稱
    return None


@note_bp.route('/create', methods=['POST'])
def note_create():
    try:
        photo = request.files['photo']
        photo_filename = save_photo(photo) if photo else None

        user = session['user']  # 獲取用戶名
        conn = db.get_connection()
        cursor = conn.cursor()

        # 根據用戶名查找 stuno
        cursor.execute('SELECT stuno FROM T01_student WHERE user = %s', (user,))
        result = cursor.fetchone()

        if result is None:
            flash('找不到用戶的學號，新增筆記失敗！')
            return redirect(url_for('note_bp.note_create_form'))

        stuno = result[0]  # 獲取學號
        title = request.form['title']
        content = request.form['content']

        # 新增筆記
        cursor.execute(
            """
            INSERT INTO T03_note (stuno, title, content, created_time)
            VALUES (%s, %s, %s, %s)
            """,
            (stuno, title, content, datetime.datetime.now())
        )
        conn.commit()
        
        # 獲取新增筆記的 note_id
        note_id = cursor.lastrowid

        # 如果有上傳圖片，將其儲存到 T04_photos 資料表
        if photo_filename:
            cursor.execute(
                """
                INSERT INTO T04_photos (note_id, url)
                VALUES (%s, %s)
                """,
                (note_id, photo_filename)
            )
            conn.commit()

        cursor.close()
        conn.close()

        flash('筆記新增成功！')
        return redirect(url_for('note_bp.note_list'))  # 返回筆記清單
    except Exception as e:
        print('-' * 30)
        print(e)
        print('-' * 30)
        flash('新增筆記失敗！請重試。')
        return redirect(url_for('note_bp.note_create_form'))  # 返回新增表單



@note_bp.route('/comment/add/<int:note_id>', methods=['POST'])
def add_comment(note_id):
    try:
        user = session['user']
        
        conn = db.get_connection()
        cursor = conn.cursor()

        # 透過 user 查找 stuno
        cursor.execute('SELECT stuno FROM T01_student WHERE user = %s', (user,))
        result = cursor.fetchone()
        
        if result is None:
            flash('使用者不存在，無法新增評論！')
            return redirect(url_for('note_bp.note_list'))

        stuno = result[0]  # 獲取學生編號
        comment_content = request.form['comment_content']

        # 將評論新增至資料庫
        cursor.execute(
            """
            INSERT INTO T05_comments (note_id, stuno, content, created_time)
            VALUES (%s, %s, %s, %s)
            """,
            (note_id, stuno, comment_content, datetime.datetime.now())
        )
        conn.commit()

        cursor.close()
        conn.close()

        flash('評論新增成功！')
        return redirect(url_for('note_bp.note_list'))  # 返回筆記清單
    except Exception as e:
        print('-' * 30)
        print(f'Error: {e}')
        print('-' * 30)
        flash('新增評論失敗！請重試。')

    return redirect(url_for('note_bp.note_list'))  # 返回筆記清單

# 獲取特定筆記的所有留言，並獲取對應的用戶名稱
def get_comments(note_id):
    conn = db.get_connection()
    cursor = conn.cursor()

    # 獲取留言及對應的用戶名稱
    cursor.execute('''
        SELECT c.content, c.created_time, s.user 
        FROM T05_comments c
        JOIN T01_student s ON c.stuno = s.stuno
        WHERE c.note_id = %s
        ORDER BY c.created_time
    ''', (note_id,))
    comments = cursor.fetchall()

    cursor.close()
    conn.close()
    
    return comments

@note_bp.route('/note/<int:note_id>', methods=['GET'])
def view_note(note_id):
    conn = db.get_connection()
    cursor = conn.cursor()

    # 獲取筆記內容
    cursor.execute('SELECT * FROM T03_note WHERE note_id = %s', (note_id,))
    note = cursor.fetchone()

    # 獲取留言
    comments = get_comments(note_id)  # 使用更新後的 get_comments 函數

    cursor.close()
    conn.close()

    return render_template('view_note.html', note=note, comments=comments)


@note_bp.route('/my', methods=['GET'])
def my_notes():
    # 確認使用者是否已登入
    stuno = session.get('stuno')
    if not stuno:
        return redirect(url_for('user_bp.login'))  # 如果未登入，重定向到登入頁面

    # 查詢使用者的所有筆記
    conn = db.get_connection()
    cursor = conn.cursor()

    # 獲取筆記及其對應圖片
    cursor.execute('''
        SELECT n.note_id, n.stuno, n.title, n.content, n.created_time, n.update_time, p.url
        FROM T03_note n
        LEFT JOIN T04_photos p ON n.note_id = p.note_id
        WHERE n.stuno = %s
        ORDER BY n.created_time DESC
    ''', (stuno,))
    
    notes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('my_notes.html', notes=notes)  # 傳遞筆記到模板


