# -*- coding: utf-8 -*-
import streamlit as st
import sqlite3
import hashlib
import random
import smtplib
from email.mime.text import MIMEText
import os

DB_NAME = "Engineering_Library.db"

# --- 1. الإعدادات الهندسية والهوية البصرية ---
st.set_page_config(
    page_title="Civil Engineering Hub", 
    layout="centered", 
    initial_sidebar_state="expanded"
)

# تنسيق CSS احترافي (Modern UI المطور والمدعوم هندسياً)
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* تصميم البطاقات والأزرار التفاعلية */
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 5em;
        font-weight: bold;
        font-size: 16px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
        transition: 0.3s;
        margin-bottom: 10px;
    }
    .stButton>button:hover {
        transform: translateY(-5px);
        background-color: #E94560;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. محرك قاعدة البيانات والوظائف الأمنية الذكية ---
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """تشفير آمن لحماية كلمات المرور وفق معيار SHA-256"""
    return hashlib.sha256(str.encode(password)).hexdigest()

# إعدادات سيرفر الإرسال للـ OTP
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

# --- 3. إدارة حالة التطبيق واحتفاظ الجلسات (Session State) ---
keys = ['step', 'user_data', 'is_admin_login', 'admin_auth', 'page', 'temp_user', 'search_q', 'otp_code', 'signup_data']
for key in keys:
    if key not in st.session_state:
        st.session_state[key] = False if 'auth' in key or 'admin' in key else (None if key != 'step' else 'welcome')

# --- 4. القائمة الجانبية (الدعم الفني والتحكم الخفي) ---
with st.sidebar:
    if st.button("⚙️", help="Admin Access"):
        st.session_state.is_admin_login = True
        st.rerun()
    
    if os.path.exists("logo.jpg"): 
        st.image("logo.jpg", use_container_width=True)
    
    st.title(" Gaza 📞 الدعم الفني")
    st.write("🟢 **واتساب (انسخ الرقم):**")
    st.code("0992325041")
    st.link_button("فتح واتساب", "https://wa.me", use_container_width=True)
    
    st.write("💬 **تليجرام (انسخ المعرف):**")
    st.code("@AMS0012")
    st.link_button("فتح تليجرام", "https://t.me", use_container_width=True)

# --- 5. لوحة التحكم السرية للمسؤول (تحقق + إدارة كاملة شاملة ومحمية) ---
if st.session_state.is_admin_login and not st.session_state.admin_auth:
    st.title("🔐 تحقق المسؤول")
    a_name = st.text_input("الاسم الثلاثي للمسؤول")
    a_pass = st.text_input("كلمة مرور المسؤول", type="password")
    if st.button("دخول للوحة التحكم"):
        db = get_db()
        admin = db.execute("SELECT * FROM admins WHERE full_name=? AND admin_password=?", (a_name, a_pass)).fetchone()
        db.close()
        if admin:
            st.session_state.admin_auth = True
            st.rerun()
        else: 
            st.error("بيانات الإدارة غير مصرح بها.")
    if st.button("رجوع"): 
        st.session_state.is_admin_login = False
        st.rerun()

elif st.session_state.admin_auth:
    st.title("🛡️ مركز الإدارة الشامل للمنصة")
    if st.button("⬅️ تسجيل خروج المسؤول"):
        st.session_state.admin_auth = False
        st.session_state.is_admin_login = False
        st.rerun()
    
    adm_tab1, adm_tab2, adm_tab3, adm_tab4 = st.tabs(["👥 الطلاب المصرح لهم", "📚 الأرشيف والمحاضرات", "📢 الإعلانات والأخبار", "📊 النتائج الامتحانية"])
    
    with adm_tab1:
        st.subheader("إضافة طالب رسمي إلى سجلات الكلية")
        n_name = st.text_input("الاسم الثلاثي للطالب:")
        n_serial = st.text_input("الرقم الجامعي (Serial Number):")
        n_national = st.text_input("الرقم الوطني المكون من 11 رقم:")
        if st.button("حفظ الطالب بالسجلات"):
            if n_name and n_serial and n_national:
                db = get_db()
                try:
                    # إضافة الحساب بـ password افتراضية لحين تفعيل الطالب له بالإيميل والـ OTP
                    db.execute('''
                        INSERT INTO access_gate (full_name, serial_number, national_id, password, is_verified) 
                        VALUES (?, ?, ?, '0000', 0)
                    ''', (n_name, n_serial, n_national))
                    db.commit()
                    st.success(f"✅ تم حفظ الطالب {n_name} بنجاح في السجلات الرسمية.")
                except sqlite3.IntegrityError:
                    st.warning("⚠️ هذا الرقم الجامعي أو الرقم الوطني مسجل مسبقاً.")
                finally:
                    db.close()
            else:
                st.error("يرجى ملء جميع الحقول.")

    with adm_tab2:
        st.subheader("إضافة محاضرة جديدة للأرشيف")
        years = ["السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"]
        sel_y = st.selectbox("اختر السنة الدراسية", years)
        
        db = get_db()
        subs = db.execute("SELECT DISTINCT subject_name FROM subjects WHERE academic_year=?", (sel_y,)).fetchall()
        db.close()
        
        sel_sub = st.selectbox("اختر المادة المعتمدة", [s['subject_name'] for s in subs])
        lec_t = st.text_input("عنوان أو رقم المحاضرة:")
        lec_u = st.text_input("رابط الملف (Google Drive/Telegram):")
        if st.button("إضافة المحاضرة رسميًا"):
            if lec_t and lec_u:
                db = get_db()
                db.execute("INSERT INTO university_archive (academic_year, subject_name, lecture_title, file_url) VALUES (?,?,?,?)", (sel_y, sel_sub, lec_t, lec_u))
                db.commit()
                db.close()
                st.success("✅ تمت الإضافة للأرشيف الجامعي بنجاح.")
            else:
                st.error("يرجى إكمال عنوان ورابط المحاضرة.")

    with adm_tab3:
        st.subheader("نشر إعلان أو خبر جامعي")
        n_title = st.text_input("عنوان الخبر:")
        n_text = st.text_area("تفاصيل الإعلان:")
        n_target = st.selectbox("السنة المستهدفة", ["العام", "السنة الأولى", "السنة الثانية", "السنة الثالثة", "السنة الرابعة", "السنة الخامسة"])
        if st.button("نشر الإعلان"):
            if n_title and n_text:
                db = get_db()
                db.execute("INSERT INTO college_news (news_title, news_text, target_year) VALUES (?,?,?)", (n_title, n_text, n_target))
                db.commit()
                db.close()
                st.success("📢 تم نشر الإعلان بنجاح على لوحة الطلاب.")

    with adm_tab4:
        st.subheader("رفع النتيجة الامتحانية لمادة")
        r_year = st.selectbox("السنة الدراسية للنتيجة", years)
        r_title = st.text_input("عنوان النتيجة (مثال: نتيحة خرسانة 1 - الدورة الأولى):")
        r_url = st.text_input("رابط ملف النتيجة PDF:")
        if st.button("إرسال النتيجة"):
            if r_title and r_url:
                db = get_db()
                db.execute("INSERT INTO exam_results (academic_year, result_title, pdf_url) VALUES (?,?,?)", (r_year, r_title, r_url))
                db.commit()
                db.close()
                st.success("📊 تم إدراج النتيجة الامتحانية بنجاح.")

# --- 6. واجهة المستخدم الرئيسية وتدفق الواجهات (The App Flow) ---
if st.session_state.step == 'welcome':
    if os.path.exists("logo.jpg"): 
        st.image("logo.jpg", use_container_width=200)
    st.title("كلية الهندسة المدنية")
    st.write("المكتبة الرقمية والمنصة الأكاديمية الرسمية الكبرى")
    st.divider()
    
    if st.button("دخول الطلاب | Student Access", type="primary", use_container_width=True):
        st.session_state.step = 'login'
        st.rerun()

elif st.session_state.step == 'login':
    st.header("🔑 تسجيل الدخول")
    u_email = st.text_input("البريد الإلكتروني المعتمد (Gmail):")
    u_password = st.text_input("كلمة المرور:", type="password")
    
    if st.button("دخول آمن", type="primary"):
        if u_email and u_password:
            db = get_db()
            # التحقق مع تشفير الباسورد المكتوب لمطابقته مع الهاش المخزن
            user = db.execute("SELECT * FROM access_gate WHERE email=? AND password=?", (u_email, hash_password(u_password))).fetchone()
            db.close()
            if user:
                if user['is_verified'] == 1:
                    st.session_state.user_data = user
                    st.session_state.step = 'dashboard'
                    st.rerun()
                else:
                    st.warning("⚠️ هذا الحساب معلق، يرجى إعادة تعيينه أو تفعيله عبر التسجيل الجديد.")
            else:
                st.error("❌ عذراً، البريد الإلكتروني أو كلمة المرور غير صحيحة.")
                
    st.divider()
    if st.button("طالب جديد؟ تفعيل وتوثيق الحساب بالرقم الوطني 📝"):
        st.session_state.step = 'signup'
        st.rerun()
    if st.button("رجوع"): 
        st.session_state.step = 'welcome'
        st.rerun()

elif st.session_state.step == 'signup':
    st.header("📝 تفعيل حساب طالب جديد")
    st.caption("أمن النظام: يجب مطابقة الاسم الكامل، الرقم الجامعي، والرقم الوطني مع سجلات الكلية.")
    
    s_name = st.text_input("الاسم الثلاثي المعتمد:")
    s_serial = st.text_input("الرقم الجامعي:")
    s_national = st.text_input("الالرقم الوطني (11 رقم):")
    s_email = st.text_input("بريدك الإلكتروني الحقيقي لتلقي الرمز:")
    s_pass = st.text_input("اختر كلمة مرور جديدة للمنصة:", type="password")
    
    if st.button("التحقق والمصادقة الأمنية 🚀", type="primary"):
        if s_name and s_serial and s_national and s_email and s_pass:
            if not s_email.endswith("@gmail.com"):
                st.error("❌ يجب استخدام بريد إلكتروني حقيقي ينتهي بـ @gmail.com.")
            else:
                with st.spinner("جاري التحقق من الهوية..."):
                    # هنا يتم التحقق من الهوية باستخدام قاعدة البيانات
                    is_verified = check_student_record(s_serial, s_name, s_national)
                    if is_verified:
                        # إذا كانت الهوية صحيحة، يتم إنشاء الحساب
                        if register_web_account(s_serial, s_email, s_pass):
                            st.success("✅ تم إنشاء الحساب بنجاح! تحقق من بريدك الإلكتروني لتفعيل الحساب.")
                            # هنا يمكن إرسال رمز التفعيل عبر البريد الإلكتروني
                        else:
                            st.error("❌ حدث خطأ أثناء إنشاء الحساب.")
                    else:
                        st.error("❌ معلومات الهوية غير صحيحة.")