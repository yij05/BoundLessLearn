#檢查上傳檔案類型
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ('png', 'jpg', 'jpeg', 'gif')
