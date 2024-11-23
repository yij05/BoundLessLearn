from flask import Flask, request, render_template, session, redirect, url_for, Blueprint
import datetime
from utils import db  # 假設你有一個 db 模組來管理連線

# 產生測驗服務藍圖
exam_bp = Blueprint('exam_bp', __name__)

# 測驗首頁
@exam_bp.route('/')
def exam():
    return render_template('exam.html')

# 測驗清單
@exam_bp.route('/list')
def exam_list():
    return render_template('exam_list.html')

# 獲取隨機的測驗問題及正確答案
def get_questions_with_answers(subject, session_year):
    connection = db.get_connection()
    try:
        cursor = connection.cursor()
        # 使用 ORDER BY RAND() 隨機選擇 5 題
        cursor.execute('SELECT que_id, question, photo1, photo2, option_a, option_b, option_c, option_d, correct FROM T11_exam_questions WHERE subject = %s AND session = %s ORDER BY RAND() LIMIT 5', (subject, session_year))
        
        data = cursor.fetchall()
        questions = []
        correct_answers = {}

        for row in data:
            question = {
                'que_id': row[0],
                'question': row[1],
                'photo1': url_for('static', filename='imgs/' + row[2]) if row[2] else None,
                'photo2': url_for('static', filename='imgs/' + row[3]) if row[3] else None,
                'options': {
                    'A': row[4],
                    'B': row[5],
                    'C': row[6],
                    'D': row[7]
                },
                #'correct': row[8]  # 正確答案
            }
            questions.append(question)
            correct_answers[str(row[0])] = row[8]  # 儲存正確答案

        return questions, correct_answers
    except Exception as e:
        print("資料庫查詢錯誤:", e)
        return [], {}
    finally:
        connection.close()

# 測驗頁面
@exam_bp.route('/quiz')
def quiz():
    subject = request.args.get('subject')
    session_year = request.args.get('session')

    # 獲取問題與正確答案
    questions, correct_answers = get_questions_with_answers(subject, session_year)

    # 儲存正確答案到 session
    session['correct_answers'] = correct_answers
    session['questions'] = questions

    return render_template('quiz.html', subject=subject, session=session_year, questions=questions)

# 儲存分數到資料庫
def save_results_to_db(student_answers, score, stuno, subject):
    connection = db.get_connection()
    try:
        cursor = connection.cursor()
        date = datetime.datetime.now().strftime('%Y-%m-%d')

        # 插入到 T02_score 表
        score_query = 'INSERT INTO T02_score (stuno, subject, score, date) VALUES (%s, %s, %s, %s)'
        cursor.execute(score_query, (stuno, subject, score, date))
        scno = cursor.lastrowid  # 獲取剛剛插入的 scno

        # 儲存每個題目的答案到 T12_answers 表
        for answer in student_answers:
            selected_option = answer['student_answer']  # 獲取學生答案
            is_correct = "yes" if answer['is_correct'] else "no"  # 判斷答案是否正確，填入 "yes" 或 "no"
            que_id = answer['question_id']  # 從結果中獲取問題 ID
            answer_query = 'INSERT INTO T12_answers (scno, que_id, selected_option, is_correct, created_at) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(answer_query, (scno, que_id, selected_option, is_correct, date))

        connection.commit()
    except Exception as e:
        print("資料庫儲存錯誤:", e)
        connection.rollback()
    finally:
        connection.close()

# 提交答案並計算分數
@exam_bp.route('/submit_answers', methods=['POST'])
def submit_answers():
    try:
        # 獲取請求參數和學生提交的答案
        student_answers = request.get_json()
        correct_answers = session.get('correct_answers', {})
        stuno = session.get('stuno')  # 假設 session 已存放學號
        subject = request.args.get('subject')
        session_year = request.args.get('session')

        # 確保必要參數存在
        if not student_answers or not correct_answers or not stuno:
            return {"error": "無法處理提交的答案或用戶資料"}, 400
        
        score = 0
        results = []
        incorrect_questions = []

        for question_id, student_answer in student_answers.items():
            correct_answer = correct_answers.get(question_id)
            is_correct = student_answer == correct_answer

            # 獲取詳細的題目資訊
            question_data = next(
                (q for q in session.get('questions', []) if str(q['que_id']) == question_id),
                None
            )
            
            # 收集結果
            result = {
                'question_id': question_id,
                'student_answer': student_answer,
                'correct_answer': correct_answer,
                'is_correct': is_correct,
            }

            # 添加詳細資訊
            if question_data:
                result.update({
                    'question_text': question_data.get('question'),
                    'photo1': question_data.get('photo1'),
                    'photo2': question_data.get('photo2'),
                    'options': question_data.get('options'),
                })

            results.append(result)

            if is_correct:
                score += 1
            else:
                incorrect_questions.append(result)

        save_results_to_db(results, score, stuno, subject)

        # 儲存分數和錯誤題目到 session
        session['score'] = score
        session['total_questions'] = len(correct_answers)
        session['incorrect_questions'] = incorrect_questions

        return {"message": "提交成功", "score": score}, 200
    except Exception as e:
        print("提交答案錯誤:", e)
        return {"error": "伺服器錯誤"}, 500

# 顯示結果頁面
@exam_bp.route('/result')
def quiz_result():
    score = session.get('score', 0)
    total_questions = session.get('total_questions', 0)
    incorrect_questions = session.get('incorrect_questions', [])

    return render_template('result.html', score=score, total_questions=total_questions, incorrect_questions=incorrect_questions)

# 國文排行榜
@exam_bp.route('/chinese/score')
def chinese_score():
    connection = db.get_connection()
    try:
        cursor = connection.cursor()
        # 查詢學生在國文科目所有測驗的總得分
        cursor.execute('''SELECT s.stuname, SUM(sc.score) AS total_score
                          FROM T02_score AS sc
                          JOIN T01_student AS s ON sc.stuno = s.stuno
                          WHERE sc.subject = %s
                          GROUP BY s.stuno, s.stuname
                          ORDER BY total_score DESC''', ('國文',))
        scores = cursor.fetchall()

        # 將查詢結果轉換為字典列表
        score_list = [{'stuname': row[0], 'total_score': row[1]} for row in scores]
        return render_template('exam_chinese_score.html', scores=score_list)
    
    except Exception as e:
        print("查詢國文成績錯誤:", e)
        return render_template('exam_chinese_score.html', scores=[])
    finally:
        connection.close()

# 英文排行榜
@exam_bp.route('/english/score')
def english_score():
    connection = db.get_connection()
    try:
        cursor = connection.cursor()
        # 查詢學生在英文科目所有測驗的總得分
        cursor.execute('''SELECT s.stuname, SUM(sc.score) AS total_score
                          FROM T02_score AS sc
                          JOIN T01_student AS s ON sc.stuno = s.stuno
                          WHERE sc.subject = %s
                          GROUP BY s.stuno, s.stuname
                          ORDER BY total_score DESC''', ('英文',))
        scores = cursor.fetchall()

        # 將查詢結果轉換為字典列表
        score_list = [{'stuname': row[0], 'total_score': row[1]} for row in scores]
        return render_template('exam_english_score.html', scores=score_list)
    
    except Exception as e:
        print("查詢英文成績錯誤:", e)
        return render_template('exam_english_score.html', scores=[])
    finally:
        connection.close()

# 數學排行榜
@exam_bp.route('/math/score')
def math_score():
    connection = db.get_connection()
    try:
        cursor = connection.cursor()
        # 查詢學生在數學科目所有測驗的總得分
        cursor.execute('''SELECT s.stuname, SUM(sc.score) AS total_score
                          FROM T02_score AS sc
                          JOIN T01_student AS s ON sc.stuno = s.stuno
                          WHERE sc.subject = %s
                          GROUP BY s.stuno, s.stuname
                          ORDER BY total_score DESC''', ('數學',))
        scores = cursor.fetchall()

        # 將查詢結果轉換為字典列表
        score_list = [{'stuname': row[0], 'total_score': row[1]} for row in scores]
        return render_template('exam_math_score.html', scores=score_list)
    
    except Exception as e:
        print("查詢數學成績錯誤:", e)
        return render_template('exam_math_score.html', scores=[])
    finally:
        connection.close()

