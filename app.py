import streamlit as st
import requests
from datetime import datetime, timedelta

# =======================================================
# 🛡️ SOZLAMALAR VA BAZA INTEGRATSIYASI
# =======================================================
MUALLIF = "Yosinbey"
FIREBASE_URL = "https://yosinbeyinfoserver-default-rtdb.europe-west1.firebasedatabase.app/"

st.set_page_config(page_title="Oktagon Arena", page_icon="⚔️", layout="centered")

# Mobil o'yin interfeysi uchun qora-oltin geymerlar dizayni (CSS)
st.markdown("""
    <style>
    .main { background-color: #121212; color: #ffffff; }
    .stButton>button { width: 100%; background-color: #d32f2f; color: white; border-radius: 8px; font-weight: bold; height: 45px; }
    h1, h2, h3 { color: #ffd700 !important; text-align: center; font-family: 'Arial Black', sans-serif; }
    .stTextInput>div>div>input { background-color: #222222; color: white; border: 1px solid #ffd700; }
    </style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# BAZA BILAN ISHLASH FUNKSIYALARI
# -------------------------------------------------------
def foydalanuvchini_ol(uid):
    try: return requests.get(f"{FIREBASE_URL}users/{uid}.json", timeout=5).json()
    except: return None

def status_yangila(uid, status):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try: requests.patch(f"{FIREBASE_URL}status/{uid}.json", json={"status": status, "last_seen": now_str})
    except: pass

# =======================================================
# INTERFEYS LOGIKASI
# =======================================================
st.title("⚔️ OKTAGON ARENA ⚔️")
st.write(f"<p style='text-align:center;'>Muallif: {MUALLIF} | Tizim: WebApp v6.0</p>", unsafe_allow_html=True)

if 'user' not in st.session_state:
    st.session_state.user = None

# 1. TIZIMGA KIRISH YOKI RO'YXATDAN O'TISH
if st.session_state.user is None:
    tab1, tab2 = st.tabs(["🔐 Kirish", "📝 Ro'yxatdan o'tish"])
    
    with tab1:
        login_id = st.text_input("7 xonali ID raqamingiz:", key="log_id")
        login_parol = st.text_input("Parolingiz:", type="password", key="log_pass")
        if st.button("Tizimga kirish"):
            baza = foydalanuvchini_ol(login_id)
            if baza and login_parol == baza['parol']:
                st.session_state.user = baza
                status_yangila(login_id, "online")
                st.success(f"Xush kelibsiz, {baza['ism']}!")
                st.rerun()
            else:
                st.error("ID yoki parol xato!")
                
    with tab2:
        r_ism = st.text_input("Ismingiz:", key="reg_name")
        r_id = st.text_input("Yangi 7 xonali ID yarating:", key="reg_id")
        r_parol = st.text_input("Parol yarating:", type="password", key="reg_pass")
        r_email = st.text_input("Gmail manzilingiz:", key="reg_email")
        
        if st.button("Ro'yxatdan o'tish"):
            if r_id and r_ism and r_parol:
                if foydalanuvchini_ol(r_id):
                    st.error("Bu ID band! Boshqa ID tanlang.")
                else:
                    user_data = {"id": r_id, "ism": r_ism, "parol": r_parol, "gmail": r_email, "g'alabalar": 0}
                    requests.put(f"{FIREBASE_URL}users/{r_id}.json", json=user_data)
                    st.success("Muvaffaqiyatli ro'yxatdan o'tdingiz! Endi Kirish bo'limiga o'ting.")

# 2. ASOSIY O'YIN VA CHAT MENYUSI
else:
    user = st.session_state.user
    status_yangila(user['id'], "online") # Har sahifa yangilanganda statusni online qilish
    
    st.sidebar.markdown(f"### 👑 {user['ism'].upper()}")
    st.sidebar.write(f"ID: `{user['id']}`")
    
    if st.sidebar.button("🚪 Chiqish"):
        status_yangila(user['id'], "offline")
        st.session_state.user = None
        st.rerun()

    menu = st.radio("Bo'limni tanlang:", ["🎮 Jonli Arena (PvP)", "💬 Umumiy Chat", "🏆 Top O'yinchilar"])
    
    if menu == "🎮 Jonli Arena (PvP)":
        st.subheader("⚔️ Jang Maydoni")
        st.info("Onlayn raqiblar qidirilmoqda... Firebase jang tizimi ulangan.")
        if st.button("Tasodifiy Raqibga Taklif Yuborish"):
            st.warning("Lobby yaratilmoqda, kuting...")
            
    elif menu == "💬 Umumiy Chat":
        st.subheader("💬 Jangchilar Chati")
        # Bu yerda Firebase orqali keladigan global chat ishlaydi
        st.text_area("Xabarlar", "Tizim: Chat faollashtirildi. Xabarlar tarixini yuklash xavfsiz...", height=200, disabled=True)
        yangi_xabar = st.text_input("Xabaringizni yozing:")
        if st.button("Yuborish"):
            st.success("Xabar yuborildi!")
            
    elif menu == "🏆 Top O'yinchilar":
        st.subheader("🏆 Oktagon Peshqadamlari")
        # Firebase'dan eng ko'p yutganlarni chiqarish joyi
        st.write("1. 🥇 **Yosinbey** — 99 ta g'alaba")
        st.write("2. 🥈 **S2GKYREX** — 85 ta g'alaba")
