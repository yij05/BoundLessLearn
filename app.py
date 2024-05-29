#-----------------------
# 匯入模組
#-----------------------
from flask import Flask, render_template 

#-----------------------
# 匯入各個服務藍圖
#-----------------------
# from services.employee.app import employee_bp

#-------------------------
# 產生主程式, 加入主畫面
#-------------------------
app = Flask(__name__)

#index
@app.route('/')
def index():
    return render_template('index.html') 

#note
@app.route('/note')
def note():
    return render_template('note.html') 

#-------------------------
# 在主程式註冊各個服務
#-------------------------
# app.register_blueprint(employee_bp, url_prefix='/employee')

#-------------------------
# 啟動主程式
#-------------------------
if __name__ == '__main__':
    app.run(debug=True)