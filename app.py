
from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'cloud_storage'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Files that require passwords
protected_files = {
    "secret.pdf": "12345",
    "grades.xlsx": "letmein"
}

# Template remains unchanged
HTML_TEMPLATE = """<full HTML here>"""  # This part is omitted for brevity in the file

@app.route('/')
def index():
    files_data = []
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath) / 1024  # KB
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M')
            files_data.append((filename, f"{size:.1f}", mtime))
    files_data.sort()
    return render_template_string(HTML_TEMPLATE, files=files_data, message=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    message = f"✅ تم رفع الملف '{file.filename}' بنجاح!"
    files_data = []
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath) / 1024  # KB
            mtime = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime('%Y-%m-%d %H:%M')
            files_data.append((filename, f"{size:.1f}", mtime))
    files_data.sort()
    return render_template_string(HTML_TEMPLATE, files=files_data, message=message)

@app.route('/files/<filename>', methods=['GET', 'POST'])
def get_file(filename):
    if filename in protected_files:
        if request.method == 'POST':
            password = request.form.get('password')
            if password == protected_files[filename]:
                return send_from_directory(UPLOAD_FOLDER, filename)
            else:
                return render_template_string('<h3>❌ كلمة المرور خاطئة!</h3><a href="/">رجوع</a>')
        return '''
            <h3>🔒 هذا الملف محمي بكلمة مرور</h3>
            <form method="POST">
                <input type="password" name="password" placeholder="أدخل كلمة المرور" required>
                <input type="submit" value="تنزيل">
            </form>
        '''
    else:
        return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    os.remove(os.path.join(UPLOAD_FOLDER, filename))
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
