import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='140.131.114.242',
        user='adminBL',
        password='Vm,6j653rup4',
        database='113-BoundlessLearnDB'
    )
