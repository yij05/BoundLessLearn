from flask import Blueprint, render_template, request, redirect, url_for, session
from utils.db import execute_query, fetch_all
from datetime import datetime

room_bp = Blueprint('room', __name__, template_folder='templates')

@room_bp.route('/create', methods=['GET', 'POST'])
def create_room():
    if request.method == 'POST':
        room_name = request.form['room_name']
        created_by = session.get('username')  # 使用 session 中的用戶名
        created_time = datetime.now()
        execute_query("""
            INSERT INTO T07_rooms (room_name, created_by, created_time) 
            VALUES (%s, %s, %s)""",
            (room_name, created_by, created_time))
        return redirect(url_for('student.student_index'))  # 創建成功後重定向
    return render_template('create_room.html')

@room_bp.route('/list')
def list_rooms():
    rooms = fetch_all("SELECT * FROM T07_rooms")
    return render_template('list_rooms.html', rooms=rooms)
