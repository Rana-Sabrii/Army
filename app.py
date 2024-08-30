from flask import Flask, render_template, redirect, request, jsonify, url_for, session, flash, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
import os
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField, StringField
from wtforms.validators import InputRequired, DataRequired
from urllib.parse import quote_plus, unquote_plus
import uuid
import re
from flask_login import current_user
from functools import wraps
from flask_wtf.csrf import CSRFProtect
# import pythoncom

# --- Initialize Flask App ---
app = Flask(__name__, template_folder='templates', static_url_path='/static')
app.secret_key = 'your_secret_key'
DATABASE = 'test40.db'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DELETION_PASSWORD'] = generate_password_hash('102030')  # Set the deletion password
from datetime import timedelta

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)


# --- Data Structure for Records ---
records = {
    'recordone': {
        'title': 'إشارات الإنذار والتعاون والسيطرة',
        
    },
    'recordtwo': {
        'title': 'الأوامر المستديمة لمراكز القيادة و السيطرة',
        
    },
    'record3': {
        'title':  'البلاغات الدورية',
        
    },
    'record4': {
        'title':'أوامر القتال - صادر',
       
    },
    'record5': {
        'title':  'أوامر القتال -وارد', 
        
    },
    'record6': {
        'title': 'بلاغات القتال صادر ',
        
    },
    'record7': {
        'title': 'بلاغات القتال وارد',
        
    },
    'record8': {
        'title':'تعليمات إبتدائية',
        
    },
    'record9': {
        'title': 'تعليمات التعاون',
        
    },
    'record10': {
        'title': 'تعليمات التعزيز',
        
    },
    'record11': {
        'title':'تعليمات الغيار - إعادة التجميع',
        
    },
    'record12': {
        'title': 'تعليمات القتال صادر',
        
    },
    'record13': {
        'title': 'تعليمات القتال وارد',
        
    },
    'record14': {
        'title': 'تعليمات الكود والرمز  ',
        
    },
    'record15': {
        'title': 'تعليمات المطاردة',
        
    },
    'record16': {
        'title': 'تعليمات تامين القتال',
        
    },
    'record17': {
        'title': 'تعليمات تحرك',
        
    },
    'record18': {
        'title': 'تعليمات سطع',
        
    },
    'record19': {
        'title': 'تقارير نتائج أعمال قتال الوحدات الوحدات الفرعية',
        
    },
    'record20': {
        'title': 'تقارير وبلاغات سطع',
       
    },
    'record21': {
        'title': 'تقرير ملخص أعمال القتال اليومية',
        
    },
    'record22': {
        'title': 'توجيهات السيد رئيس أركان حرب القوات المسلحة',
        
    },
    'record23': {
        'title': 'خبرة قتال',
        
    },
    'record24': {
        'title': 'سجل إشارات الإتذار والتعاون السيطرة',
       
    },
    'record25': {
        'title': 'سجل الإختراقات الجوية',
        
    },
    'record26': {
        'title': 'سجل الإشارات - صادر',
       
    },
    'record27': {
        'title':'سجل الإشارات - وارد',
        
    },
    'record28': {
        'title': 'سجل الكلمات الرمزية لحالات الاستعداد القتالي',
        
    },
    'record29': {
        'title': 'كود الوظائف',
        
    },
    'record30': {
        'title': 'سجل المحادثات التلفونية',
        
    },
    'record31': {
        'title': 'تقرير الغارة الجوية',
       
    },
    'record32': {
        'title': ' سجل نتائج ضرب المدفعية',
       
    }
    
    
}

# --- Create the uploads folder if it doesn't exist ---
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Database Functions ---
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.set_trace_callback(print)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA encoding = 'UTF-8'")  # Set UTF-8 encoding here
    return conn

# --- Helper Functions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def get_folders(folder_path):
    folders = []
    if os.path.exists(folder_path):  # Check if the folder exists first
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            if os.path.isdir(item_path):
                folders.append(item)
    return folders

def generate_unique_filename(filename):
    """Generates a unique filename to avoid overwriting existing files."""
    name, extension = os.path.splitext(filename)
    if re.search(r'[^\x00-\x7F]', name):
        unique_filename = f"{name}_{uuid.uuid4().hex}{extension}"
    else:
        unique_filename = secure_filename(f"{name}_{uuid.uuid4().hex}{extension}")
    return unique_filename

# --- Forms ---
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    desired_filename = StringField("Desired Filename", validators=[DataRequired()])
    submit = SubmitField("Upload File")

class DeleteFileForm(FlaskForm):
    password = StringField("Enter Deletion Password", validators=[InputRequired()])
    submit = SubmitField("Delete File")

# --- Routes ---

# Login
@app.route('/', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['login-email']
        password = request.form['login-pass']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'
        else:
            session['user_id'] = user['id']
            session['role'] = user['role']
            flash('You were successfully logged in', 'success')
            if session['role'] == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif session['role'] == 'Tester':
                return redirect(url_for('tester_dashboard'))
    return render_template('index.html', error=error), 200, {'Content-Type': 'text/html; charset=utf-8'}



# Admin Dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' in session and session['role'] == 'Admin':
        folder_counts = {}
        for record_key, record in records.items():
            record_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], record_key)
            if os.path.exists(record_folder_path):
                folder_counts[record_key] = len(os.listdir(record_folder_path))
            else:
                folder_counts[record_key] = 0

        return render_template('starter-template.html', folder_counts=folder_counts)
    else:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))


# Tester Dashboard
@app.route('/tester_dashboard')
def tester_dashboard():
    if 'user_id' in session and session['role'] == 'Tester':
        folder_counts = {}
        record_keys = []  # List to store the record keys

        for record_key, record in records.items():
            record_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], record_key)
            if os.path.exists(record_folder_path):
                folder_counts[record_key] = len(os.listdir(record_folder_path))
            else:
                folder_counts[record_key] = 0

            record_keys.append(record_key)  # Append each record_key to the list

        return render_template('Tester starter-template.html', folder_counts=folder_counts, record_keys=record_keys)
    else:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('login'))


# Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('You were logged out', 'success')
    return redirect(url_for('login'))

# Protect Routes with Decorators
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or session.get('role') != role:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/record/<record_key>')
def record_page(record_key):
    # Ensure the record_key exists in the records dictionary
    if record_key not in records:
        flash('Record not found', 'danger')
        return redirect(url_for('admin_dashboard'))

    # Get the record details from the records dictionary
    record = records[record_key]
    
    # Render the appropriate template with the record details
    return render_template(record['records_template'], title=record['title'])



#--- Run the app ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

