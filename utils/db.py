import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()  # 從 .env 檔案加載環境變數

def create_connection():
    """建立與 MySQL 數據庫的連接"""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DB')
        )
        print("成功連接到數據庫")
    except Error as e:
        print(f"數據庫連接錯誤: {e}")
    return connection

def close_connection(connection):
    """關閉與 MySQL 數據庫的連接"""
    if connection.is_connected():
        connection.close()
        print("數據庫連接已關閉")

def execute_query(query, params=None):
    """執行查詢語句"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
            return cursor.lastrowid  # 返回最後插入的 ID
        except Error as e:
            print(f"執行查詢錯誤: {e}")
        finally:
            cursor.close()
            close_connection(connection)

def fetch_all(query, params=None):
    """獲取所有結果"""
    connection = create_connection()
    results = []
    if connection:
        cursor = connection.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()  # 獲取所有行
        except Error as e:
            print(f"獲取數據錯誤: {e}")
        finally:
            cursor.close()
            close_connection(connection)
    return results
