import streamlit as st
import sqlite3
import hashlib
import random
import smtplib
from email.mime.text import MIMEText

# --- 1. إعدادات السيرفر لإرسال الإيميلات (تم التحديث ببياناتك) ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "yaroubnassif71@gmail.com" 
SENDER_PASSWORD = "gqnk vttk kifk czbt"  # الرمز السحري الخاص بك

def send_otp_email(receiver_email, otp_code):
    """دالة لإرسال رمز التأكيد إلى إيميل المستخدم بشكل حقيقي"""
    msg = MIMEText(f"مرحباً بك يا مهندس! رمز التأكيد الخاص بك لتفعيل حسابك هو: {otp_code}")
    msg['Subject'] = 'رمز تأكيد التسجيل - تطبيق الهندسة المدنية'
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        return True
    except Exception as e:
        # في حال حدوث خطأ غير متوقع، سيظهر في التيرمينال
        print(f"حدث خطأ أثناء الإرسال: {e}")
        return False

# --- 2. إدارة قاعدة البيانات SQLite ---
def init_db():
    conn = sqlite3.connect('users_db.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT,
            is_verified INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(email, password):
    conn = sqlite3.connect('users_db.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (email, password, is_verified) VALUES (?, ?, 0)', (email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user_status(email):
    conn = sqlite3.connect('users_db.db')
    c = conn.cursor()
    c.execute('UPDATE users SET is_verified = 1 WHERE email = ?', (email,))
    conn.commit()
    conn.close()

def check_login(email, password):
    conn = sqlite3.connect('users_db.db')
    c = conn.cursor()
    c.execute('SELECT is_verified FROM users WHERE email = ? AND password = ?', (email, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result

# --- 3. إعدادات واجهة الويب وعناصر التحكم ---
st.set_page_config(page_title="نظام إدارة المستخدمين الهندسي", page_icon="🔐")
init_db()

if 'page_state' not in st.session_state:
    st.session_state.page_state = 'login'
if 'temp_email' not in st.session_state:
    st.session_state.temp_email = ''
if 'generated_otp' not in st.session_state:
    st.session_state.generated_otp = ''

# --- الواجهة الأولى: تسجيل الدخول (Login) ---
if st.session_state.page_state == 'login':
    st.title("🔐 تسجيل الدخول إلى منصة المهندسين")
    
    login_email = st.text_input("البريد الإلكتروني:")
    login_pass = st.text_input("كلمة المرور:", type="password")
    
    if st.button("دخول"):
        user_status = check_login(login_email, login_pass)
        if user_status:
            if user_status[0] == 1: 
                st.session_state.page_state = 'main_app'
                st.rerun()
            else:
                st.warning("هذا الحساب لم يتم تفعيله بعد بواسطة رمز OTP! يرجى إعادة التسجيل بنفس البريد لتفعيله.")
        else:
            st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة!")
            
    st.write("---")
    if st.button("ليس لديك حساب؟ سجل الآن"):
        st.session_state.page_state = 'signup'
        st.rerun()

# --- الواجهة الثانية: إنشاء حساب جديد (Sign Up) ---
elif st.session_state.page_state == 'signup':
    st.title("📝 إنشاء حساب مهندس جديد")
    
    new_email = st.text_input("أدخل بريدك الإلكتروني الحقيقي لتلقي الرمز:")
    new_pass = st.text_input("أدخل كلمة المرور الخاصة بك:", type="password")
    confirm_pass = st.text_input("تأكيد كلمة المرور:", type="password")
    
    if st.button("إرسال رمز التأكيد 🚀"):
        if new_pass != confirm_pass:
            st.error("كلمات المرور غير متطابقة!")
        elif new_email == "" or new_pass == "":
            st.warning("الرجاء ملء كافة الحقول.")
        else:
            if add_user(new_email, new_pass):
                otp = str(random.randint(100000, 999999))
                st.session_state.generated_otp = otp
                st.session_state.temp_email = new_email
                
                with st.spinner("جاري إرسال الرمز إلى بريدك الإلكتروني..."):
                    sent = send_otp_email(new_email, otp)
                
                if sent:
                    st.success(f"تم إرسال رمز الـ OTP بنجاح إلى: {new_email}")
                    st.session_state.page_state = 'verify'
                    st.rerun()
                else:
                    st.error("فشل إرسال الإيميل. تأكد من اتصال الإنترنت أو إعدادات الحساب.")
            else:
                st.error("هذا البريد الإلكتروني مسجل بالفعل لدينا!")
                
    if st.button("العودة لصفحة تسجيل الدخول"):
        st.session_state.page_state = 'login'
        st.rerun()

# --- الواجهة الثالثة: تأكيد الرمز (Verification) ---
elif st.session_state.page_state == 'verify':
    st.title("🔢 تفعيل الحساب برمز الـ OTP")
    st.write(f"تفقد صندوق الوارد في الإيميل: **{st.session_state.temp_email}**")
    
    user_otp = st.text_input("أدخل الرمز المكون من 6 أرقام هنا:")
    
    if st.button("تأكيد الحساب وتفعيله ✅"):
        if user_otp == st.session_state.generated_otp:
            verify_user_status(st.session_state.temp_email)
            st.success("تم تفعيل حسابك بنجاح! يمكنك الآن تسجيل الدخول.")
            st.session_state.page_state = 'login'
            st.rerun()
        else:
            st.error("الرمز المدخل غير صحيح! حاول مجدداً.")

# --- الواجهة الرابعة: التطبيق الرئيسي بعد الدخول (Main App) ---
elif st.session_state.page_state == 'main_app':
    st.title("🏗️ أهلاً بك داخل تطبيق الويب الهندسي الآمن!")
    st.balloons() 
    
    st.markdown("""
    ### تهانينا يا هندسة! 🎉
    التطبيق يعمل الآن بالكامل ونظام التحقق والـ OTP يرسل رسائل حقيقية من سيرفرك الخاص.
    """)
    
    if st.button("تسجيل الخروج 🚪"):
        st.session_state.page_state = 'login'
        st.rerun()
