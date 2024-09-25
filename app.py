from flask import Flask, redirect, url_for, render_template, session
from services.student.app import student_bp  # 導入 student 藍圖
from services.student.room import room_bp  # 導入 room 藍圖

app = Flask(__name__)
app.config['SECRET_KEY'] = 'itismysecretkey'

# 根路由，將 "/" 重定向到 "/student/"
@app.route('/')
def index():
    return redirect(url_for('student.student_index'))

# 註冊藍圖
app.register_blueprint(student_bp, url_prefix='/student')
app.register_blueprint(room_bp, url_prefix='/student/room')  # 註冊 room 藍圖

if __name__ == "__main__":
    app.run(debug=True)
