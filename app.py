from flask import Flask, redirect, url_for, session, render_template, request, flash
from utils.common import get_student
from services.student.room import room_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 設定 Flask 的 session 加密金鑰
app.register_blueprint(room_bp, url_prefix='/room')

# 登入頁面
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        stuno = request.form['stuno']
        password = request.form['password']
        student = get_student(stuno, password)
        
        if student:
            session['stuno'] = student['stuno']
            flash(f"歡迎, {student['stuname']}!")
            return redirect(url_for('room.list_rooms'))
        else:
            flash("無效的學號或密碼，請重試！")
    
    return render_template('login.html')

# 登出
@app.route('/logout')
def logout():
    session.clear()
    flash("您已成功登出")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
