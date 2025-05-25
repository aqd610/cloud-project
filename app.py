from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'cloud_storage'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ملفات محمية بكلمات مرور
protected_files = {
    "secret.pdf": "12345",
    "grades.xlsx": "letmein"
}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Cloud Project (DR: Monther Tarawneh)</title>
    <style>
        body {
            background-color: #121212;
            color: #80cbc4;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 30px;
        }
        .container {
            max-width: 800px;
            margin: auto;
            background: #1e1e1e;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 0 30px rgba(128, 203, 196, 0.7);
        }
        h1 {
            text-align: center;
            margin-bottom: 25px;
            font-weight: 700;
            color: #26a69a;
        }
        form {
            text-align: center;
            margin-bottom: 40px;
        }
        input[type="file"] {
            padding: 10px;
            border-radius: 6px;
            border: none;
            margin-bottom: 15px;
            background-color: #2c2c2c;
            color: #80cbc4;
        }
        input[type="submit"] {
            background-color: #26a69a;
            border: none;
            color: #121212;
            font-weight: bold;
            padding: 12px 24px;
            border-radius: 10px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        input[type="submit"]:hover {
            background-color: #00796b;
            color: #e0f2f1;
        }
        ul {
            list-style: none;
            padding-left: 0;
        }
        li {
            background: #2c2c2c;
            margin: 10px 0;
            padding: 16px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: #b2dfdb;
            font-size: 16px;
            box-shadow: 0 0 8px rgba(38, 166, 154, 0.3);
        }
        .file-info {
            flex-grow: 1;
            margin-left: 15px;
        }
        a, button {
            color: #26a69a;
            text-decoration: none;
            margin-left: 15px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 17px;
        }
        button:hover, a:hover {
            color: #004d40;
        }
        #spinner {
            display: none;
            margin: 10px auto;
            border: 6px solid #26a69a;
            border-top: 6px solid #121212;
            border-radius: 50%;
            width: 44px;
            height: 44px;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% {transform: rotate(0deg);}
            100% {transform: rotate(360deg);}
        }
        #message {
            text-align: center;
            margin-bottom: 15px;
            font-weight: bold;
            color: #4db6ac;
        }
    </style>
    <script>
        function showSpinner() {
            document.getElementById('spinner').style.display = 'block';
        }
    </script>
</head>
<body>
    <div class="container">
        <h1>☁️ Cloud Project (DR: Monther Tarawneh)</h1>
        
        {% if message %}
            <div id="message">{{ message }} <a href="{{ url_for('index') }}">عودة</a></div>
        {% endif %}
        
        <form method="POST" enctype="multipart/form-data" action="/upload" onsubmit="showSpinner()">
            <input type="file" name="file" required />
            <br />
            <input type="submit" value="رفع الملف" />
        </form>

        <div id="spinner"></div>

        <h2>الملفات المرفوعة</h2>
        <ul>
            {% for file, size, mtime in files %}
            <li>
                <div class="file-info">
                    📄 {{ file }} &nbsp;&nbsp; | الحجم: {{ size }} كيلوبايت &nbsp;&nbsp; | آخر تعديل: {{ mtime }}
                </div>
                <div>
                    <a href="{{ url_for('get_file', filename=file) }}" target="_blank">⬇️ تحميل</a>
                    <form method="POST" action="{{ url_for('delete_file', filename=file) }}" style="display:inline;">
                        <button type="submit" title="حذف الملف">🗑️ حذف</button>
                    </form>
                </div>
            </li>
            {% else %}
            <li>لا يوجد ملفات مرفوعة حالياً.</li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
'''

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
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

