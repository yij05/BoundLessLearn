import os
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """
    檢查文件格式是否被允許。
    :param filename: 文件名
    :return: 是否允許上傳
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_photo(photo):
    """
    保存上傳的圖片，並返回圖片的相對路徑。
    :param photo: 從表單接收到的 FileStorage 對象。
    :return: 儲存後的相對路徑或 None。
    """
    if not photo or not allowed_file(photo.filename):
        raise ValueError("不支持的文件格式")  # 如果文件不符合條件，直接拋出異常
    
    # 確保檔名安全
    filename = secure_filename(photo.filename)
    
    # 確定保存路徑
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)  # 確保目錄存在
    
    # 儲存圖片
    filepath = os.path.join(upload_folder, filename)
    photo.save(filepath)
    
    # 返回相對路徑以便存入資料庫
    return os.path.join('static', 'uploads', filename)
