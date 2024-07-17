from flask import request, render_template
from flask import Blueprint

from utils import db

# 產生筆記服務藍圖
note_bp = Blueprint('note_bp', __name__)

#--------------------------
# 在筆記服務藍圖加入路由
#--------------------------
#筆記清單
@note_bp.route('/list')
def note_list(): 
    #取得資料庫連線 
    connection = db.get_connection() 
    
    #產生執行sql命令的物件, 再執行sql   
    cursor = connection.cursor()     
    cursor.execute('SELECT * FROM note order by nono')
    
    #取出資料
    data = cursor.fetchall()    
    print(data)
    #關閉資料庫連線    
    connection.close() 

    #渲染網頁
    return render_template('note_list.html', data=data)