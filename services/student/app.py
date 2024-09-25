from flask import Blueprint, render_template, session, redirect, url_for
from services.student.room import room_bp  # 引入討論室藍圖

student_bp = Blueprint('student', __name__, template_folder='templates')

@student_bp.route('/')
def student_index():
    session['username'] = '123'  # 假設用戶
    return render_template('index.html', name=session['username'])

@student_bp.route('/logout')
def logout():
    session.pop('username', None)  # 清除 session
    return redirect(url_for('student.student_index'))  # 重定向到學生首頁

# 註冊討論室的藍圖
student_bp.register_blueprint(room_bp, url_prefix='/room')  # 註冊討論室藍圖
