from flask import Flask, request, send_from_directory, render_template_string, redirect, url_for
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'cloud_storage'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

protected_files = {}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="ar">
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
        input[type="file"], input[type="password"] {
            padding: 10px;
            border-radius: 6px;
            border: none;
            margin-bottom: 15px;
            background-color: #2c2c2c;
            color: #80cbc4;
            width: 250px;
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
            width: 150px;
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
            word-break: break-all;
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
            <input type="password" name="password" placeholder="أدخل كلمة مرور للملف" required />
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
                    <a href="{{ url_for('delete_file', filename=file) }}">🗑️ حذف</a>
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
    password = request.form.get('password')
    filename = file.filename
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    protected_files[filename] = password
    message = f"✅ تم رفع الملف '{filename}' مع حماية بكلمة مرور!"
    files_data = []
    for filename in os.listdir(UPLOAD_FOLDER):
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath) / 1024
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
                return render_template_string('''
                    <!DOCTYPE html>
                    <html lang="ar">
                    <head>
                        <meta charset="UTF-8">
                        <title>كلمة المرور خاطئة</title>
                        <style>
                            body {
                                background-color: #121212;
                                color: #ff5252;
                                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                                margin: 0;
                            }
                            .container {
                                background: #1e1e1e;
                                padding: 25px 35px;
                                border-radius: 12px;
                                box-shadow: 0 0 15px rgba(255, 82, 82, 0.7);
                                text-align: center;
                            }
                            h3 {
                                margin-bottom: 20px;
                                font-size: 1.4rem;
                            }
                            a {
                                display: inline-block;
                                margin-top: 15px;
                                color: #26a69a;
                                text-decoration: none;
                                font-weight: bold;
                                border: 2px solid #26a69a;
                                padding: 8px 18px;
                                border-radius: 8px;
                                transition: background-color 0.3s ease, color 0.3s ease;
                            }
                            a:hover {
                                background-color: #26a69a;
                                color: #121212;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h3>❌ كلمة المرور خاطئة!</h3>
                            <a href="/">رجوع للصفحة الرئيسية</a>
                        </div>
                    </body>
                    </html>
                ''')
        return render_template_string('''
            <!DOCTYPE html>
            <html lang="ar">
            <head>
                <meta charset="UTF-8" />
                <title>التحقق من كلمة المرور</title>
                <style>
                    body {
                        background-color: #121212;
                        color: #80cbc4;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .container {
                        background: #1e1e1e;
                        padding: 30px 40px;
                        border-radius: 12px;
                        box-shadow: 0 0 30px rgba(128, 203, 196, 0.7);
                        text-align: center;
                        width: 320px;
                    }
                    h3 {
                        margin-bottom: 25px;
                        font-weight: 700;
                    }
                    input[type="password"] {
                        width: 100%;
                        padding: 12px;
                        border-radius: 8px;
                        border: none;
                        margin-bottom: 20px;
                        background-color: #2c2c2c;
                        color: #80cbc4;
                        font-size: 1rem;
                    }
                    input[type="submit"] {
                        background-color: #26a69a;
                        color: #121212;
                        border: none;
                        padding: 12px 0;
                        border-radius: 10px;
                        font-weight: bold;
                        cursor: pointer;
                        width: 100%;
                        transition: background-color 0.3s ease;
                    }
                    input[type="submit"]:hover {
                        background-color: #00796b;
                        color: #e0f2f1;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h3>🔒 هذا الملف محمي بكلمة مرور</h3>
                    <form method="POST">
                        <input type="password" name="password" placeholder="أدخل كلمة المرور" required />
                        <input type="submit" value="تنزيل" />
                    </form>
                </div>
            </body>
            </html>
        ''')
    else:
        return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/delete/<filename>', methods=['GET', 'POST'])
def delete_file(filename):
    if filename not in os.listdir(UPLOAD_FOLDER):
        return redirect(url_for('index'))
    if filename in protected_files:
        if request.method == 'POST':
            password = request.form.get('password')
            if password == protected_files[filename]:
                os.remove(os.path.join(UPLOAD_FOLDER, filename))
                del protected_files[filename]
                return redirect(url_for('index'))
            else:
                return render_template_string('''
                    <!DOCTYPE html>
                    <html lang="ar">
                    <head>
                        <meta charset="UTF-8">
                        <title>كلمة المرور خاطئة</title>
                        <style>
                            body {
                                background-color: #121212;
                                color: #ff5252;
                                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                                display: flex;
                                flex-direction: column;
                                justify-content: center;
                                align-items: center;
                                height: 100vh;
                                margin: 0;
                            }
                            .container {
                                background: #1e1e1e;
                                padding: 25px 35px;
                                border-radius: 12px;
                                box-shadow: 0 0 15px rgba(255, 82, 82, 0.7);
                                text-align: center;
                            }
                            h3 {
                                margin-bottom: 20px;
                                font-size: 1.4rem;
                            }
                            a {
                                display: inline-block;
                                margin-top: 15px;
                                color: #26a69a;
                                text-decoration: none;
                                font-weight: bold;
                                border: 2px solid #26a69a;
                                padding: 8px 18px;
                                border-radius: 8px;
                                transition: background-color 0.3s ease, color 0.3s ease;
                            }
                            a:hover {
                                background-color: #26a69a;
                                color: #121212;
                            }
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h3>❌ كلمة المرور خاطئة!</h3>
                            <a href="/">رجوع للصفحة الرئيسية</a>
                        </div>
                    </body>
                    </html>
                ''')
        return render_template_string('''
            <!DOCTYPE html>
            <html lang="ar">
            <head>
                <meta charset="UTF-8" />
                <title>تأكيد حذف الملف</title>
                <style>
                    body {
                        background-color: #121212;
                        color: #80cbc4;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .container {
                        background: #1e1e1e;
                        padding: 30px 40px;
                        border-radius: 12px;
                        box-shadow: 0 0 30px rgba(128, 203, 196, 0.7);
                        text-align: center;
                        width: 320px;
                    }
                    h3 {
                        margin-bottom: 25px;
                        font-weight: 700;
                    }
                    input[type="password"] {
                        width: 100%;
                        padding: 12px;
                        border-radius: 8px;
                        border: none;
                        margin-bottom: 20px;
                        background-color: #2c2c2c;
                        color: #80cbc4;
                        font-size: 1rem;
                    }
                    input[type="submit"] {
                        background-color: #26a69a;
                        color: #121212;
                        border: none;
                        padding: 12px 0;
                        border-radius: 10px;
                        font-weight: bold;
                        cursor: pointer;
                        width: 100%;
                        transition: background-color 0.3s ease;
                    }
                    input[type="submit"]:hover {
                        background-color: #00796b;
                        color: #e0f2f1;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h3>🔒 هذا الملف محمي بكلمة مرور. أدخل كلمة المرور للحذف.</h3>
                    <form method="POST">
                        <input type="password" name="password" placeholder="أدخل كلمة المرور" required />
                        <input type="submit" value="حذف الملف" />
                    </form>
                </div>
            </body>
            </html>
        ''')

    else:
        # حذف مباشر بدون باسورد لو الملف مش محمي
        os.remove(os.path.join(UPLOAD_FOLDER, filename))
        return redirect(url_for('index'))

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
