import streamlit as st
import sqlite3
import hashlib

# --- 1. إدارة العمليات الحسابية والتحقق عبر قاعدة بيانات الوزارة ---
def check_triple_auth(national_id, university_id, full_name):
    """التحقق الثلاثي: مطابقة البيانات مع سجلات الوزارة الرسمية"""
    conn = sqlite3.connect('ministry_system.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT faculty, department FROM official_ministry_records 
        WHERE national_id = ? AND university_id = ? AND full_name = ?
    ''', (national_id, university_id, full_name))
    result = cursor.fetchone()
    conn.close()
    return result # يعيد (الكلية، القسم) إذا تطابقت البيانات الثلاثية، أو None إذا أخطأ بأي حقل

def check_email_exists(email):
    """التحقق من عدم تكرار تسجيل البريد الإلكتروني في الموقع"""
    conn = sqlite3.connect('ministry_system.db')
    cursor = conn.cursor()
    cursor.execute('SELECT email FROM platform_user_accounts WHERE email = ?', (email,))
    result = cursor.fetchone()
    conn.close()
    return result

def add_new_user(email, national_id, password):
    """إنشاء الحساب وحفظ الإيميل في قاعدة البيانات بعد نجاح التحقق الثلاثي"""
    conn = sqlite3.connect('ministry_system.db')
    cursor = conn.cursor()
    try:
        hashed_pass = hashlib.sha256(str.encode(password)).hexdigest()
        cursor.execute('''
            INSERT INTO platform_user_accounts (email, national_id, password) 
            VALUES (?, ?, ?)
        ''', (email, national_id, hashed_pass))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def check_login(email, password):
    """التحقق من بيانات تسجيل الدخول ومطابقتها لجلب الاسم والكلية"""
    conn = sqlite3.connect('ministry_system.db')
    cursor = conn.cursor()
    hashed_pass = hashlib.sha256(str.encode(password)).hexdigest()
    cursor.execute('''
        SELECT omr.full_name, omr.faculty, omr.department 
        FROM platform_user_accounts pua
        JOIN official_ministry_records omr ON pua.national_id = omr.national_id
        WHERE pua.email = ? AND pua.password = ?
    ''', (email, hashed_pass))
    result = cursor.fetchone()
    conn.close()
    return result

# --- 2. بناء واجهات الويب الديناميكية (Streamlit) ---
st.set_page_config(page_title="بوابة الخدمات الطلابية الرقمية", page_icon="🎓")

# إدارة تنقل الصفحات عبر متغيرات الجلسة (Session State)
if 'page' not in st.session_state:
    st.session_state.page = 'login' # الصفحات المتاحة: login, signup, main_app
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

# --- الواجهة 1: تسجيل الدخول (Login) ---
if st.session_state.page == 'login':
    st.title("🎓 بوابة جامعة اللاذقية | تسجيل الدخول")
    st.subheader("كلية الهندسة المدنية - المنصة الرقمية")
    
    email = st.text_input("البريد الإلكتروني المعتمد:")
    password = st.text_input("كلمة المرور:", type="password")
    
    if st.button("تسجيل الدخول 🚪", use_container_width=True):
        user_data = check_login(email, password)
        if user_data:
            st.session_state.user_info['name'] = user_data[0]
            st.session_state.user_info['faculty'] = user_data[1]
            st.session_state.user_info['dept'] = user_data[2]
            st.session_state.page = 'main_app'
            st.rerun()
        else:
            st.error("❌ البريد الإلكتروني أو كلمة المرور غير صحيحة، أو الحساب لم يُنشأ بعد.")
            
    st.divider()
    if st.button("طالب جديد؟ إنشاء حساب موثق بالرقم الوطني 📝", use_container_width=True):
        st.session_state.page = 'signup'
        st.rerun()

# --- الواجهة 2: نموذج التسجيل المتقدم بالتحقق الثلاثي الصارم (Sign Up) ---
elif st.session_state.page == 'signup':
    st.title("📝 نموذج تسجيل حساب جامعي جديد")
    st.info("💡 أمن النظام: يجب أن تتطابق البيانات الثلاثية أدناه تماماً مع بياناتك المسجلة في سجلات الوزارة الرسمية.")
    
    student_name = st.text_input("الاسم الكامل (كما هو بالبطاقة الشخصية):")
    uni_id = st.text_input("الرقم الجامعي الرسمي:")
    nat_id = st.text_input("الرقم الوطني المكون من 11 رقماً:")
    student_email = st.text_input("أدخل بريدك الإلكتروني (لحفظه وإرسال المستجدات لاحقاً):")
    student_pass = st.text_input("اختر كلمة مرور قوية للموقع:", type="password")
    confirm_pass = st.text_input("تأكيد كلمة المرور:", type="password")
    
    if st.button("التحقق والمصادقة الرسمية 🚀", use_container_width=True):
        if student_pass != confirm_pass:
            st.error("❌ كلمات المرور غير متطابقة!")
        elif not (student_name and uni_id and nat_id and student_email and student_pass):
            st.warning("⚠️ يرجى ملء كافة الخانات المطلوبة مسبقاً.")
        elif not student_email.endswith("@gmail.com"): # حظر الإيميلات الوهمية وتأكيد الجيميل الحقيقي
            st.error("❌ عذراً، يجب استخدام بريد إلكتروني حقيقي وصحيح ينتهي بـ @gmail.com.")
        else:
            with st.spinner("جاري فحص وتدقيق البيانات في سجلات الوزارة..."):
                # 🔍 خطوة الأمان الثلاثية المباشرة من قاعدة البيانات
                college_info = check_triple_auth(nat_id, uni_id, student_name)
                
                if college_info:
                    # تفقد إن كان الإيميل مسجلاً من قبل طالب آخر
                    if check_email_exists(student_email):
                        st.error("❌ هذا البريد الإلكتروني مستخدم بالفعل في حساب آخر!")
                    else:
                        # إضافة الحساب بنجاح لجدول المنصة
                        if add_new_user(student_email, nat_id, student_pass):
                            st.success(f"🎉 ممتاز يا مهندس {student_name}! تم التحقق من هويتك رسميًا وإنشاء حسابك بنجاح.")
                            st.info("📨 تم تسجيل بريدك الإلكتروني في قاعدة البيانات لتلقي المستجدات الهندسية القادمة.")
                            st.session_state.page = 'login'
                            st.rerun()
                        else:
                            st.error("❌ هذا الرقم الوطني قام بإنشاء حساب مسبقاً!")
                else:
                    # رسالة الرفض الذكية والمحايدة
                    st.error("❌ عذراً، معلوماتك غير مطابقة لسجلات الكلية الرسمية. الرجاء التأكد من كتابة (الاسم، الرقم الجامعي، والرقم الوطني) بدقة وأعد المحاولة.")
                    
    if st.button("العودة لصفحة الدخول"):
        st.session_state.page = 'login'
        st.rerun()

# --- الواجهة 3: التطبيق الرئيسي والخدمات الطلابية الآمنة (Main App) ---
elif st.session_state.page == 'main_app':
    st.title(f"👷‍♂️ أهلاً بك يا مهندس: {st.session_state.user_info.get('name')}")
    st.subheader(f"📍 {st.session_state.user_info.get('faculty')} | {st.session_state.user_info.get('dept')}")
    st.balloons()
    
    st.success("🔒 تم توثيق الدخول بنجاح بناءً على هويتك الوطنية والجامعية المصرحة.")
    
    st.markdown("""
    ---
    ### 📂 لوحة التحكم والخدمات البرمجية المتاحة حالياً:
    مرحباً بك في فضائك الرقمي النظيف. المنصة الآن جاهزة ومؤمنة تماماً لاستقبال أول برنامج هندسي تقوم بتطويره لزملائك.
    """)
    
    if st.button("تسجيل الخروج الآمن 🚪", use_container_width=True):
        st.session_state.page = 'login'
        st.session_state.user_info = {}
        st.rerun()
