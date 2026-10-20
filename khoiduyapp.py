import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Anime Battle 3.0 - Bleach vs Naruto Style",
    page_icon="⚔️",
    layout="wide"
)

# Custom CSS cho giao diện Streamlit hiện đại
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0d0e15, #1a1c29, #26122b);
            color: #ffffff;
        }
        .main-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 900;
            background: -webkit-linear-gradient(45deg, #ff416c, #8a2be2, #00f2fe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .sub-desc {
            text-align: center;
            color: #a0aec0;
            font-size: 1rem;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">⚔️ ANIME BATTLE 3.0 ⚔️</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-desc">Game đối kháng 2D phong cách Bleach vs Naruto — Chế độ 2 Người chơi (P1 vs P2)</p>', unsafe_allow_html=True)

# Giao diện Sidebar hướng dẫn điều khiển
with st.sidebar:
    st.markdown("### 🎮 Bảng Điều Khiển Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🔴 PLAYER 1 (Soul Reaper)**")
        st.markdown("""
        * **A / D**: Di chuyển Trái / Phải
        * **W**: Nhảy lên
        * **J**: Tấn công thường (Combo)
        * **K**: Tuyệt kỹ Ultimate (Tốn 30 MP)
        * **L**: Tăng tốc / Lướt né
        """)
    
    with col2:
        st.markdown("**🔵 PLAYER 2 (Ninja Shinobi)**")
        st.markdown("""
        * **← / →**: Di chuyển Trái / Phải
        * **↑**: Nhảy lên
        * **Numpad 1**: Tấn công thường
        * **Numpad 2
