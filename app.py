import streamlit as st
import sqlite3
import hashlib
import random
import smtplib
from email.mime.text import MIMEText

# --- 1. إعدادات سيرفر الإرسال الخاصة بك ---
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "yaroubnassif71@gmail.com" 
SENDER_PASSWORD = "gqnk vttk kifk czbt" 

def send_email(receiver_email, subject, body):
    """دالة عامة لإرسال الإيميلات"""
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        return True
    except Exception as e:
        return False

# --- 2. إدارة قاعدة البيانات المستقلة تماماً (نظام الكلية الجديد) ---
def init_independent_db():
    """إنشاء قاعدة بيانات جديدة كلياً ومنفصلة لضمان عدم التداخل"""
    conn = sqlite3.connect('independent_college.db')
    cursor = conn.cursor()
    
    # جدول الطلاب المصرح لهم (سجلات الكلية الرسمية)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS official_students (
            uni_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            faculty TEXT NOT NULL,
            department TEXT NOT NULL
        )
    ''')
    
    # جدول الحسابات المسجلة بالموقع
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_web_accounts (
            email TEXT PRIMARY KEY,
            uni_id TEXT NOT NULL,
            password TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            FOREIGN KEY (uni_id) REFERENCES official_students(uni_id)
        )
    ''')
    
    # 📝 إدخال بياناتك المعتمدة مباشرة في النظام المستقل
    # الرجاء التأكد من كتابة اسمك ورقك الجامعي هنا تماماً كما ستكتبهما في واجهة التسجيل
    my_real_id = "123456"          # ضع رقمك الجامعي الحقيقي هنا
    my_real_name = "يعرب نصيف"     # ضع اسمك الكامل هنا بنفس الحروف والهمزات
    
    cursor.execute('''
        INSERT OR IGNORE INTO official_students (uni_id, full_name, faculty, department)
        VALUES (?, ?, 'كلية الهندسة المدنية', 'السنة الثالثة')
    ''', (my_real_id, my_real_name))
    
    conn.commit()
    conn.close()

def check_college_records(university_id, full_name):
    """التحقق من السجلات الرسمية"""
    conn = sqlite3.connect('independent_college.db')
    cursor = conn.cursor()
    cursor.execute('SELECT faculty, department FROM official_students WHERE uni_id = ? AND full_name = ?', (university_id, full_name))
    result = cursor.fetchone()
    conn.close()
    return result

def add_user_account(email, university_id, password):
    """إنشاء حساب مستخدم جديد بربطه برقمه الجامعي"""
    conn = sqlite3.connect('independent_college.db')
    cursor = conn.cursor()
    try:
        hashed_pass = hashlib.sha256(str.encode(password)).hexdigest()
        cursor.execute('INSERT INTO student_web_accounts (email, uni_id, password, is_verified) VALUES (?, ?, ?, 0)', (email, university_id, hashed_pass))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # الإيميل مسجل مسبقاً
    finally:
        conn.close()

def verify_user_account(email):
    conn = sqlite3.connect('independent_college.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE student_web_accounts SET is_verified = 1 WHERE email = ?', (email,))
    conn.commit()
    conn.close()

def check_login(email, password):
    conn = sqlite3.connect('independent_college.db')
    cursor = conn.cursor()
    hashed_pass = hashlib.sha256(str.encode(password)).hexdigest()
    cursor.execute('''
        SELECT swa.is_verified, os.full_name, os.faculty, os.department 
        FROM student_web_accounts swa
        JOIN official_students os ON swa.uni_id = os.uni_id
        WHERE swa.email = ? AND swa.password = ?
    ''', (email, hashed_pass))
    result = cursor.fetchone()
    conn.close()
    return result

def update_password(email, new_password):
    conn = sqlite3.connect('independent_college.db')
    cursor = conn.cursor()
    hashed_pass = hashlib.sha256(str.encode(new_password)).hexdigest()
    cursor.execute('UPDATE student_web_accounts SET password = ? WHERE email = ?', (hashed_pass, email))
    conn.commit()
    conn.close()

# --- 3. تشغيل واجهات الموقع (Streamlit) ---
st.set_page_config(page_title="بوابة جامعة اللاذقية الرقمية", page_icon="🎓")

# تهيئة قاعدة البيانات المستقلة تلقائياً عند التشغيل الأول للبرنامج
init_independent_db()

if 'page' not in st.session_state:
    st.session_state.page = 'login' 
if 'auth_data' not in st.session_state:
    st.session_state.auth_data = {} 

# --- الواجهة 1: تسجيل الدخول (Login) ---
if st.session_state.page == 'login':
    st.title("🎓 تسجيل الدخول | بوابة الخدمات الطلابية")
    st.subheader("كلية الهندسة المدنية - جامعة اللاذقية")
    
    email = st.text_input("البريد الإلكتروني:")
    password = st.text_input("كلمة المرور:", type="password")
    
    col_log1, col_log2 = st.columns(2)
    with col_log1:
        if st.button("تسجيل الدخول 🚪", use_container_width=True):
            user = check_login(email, password)
            if user:
                if user[0] == 1: 
                    st.session_state.auth_data['name'] = user[1]
                    st.session_state.auth_data['faculty'] = user[2]
                    st.session_state.auth_data['dept'] = user[3]
                    st.session_state.page = 'main_app'
                    st.rerun()
                else:
                    st.warning("⚠️ هذا الحساب معلق، يرجى تفعيله برمز الـ OTP أولاً.")
            else:
                st.error("❌ البريد الإلكتروني أو كلمة المرور غير صحيحة.")
                
    with col_log2:
        if st.button("نسيت كلمة المرور؟ 🔍", use_container_width=True):
            st.session_state.page = 'forgot'
            st.rerun()
            
    st.divider()
    if st.button("مستخدم جديد؟ إنشاء حساب طالب 📝", use_container_width=True):
        st.session_state.page = 'signup'
        st.rerun()

# --- الواجهة 2: إنشاء حساب جديد والتحقق من سجلات الكلية (Sign Up) ---
elif st.session_state.page == 'signup':
    st.title("📝 نموذج تسجيل طالب جديد")
    
    student_name = st.text_input("الاسم الكامل (كما هو مسجل في الكلية):")
    uni_id = st.text_input("الرقم الجامعي:")
    student_email = st.text_input("البريد الإلكتروني الحقيقي:")
    student_pass = st.text_input("كلمة المرور الجديدة:", type="password")
    confirm_pass = st.text_input("تأكيد كلمة المرور:", type="password")
    
    if st.button("التحقق وإرسال رمز الأمان 🚀", use_container_width=True):
        if student_pass != confirm_pass:
            st.error("❌ كلمات المرور غير متطابقة!")
        elif not (student_name and uni_id and student_email and student_pass):
            st.warning("⚠️ يرجى ملء كافة الحقول المذكورة.")
        else:
            college_info = check_college_records(uni_id, student_name)
            if college_info:
                if add_user_account(student_email, uni_id, student_pass):
                    otp = str(random.randint(100000, 999999))
                    st.session_state.auth_data['otp'] = otp
                    st.session_state.auth_data['email'] = student_email
                    st.session_state.auth_data['action'] = 'verify_account'
                    
                    with st.spinner("جاري إرسال رمز الأمان إلى بريدك..."):
                        body = f"مرحباً بك يا مهندس {student_name}!\nرمز الأمان الخاص بتفعيل حسابك الجامعي هو: {otp}"
                        sent = send_email(student_email, "تفعيل الحساب الجامعي", body)
                    
                    if sent:
                        st.success(f"✅ تم التحقق من هويتك بنجاح وإرسال الرمز إلى {student_email}")
                        st.session_state.page = 'verify'
                        st.rerun()
                    else:
                        st.error("❌ فشل إرسال الإيميل، يرجى التحقق من اتصالك بالإنترنت.")
                else:
                    st.error("❌ هذا البريد الإلكتروني مسجل مسبقاً بنظام الكلية!")
            else:
                st.error("❌ عذراً، اسمك أو رقمك الجامعي غير موجود في معلومات الكلية الرسمية. الرجاء التسجيل بالكلية أولاً ثم إعادة المحاولة.")
                
    if st.button("العودة لصفحة الدخول"):
        st.session_state.page = 'login'
        st.rerun()

# --- الواجهة 3: شاشة إدخال رمز الأمان وتأكيده (Verification) ---
elif st.session_state.page == 'verify':
    st.title("🔢 نافذة التحقق من رمز الأمان")
    st.write(f"الرجاء إدخال الرمز المرسل إلى: **{st.session_state.auth_data.get('email')}**")
    
    input_otp = st.text_input("أدخل الرمز المكون من 6 أرقام:")
    
    if st.button("تأكيد الحساب والإنهاء ✅", use_container_width=True):
        if input_otp == st.session_state.auth_data.get('otp'):
            if st.session_state.auth_data.get('action') == 'verify_account':
                verify_user_account(st.session_state.auth_data.get('email'))
                st.success("🎉 ممتاز! تم تفعيل حسابك بنجاح. يمكنك الآن الدخول.")
                st.session_state.page = 'login'
            elif st.session_state.auth_data.get('action') == 'reset_password':
                st.session_state.page = 'new_password_page'
            st.rerun()
        else:
            st.error("❌ الرمز غير صحيح، يرجى المحاولة مرة أخرى.")

# --- الواجهة 4: نسيت كلمة المرور (Forgot Password) ---
elif st.session_state.page == 'forgot':
    st.title("🔍 استعادة كلمة المرور")
    forgot_email = st.text_input("أدخل بريدك الإلكتروني المسجل لدينا:")
    
    if st.button("إرسال رمز إعادة التعيين 📩", use_container_width=True):
        conn = sqlite3.connect('independent_college.db')
        c = conn.cursor()
        c.execute('SELECT email FROM student_web_accounts WHERE email = ?', (forgot_email,))
        email_exists = c.fetchone()
        conn.close()
        
        if email_exists:
            otp = str(random.randint(100000, 999999))
            st.session_state.auth_data['otp'] = otp
