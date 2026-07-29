import streamlit as st
import sqlite3
import hashlib
import random
import smtplib
from email.mime.text import MIMEText

# --- 1. إعدادات السيرفر لإرسال الإيميلات (Gmail كمثال) ---
# تنبيه: ضع إيميلك وكلمة مرور التطبيقات الخاصة بك هنا ليعمل الإرسال الحقيقي
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "your_email@gmail.com" 
SENDER_PASSWORD = "your_app_password" # كلمة مرور التطبيقات من جوجل وليس كلمة سر الإيميل العادية

def send_otp_email(receiver_email, otp_code):
    """دالة لإرسال رمز التأكيد إلى إيميل المستخدم"""
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
        # في حال فشل الإرسال الحقيقي (بسبب عدم إعداد الإيميل)، سنطبع الرمز في التيرمينال للتجربة
        print(f"فشل إرسال الإيميل الحقيقي. الرمز للتجربة هو: {otp_code}")
        return False

# --- 2. إدارة قاعدة البيانات SQLite ---
def init_db():
    conn = sqlite3.connect('users_db.db')
    c = conn.cursor()
    # إنشاء جدول المستخدمين إذا لم يكن موجوداً
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
    """تشفير كلمة المرور لحماية خصوصية المستخدمين"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def add_user(email, password):
    conn = sqlite3.connect('users_db.db')
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (email, password, is_verified) VALUES (?, ?, 0)', (email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False # الإيميل موجود مسبقاً
    finally:
        conn.close()

def verify_user_status(email):
    """تفعيل الحساب في قاعدة البيانات بعد كتابة الرمز الصحيح"""
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

# تعريف متغيرات الجلسة (Session State) للحفاظ على حالة المستخدم أثناء التنقل
if 'page_state' not in st.session_state:
    st.session_state.page_state = 'login' # الصفحات المتاحة: login, signup, verify, main_app
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
            if user_status[0] == 1: # الحساب مفعّل
                st.session_state.page_state = 'main_app'
                st.rerun()
            else:
                st.warning("هذا الحساب لم يتم تفعيله بعد بواسطة رمز OTP! يرجى إعادة التسجيل أو التفعيل.")
        else:
            st.error("البريد الإلكتروني أو كلمة المرور غير صحيحة!")
            
    st.write("---")
    if st.button("ليس لديك حساب؟ سجل الآن"):
        st.session_state.page_state = 'signup'
        st.rerun()

# --- الواجهة الثانية: إنشاء حساب جديد (Sign Up) ---
elif st.session_state.page_state == 'signup':
    st.title("📝 إنشاء حساب مهندس جديد")
    
    new_email = st.text_input("أدخل بريدك الإلكتروني الحقيقي:")
    new_pass = st.text_input("أدخل كلمة المرور الخاصة بك:", type="password")
    confirm_pass = st.text_input("تأكيد كلمة المرور:", type="password")
    
    if st.button("إرسال رمز التأكيد 🚀"):
        if new_pass != confirm_pass:
            st.error("كلمات المرور غير متطابقة!")
        elif new_email == "" or new_pass == "":
            st.warning("الرجاء ملء كافة الحقول.")
        else:
            # محاولة إضافة المستخدم لقاعدة البيانات
            if add_user(new_email, new_pass):
                # توليد رمز عشوائي من 6 أرقام
                otp = str(random.randint(100000, 999999))
                st.session_state.generated_otp = otp
                st.session_state.temp_email = new_email
                
                # محاولة إرسال الإيميل
                with st.spinner("جاري إرسال الرمز إلى بريدك..."):
                    sent = send_otp_email(new_email, otp)
                
                st.success("تم تسجيل بياناتك بنجاح!")
                if sent:
                    st.info("تم إرسال رمز OTP إلى بريدك الإلكتروني الحقيقي.")
                else:
                    st.info("تنبيه التجربة الافتراضية: تفقد شاشة Terminal السوداء في VS Code لرؤية الرمز والنسخ منه لحين إعداد سيرفر إيميلك.")
                
                st.session_state.page_state = 'verify'
                st.rerun()
            else:
                st.error("هذا البريد الإلكتروني مسجل بالفعل لدينا!")
                
    if st.button("العودة لصفحة تسجيل الدخول"):
        st.session_state.page_state = 'login'
        st.rerun()

# --- الواجهة الثالثة: تأكيد الرمز (Verification) ---
elif st.session_state.page_state == 'verify':
    st.title("🔢 تفعيل الحساب برمز الـ OTP")
    st.write(f"تم إرسال رمز تأكيد إلى الحساب: **{st.session_state.temp_email}**")
    
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
    st.title("🏗️ أهلاً بك داخل تطبيق الويب الهندسي المغلق!")
    st.balloons() # تأثير بصري مبهج للاحتفال بالنجاح
    
    st.markdown("""
    ### تهانينا! 🎉
    لقد نجحت في عبور نظام الأمان وقاعدة البيانات بامتياز. 
    هذه الصفحة فارغة الآن كما طلبت، وجاهزة تماماً لنضع فيها كود حساب الجوائز السابق، أو أي أداة هندسية تحلم ببرمجتها.
    """)
    
    if st.button("تسجيل الخروج 🚪"):
        st.session_state.page_state = 'login'
        st.rerun()
