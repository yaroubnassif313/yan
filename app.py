import streamlit as st
import sqlite3
import hashlib
import random
import smtplib
from email.mime.text import MIMEText

DB_NAME = "Engineering_Library.db"

# --- 1. إعدادات سيرفر الإرسال ---
SMTP_SERVER = "://gmail.com"
SMTP_PORT = 465
SENDER_EMAIL = "yaroubnassif71@gmail.com" 
SENDER_PASSWORD = "gqnk vttk kifk czbt" 

def send_email(receiver_email, subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        return True
    except Exception:
        return False

# --- 2. إدارة العمليات الحسابية والتحقق مع "المنصة الكبرى" ---
def check_student_record(serial_number, full_name, national_id):
    """التحقق الذكي: هل الطالب موجود بسجلات الكلية ومطابق لهويته الوطنية؟"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT is_verified FROM access_gate 
        WHERE serial_number = ? AND full_name = ? AND national_id = ?
    ''', (serial_number, full_name, national_id))
    result = cursor.fetchone()
    conn.close()
    return result

def register_web_account(serial_number, email, password):
    """تحديث البريد وتشفير الباسورد لتفعيل حساب الطالب الحقيقي"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        hashed_pass = hashlib.sha256(str.encode(password)).hexdigest()
        cursor.execute('''
            UPDATE access_gate 
            SET email = ?, password = ?, is_verified = 0 
            WHERE serial_number = ?
        ''', (email, hashed_pass, serial_number))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def activate_account(email):
    """تفعيل الحساب نهائياً بعد كتابة الـ OTP الصحيح"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('UPDATE access_gate SET is_verified = 1 WHERE email = ?', (email,))
    conn.commit()
    conn.close()

def check_login(email, password):
    """تسجيل الدخول الآمن ومطابقة كلمة المرور المشفرة"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    hashed_pass = hashlib.sha256(str.encode(password)).hexdigest()
    cursor.execute('SELECT is_verified, full_name FROM access_gate WHERE email = ? AND password = ?', (email, hashed_pass))
    result = cursor.fetchone()
    conn.close()
    return result

def check_email_for_reset(email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM access_gate WHERE email = ? AND is_verified = 1', (email,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_password(email, new_password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    hashed_pass = hashlib.sha256(str.encode(new_password)).hexdigest()
    cursor.execute('UPDATE access_gate SET password = ? WHERE email = ?', (hashed_pass, email))
    conn.commit()
    conn.close()

# --- 3. بناء واجهات الويب الديناميكية (Streamlit) ---
st.set_page_config(page_title="المنصة الكبرى | كلية الهندسة المدنية", page_icon="🎓")

if 'page' not in st.session_state:
    st.session_state.page = 'login' 
if 'auth_data' not in st.session_state:
    st.session_state.auth_data = {} 

# --- الواجهة 1: تسجيل الدخول ---
if st.session_state.page == 'login':
    st.title("🎓 تسجيل الدخول | المنصة الكبرى")
    st.subheader("كلية الهندسة المدنية - جامعة اللاذقية")
    
    email = st.text_input("البريد الإلكتروني الجامعي:")
    password = st.text_input("كلمة المرور:", type="password")
    
    col_log1, col_log2 = st.columns(2)
    with col_log1:
        if st.button("تسجيل الدخول 🚪", use_container_width=True):
            user = check_login(email, password)
            if user:
                if user[0] == 1: 
                    st.session_state.auth_data['name'] = user[1]
                    st.session_state.page = 'main_app'
                    st.rerun()
                else:
                    st.warning("⚠️ الحساب معلق، يرجى تفعيله برمز الـ OTP أولاً.")
            else:
                st.error("❌ البريد الإلكتروني أو كلمة المرور غير صحيحة.")
                
    with col_log2:
        if st.button("نسيت كلمة المرور؟ 🔍", use_container_width=True):
            st.session_state.page = 'forgot'
            st.rerun()
            
    st.divider()
    if st.button("طالب جديد؟ سجل حسابك الموثق بالرقم الوطني 📝", use_container_width=True):
        st.session_state.page = 'signup'
        st.rerun()

# --- الواجهة 2: إنشاء حساب طالب جديد بالفحص الثلاثي المطور ---
elif st.session_state.page == 'signup':
    st.title("📝 بوابة إنشاء حساب طالب جديد")
    
    student_name = st.text_input("الاسم الكامل (كما هو مسجل بالكلية):")
    uni_id = st.text_input("الرقم الجامعي (Serial Number):")
    nat_id = st.text_input("الرقم الوطني المكون من 11 رقماً:")
    student_email = st.text_input("البريد الإلكتروني الحقيقي (Gmail):")
    student_pass = st.text_input("أدخل كلمة مرور جديدة للمنصة:", type="password")
    confirm_pass = st.text_input("تأكيد كلمة المرور الجديدة:", type="password")
    
    if st.button("التحقق والمصادقة الأمنية 🚀", use_container_width=True):
        if student_pass != confirm_pass:
            st.error("❌ كلمات المرور غير متطابقة!")
        elif not (student_name and uni_id and nat_id and student_email and student_pass):
            st.warning("⚠️ يرجى تعبئة كافة الحقول المطلوبة.")
        elif not student_email.endswith("@gmail.com"):
            st.error("❌ عذراً، يجب استخدام بريد إلكتروني حقيقي ينتهي بـ @gmail.com.")
        else:
            with st.spinner("جاري فحص هويتك في سجلات الكلية..."):
                # الفحص الثلاثي الحقيقي من جدولك الأصلي
                record_exists = check_student_record(uni_id, student_name, nat_id)
                
                if record_exists:
                    if register_web_account(uni_id, student_email, student_pass):
                        otp = str(random.randint(100000, 999999))
                        st.session_state.auth_data['otp'] = otp
                        st.session_state.auth_data['email'] = student_email
                        st.session_state.auth_data['action'] = 'verify_account'
                        
                        body = f"مرحباً بك يا مهندس {student_name}!\nرمز الأمان الخاص بتفعيل حسابك على المنصة الكبرى هو: {otp}"
                        sent = send_email(student_email, "تفعيل حساب المنصة الكبرى", body)
                        
                        if sent:
                            st.success(f"✅ تم إرسال الرمز بنجاح إلى {student_email}")
                        else:
                            st.warning("⚠️ تم توليد الرمز سحابياً ولكن تعذر الاتصال بسيرفر الإرسال.")
                            st.info(f"⚙️ وضع المطور التجريبي: الرمز هو: {otp}")
                            
                        st.session_state.page = 'verify'
                        st.rerun()
                else:
                    st.error("❌ عذراً، اسمك أو رقمك الجامعي أو رقمك الوطني غير موجود في السجلات الرسمية الكبرى للكلية. راجع الإدارة وأعد المحاولة.")
                    
    if st.button("العودة لصفحة الدخول"):
        st.session_state.page = 'login'
        st.rerun()

# --- الواجهة 3: شاشة تأكيد الرمز ---
elif st.session_state.page == 'verify':
    st.title("🔢 نافذة التحقق من رمز الأمان")
    st.write(f"أدخل الرمز المخصص للحساب: **{st.session_state.auth_data.get('email')}**")
    
    if 'otp' in st.session_state.auth_data:
        st.caption(f"(وضع المطور: الرمز الحالي هو {st.session_state.auth_data['otp']})")
        
    input_otp = st.text_input("أدخل الرمز المكون من 6 أرقام:")
    
    if st.button("تأكيد وتفعيل ✅", use_container_width=True):
        if input_otp == st.session_state.auth_data.get('otp'):
            if st.session_state.auth_data.get('action') == 'verify_account':
                activate_account(st.session_state.auth_data.get('email'))
                st.success("🎉 ممتاز! تم تفعيل حسابك بنجاح في المنصة الكبرى. يمكنك الدخول.")
                st.session_state.page = 'login'
            elif st.session_state.auth_data.get('action') == 'reset_password':
                st.session_state.page = 'new_password_page'
            st.rerun()
        else:
            st.error("❌ الرمز غير صحيح، يرجى المحاولة مرة أخرى.")

# --- الواجهة 4: نسيت كلمة المرور ---
elif st.session_state.page == 'forgot':
    st.title("🔍 استعادة كلمة المرور")
    forgot_email = st.text_input("أدخل بريدك الإلكتروني المسجل:")
    
    if st.button("إرسال رمز إعادة التعيين 📩", use_container_width=True):
        if check_email_for_reset(forgot_email):
            otp = str(random.randint(100000, 999999))
            st.session_state.auth_data['otp'] = otp
            st.session_state.auth_data['email'] = forgot_email
            st.session_state.auth_data['action'] = 'reset_password'
            
            body = f"لقد طلبت إعادة تعيين كلمة المرور للمنصة الكبرى. رمز الأمان هو: {otp}"
            sent = send_email(forgot_email, "إعادة تعيين كلمة المرور", body)
            
            if sent:
                st.success("✅ تم إرسال الرمز بنجاح.")
            else:
                st.warning("⚠️ استخدم رمز المطور الموضح بالأسفل للتجربة السحابية.")
                
            st.session_state.page = 'verify'
            st.rerun()
        else:
            st.error("❌ هذا البريد الإلكتروني غير مسجل ومفعّل في نظامنا.")
            
    if st.button("إلغاء والعودة"):
        st.session_state.page = 'login'
        st.rerun()

# --- الواجهة 5: تعيين كلمة المرور الجديدة ---
elif st.session_state.page == 'new_password_page':
    st.title("🔒 تعيين كلمة مرور جديدة")
    new_p = st.text_input("كلمة المرور الجديدة:", type="password")
    confirm_new_p = st.text_input("تأكيد كلمة المرور الجديدة:", type="password")

    if st.button("تأكيد التغيير"):
        if new_p == confirm_new_p:
            update_password(st.session_state.auth_data.get('email'), new_p)
            st.success("✅ تم تغيير كلمة المرور بنجاح.")
            st.session_state.page = 'login'
        else:
            st.error("❌ تأكيد كلمة المرور غير متطابق.")
            
