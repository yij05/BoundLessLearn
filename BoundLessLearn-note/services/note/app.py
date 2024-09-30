from flask import request, render_template
from flask import Blueprint
import os
import uuid
import datetime

from utils import db, common

# 產生筆記服務藍圖
note_bp = Blueprint('note_bp', __name__)

# --------------------------
# 在筆記服務藍圖加入路由
# --------------------------

# 筆記清單
@note_bp.route('/list')
def note_list():
    # 取得資料庫連線
    connection = db.get_connection()

    # 執行 SQL 命令
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM T03_note ORDER BY note_id')

    # 取出資料
    data = cursor.fetchall()
    print(data)

    # 關閉資料庫連線
    connection.close()

    # 渲染網頁
    return render_template('note_list.html', data=data)


# 筆記新增表單
@note_bp.route('/create/form')
def note_create_form():
    return render_template('note_create_form.html')


# 筆記新增
@note_bp.route('/create', methods=['POST'])
def note_create():
    try:
        # 取得上傳圖檔
        photo = request.files['photo']
        filename = None

        # 檢查是否有選擇圖片, 並且檔案類型允許
        if photo and common.allowed_file(photo.filename):
            # 產生唯一的檔名並儲存圖片
            filename = str(uuid.uuid4()) + '.' + photo.filename.rsplit('.', 1)[1].lower()
            photo.save(os.path.join('static/photos', filename))

        # 取得其他參數
        note_id = request.form.get('note_id')
        stuno = request.form.get('stuno')
        title = request.form.get('title')
        content = request.form.get('content')

        # 如果沒有提供 created_time，則自動生成
        created_time = request.form.get('created_time') or datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(note_id, stuno, title, content, created_time, filename)

        # 取得資料庫連線
        conn = db.get_connection()

        # 將資料加入 T03_note 表
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO T03_note (cnote_id, stuno, title, content, created_time, photo)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (note_id, stuno, title, content, created_time, filename)
        )
        conn.commit()
        conn.close()

        # 渲染成功畫面
        return render_template('create_success.html')
    except Exception as e:
        # 印出錯誤原因
        print('-' * 30)
        print(e)
        print('-' * 30)

        # 渲染失敗畫面
        return render_template('create_fail.html')
