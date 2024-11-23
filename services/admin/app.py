from flask import request, render_template, redirect, url_for, flash, Blueprint, session
import hashlib
from utils import db
from utils.common import save_photo

# 創建管理者藍圖
admin_bp = Blueprint('admin_bp', __name__, template_folder='templates')


# 管理者登入
@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()

        try:
            connection = db.get_connection()
            cursor = connection.cursor()

            # 查詢 T01_student 表中的資料 (stuno=1 代表管理者)
            cursor.execute("SELECT stuno, stuname FROM T01_student WHERE user=%s AND password=%s AND stuno=1", (username, password))
            user = cursor.fetchone()
            cursor.close()

            if user:
                session['admin'] = user[1]  # 儲存管理者名稱
                session['stuno'] = user[0]    # 儲存管理者 stuno
                return redirect(url_for('admin_bp.dashboard'))  # 登入成功，導向管理者儀表板
            else:
                flash('帳號或密碼錯誤，或此帳號不是管理者！', 'error')  # 提示錯誤
        except Exception as e:
            flash(f'發生錯誤: {str(e)}', 'error')  # 捕獲並顯示異常錯誤

    return render_template('admin_login.html')  # 顯示登入頁面

# 管理者主頁
@admin_bp.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        flash('請先登入管理者帳號！', 'error')
        return redirect(url_for('admin_bp.admin_dashboard.html'))

    return render_template('admin_dashboard.html', admin_name=session.get('username'))


# 上傳題目
@admin_bp.route('/upload_questions', methods=['GET', 'POST'])
def upload_questions():
    if 'admin' not in session:
        return redirect(url_for('admin_bp.admin_login'))

    if request.method == 'POST':
        question = request.form.get('question')
        correct = request.form.get('correct')
        subject = request.form.get('subject')
        session_name = request.form.get('session')
        options = {
            'A': request.form.get('option_a'),
            'B': request.form.get('option_b'),
            'C': request.form.get('option_c'),
            'D': request.form.get('option_d')
        }

        # 驗證輸入
        valid_subjects = {'國文', '英文', '數學'}
        valid_sessions = {'113', '114'}

        if not question or not correct or correct not in options:
            flash('請完整填寫題目資料，並確認正確答案在選項中！', 'error')
            return render_template('upload_questions.html', question=question, correct=correct, options=options, subject=subject, session_name=session_name)

        if subject not in valid_subjects or session_name not in valid_sessions:
            flash('科目或學年選擇錯誤！', 'error')
            return render_template('upload_questions.html', question=question, correct=correct, options=options, subject=subject, session_name=session_name)

        try:
            # 處理圖片
            photo1, photo2 = None, None
            try:
                photo1 = save_photo(request.files.get('photo1')) if 'photo1' in request.files and request.files.get('photo1').filename else None
                photo2 = save_photo(request.files.get('photo2')) if 'photo2' in request.files and request.files.get('photo2').filename else None
            except Exception as e:
                flash(f"圖片處理失敗：{str(e)}", 'error')
                return render_template('upload_questions.html', question=question, correct=correct, options=options, subject=subject, session_name=session_name)

            # 新增題目到資料庫
            with db.get_connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO T11_exam_questions 
                        (question, correct, option_a, option_b, option_c, option_d, subject, session, photo1, photo2) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (question, correct, options['A'], options['B'], options['C'], options['D'], subject, session_name, photo1, photo2)
                    )
                    connection.commit()
                    flash('題目已成功新增！', 'success')
            return redirect(url_for('admin_bp.upload_questions'))  # 重定向，清空表單
        except Exception as e:
            flash(f'上傳題目時發生錯誤：{str(e)}', 'error')

    # GET 或提交失敗時返回表單
    return render_template('upload_questions.html')



# 管理者登出
@admin_bp.route('/logout')
def admin_logout():
    session.pop('admin', None)
    session.pop('username', None)  # 清除使用者名稱
    flash('管理者已成功登出！')
    return redirect(url_for('admin_bp.admin_login'))
