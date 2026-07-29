import streamlit as st
import numpy as np
import plotly.graph_objects as go

# إعدادات الصفحة العامة للتطبيق
st.set_page_config(page_title="مستشار الهندسة المدنية الذكي", page_icon="🏗️", layout="wide")

# العنوان الرئيسي للتطبيق بتصميم جذاب
st.title("🏗️ تطبيق حساب ورسم مخططات الجوائز البيتونية والمعدنية")
st.markdown("""
### أهلاً بك يا مهندس المستقبل! 🚀
هذا التطبيق يقوم بحساب ردود الأفعال ورسم مخططات **عزوم الانعطاف (BMD)** و**قوى القص (SFD)** لجائز بسيط الاستناد خاضع لحمولة موزعة بانتظام.
""")

# تقسيم الشاشة إلى قسمين: قسم المدخلات وقسم النتائج
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📥 مدخلات الجائز (Beam Inputs)")
    
    # مدخلات المستخدم مع قيم افتراضية
    L = st.number_input("طول الجائز الكلي (L) بالمتر:", min_value=1.0, max_value=30.0, value=6.0, step=0.5)
    w = st.number_input("الحمولة الموزعة بانتظام (w) طن/متر:", min_value=0.0, max_value=100.0, value=2.5, step=0.1)
    
    st.divider()
    
    # العمليات الحسابية الهندسة المدنية
    # 1. حساب ردود الأفعال (R1 = R2 = w * L / 2)
    R1 = (w * L) / 2
    R2 = R1
    
    # 2. حساب العزم الأعظمي في المنتصف (M_max = w * L^2 / 8)
    M_max = (w * (L ** 2)) / 8
    
    # عرض النتائج الرقمية بشكل أنيق
    st.header("📊 النتائج الحسابية")
    st.metric(label="رد الفعل عند المسند الأيسر (R1)", value=f"{R1:.2f} Ton")
    st.metric(label="رد الفعل عند المسند الأيمن (R2)", value=f"{R2:.2f} Ton")
    st.metric(label="العزم الأعظمي في المنتصف (M_max)", value=f"{M_max:.2f} Ton.m")

with col2:
    st.header("📈 المخططات الهندسية التفاعلية")
    
    # توليد نقاط على طول الجائز للرسم (100 نقطة)
    x = np.linspace(0, L, 100)
    
    # معادلات القص والعزم عند كل نقطة x
    shear = R1 - (w * x)
    moment = (R1 * x) - (0.5 * w * (x ** 2))
    
    # ---- رسم مخطط قوى القص (SFD) ----
    fig_shear = go.Figure()
    fig_shear.add_trace(go.Scatter(x=x, y=shear, fill='tozeroy', line_color='red', name='قوة القص V'))
    fig_shear.update_layout(
        title="مخطط قوى القص (Shear Force Diagram - SFD)",
        xaxis_title="الطول (متر)",
        yaxis_title="القص (طن)",
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_shear, use_container_width=True)
    
    # ---- رسم مخطط عزوم الانعطاف (BMD) ----
    fig_moment = go.Figure()
    # هندسياً نفضل رسم العزم الموجب للأسفل في الهندسة المدنية
    fig_moment.add_trace(go.Scatter(x=x, y=moment, fill='tozeroy', line_color='green', name='العزم M'))
    fig_moment.update_layout(
        title="مخطط عزوم الانعطاف (Bending Moment Diagram - BMD)",
        xaxis_title="الطول (متر)",
        yaxis_title="العزم (طن.متر)",
        height=300,
        yaxis=dict(autorange="reverse"), # قلب المحور ليتناسب مع الرسم الهندسي لشد الألياف السفلية
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig_moment, use_container_width=True)

# تذييل الصفحة
st.markdown("---")
st.caption("تم التطوير بكل حماس لدعم طالب جامعة اللاذقية المميز في سنته الثالثة 🛠️👷‍♂️.")
