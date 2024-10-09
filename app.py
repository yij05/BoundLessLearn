from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error
from datetime import datetime

app = Flask(__name__, template_folder='services/student/templates')

# 連接到 MySQL 資料庫
def get_db_connection():
    return mysql.connector.connect(
        host='140.131.114.242',
        user='adminBL',
        password='Vm,6j653rup4',
        database='113-BoundlessLearnDB'
    )

@app.route('/')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    rooms = []
    
    try:
        cursor.execute('SELECT room_id, room_name, people FROM T07_rooms')
        all_rooms = cursor.fetchall()
        rooms = [room for room in all_rooms if room[2] is not None and room[2] > 0]
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        cursor.close()
        conn.close()

    message = "目前尚無討論室可以加入！趕快創建討論室和大家一起討論吧！" if not rooms else ""
    return render_template('discuss.html', rooms=rooms, message=message)

@app.route('/add', methods=['GET', 'POST'])
def add_room():
    if request.method == 'POST':
        room_name = request.form['account']
        created_by = 1  # 假設固定用戶 ID 為 1
        created_time = datetime.now()

        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT COALESCE(MAX(room_id), 0) FROM T07_rooms')
            max_room_id = cursor.fetchone()[0]
            new_room_id = max_room_id + 1
            
            cursor.execute(
                'INSERT INTO T07_rooms (room_id, room_name, created_by, created_time, people) VALUES (%s, %s, %s, %s, 0)',
                (new_room_id, room_name, created_by, created_time)
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error inserting new room: {e}")
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('discussion', room_id=new_room_id))

    return render_template('add.html')

@app.route('/discussion/<int:room_id>')
def discussion(room_id):
    stuno = 1  # 假設固定用戶 ID 為 1
    join_time = datetime.now()

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT room_name FROM T07_rooms WHERE room_id = %s', (room_id,))
        room_name = cursor.fetchone()[0]

        cursor.execute(
            'INSERT INTO T08_room_members (stuno, room_id, join_time, created_time) VALUES (%s, %s, %s, %s)',
            (stuno, room_id, join_time, join_time)
        )
        
        cursor.execute('UPDATE T07_rooms SET people = people + 1 WHERE room_id = %s', (room_id,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error during joining discussion: {err}")
    finally:
        cursor.close()
        conn.close()

    return render_template('discussion.html', room_id=room_id, room_name=room_name)

@app.route('/delete_room/<int:room_id>', methods=['POST'])
def delete_room(room_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('DELETE FROM T07_rooms WHERE room_id = %s', (room_id,))
        cursor.execute('DELETE FROM T10_timers WHERE room_id = %s', (room_id,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        print(f"Error during deleting room: {err}")
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('home'))  # 返回主頁

if __name__ == '__main__':
    app.run(debug=True)
