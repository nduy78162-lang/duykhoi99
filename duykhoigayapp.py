import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Plants vs Zombies 2D - Streamlit Edition",
    page_icon="🌻",
    layout="wide"
)

# Custom CSS giao diện Streamlit
st.markdown("""
<style>
    .stApp { background-color: #1a2a1a; color: #ffffff; }
    header, footer { visibility: hidden; }
    h1 { color: #55ff55 !important; font-family: 'Trebuchet MS', sans-serif; text-align: center; margin-bottom: 5px; text-shadow: 2px 2px #000; }
    p { text-align: center; color: #cccccc; font-family: sans-serif; }
</style>
""", unsafe_allow_html=True)

st.title("🌻 PLANTS VS. ZOMBIES 2D 🧟")
st.markdown("Chọn cây từ thanh công cụ bên trên, sau đó nhấp vào ô trống trên bãi cỏ để trồng. Nhấp vào **Mặt trời ☀️** để thu thập!")

# HTML & JavaScript Game Engine 2D
pvz_game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body { background: #0e170e; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; }
        
        #game-container {
            position: relative;
            width: 880px;
            height: 520px;
            border: 4px solid #3d2514;
            border-radius: 8px;
            box-shadow: 0 0 30px rgba(0,0,0,0.8);
            background: #111;
        }
        
        canvas { display: block; cursor: pointer; }
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="pvzCanvas" width="880" height="520"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('pvzCanvas');
        const ctx = canvas.getContext('2d');

        // --- CẤU HÌNH BÀN CHƠI (5 HÀNG x 8 CỘT) ---
        const ROWS = 5;
        const COLS = 8;
        const CELL_W = 80;
        const CELL_H = 80;
        const OFFSET_X = 140; // Khoảng cách lề trái cho Lawn Mower & Nhà
        const OFFSET_Y = 80;  // Khoảng cách lề trên cho Thanh UI

        // Trạng thái Game
        let suns = 150;
        let score = 0;
        let gameOver = false;
        let selectedPlant = null; // 'sunflower', 'peashooter', 'wallnut', 'cherry'

        // Thẻ cây & Giá tiền
        const PLANT_CARDS = [
            { id: 'sunflower', name: '🌻 Sunflower', cost: 50, icon: '🌻' },
            { id: 'peashooter', name: '🫛 Peashooter', cost: 100, icon: '🫛' },
            { id: 'wallnut', name: '🧱 Wall-nut', cost: 50, icon: '🧱' },
            { id: 'cherry', name: '🍒 Cherry Bomb', cost: 150, icon: '🍒' }
        ];

        // Lưới ô cờ
        let grid = [];
        for (let r = 0; r < ROWS; r++) {
            grid[r] = [];
            for (let c = 0; c < COLS; c++) {
                grid[r][c] = null; // Không có cây
            }
        }

        // Danh sách đối tượng
        let lawnMowers = [];
        for (let r = 0; r < ROWS; r++) {
            lawnMowers.push({ row: r, x: OFFSET_X - 45, y: OFFSET_Y + r * CELL_H + 20, active: false, used: false });
        }

        let plants = [];
        let zombies = [];
        let peas = [];
        let fallingSuns = [];
        let explosions = [];

        // --- ÂM THANH HIỆU ỨNG (Web Audio Synth) ---
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playSound(type) {
            try {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain);
                gain.connect(audioCtx.destination);

                if (type === 'pop') {
                    osc.frequency.setValueAtTime(400, audioCtx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(800, audioCtx.currentTime + 0.1);
                    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
                    osc.start(); osc.stop(audioCtx.currentTime + 0.1);
                } else if (type === 'shoot') {
                    osc.frequency.setValueAtTime(300, audioCtx.currentTime);
                    osc.frequency.linearRampToValueAtTime(150, audioCtx.currentTime + 0.08);
                    gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);
                    osc.start(); osc.stop(audioCtx.currentTime + 0.08);
                } else if (type === 'boom') {
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(120, audioCtx.currentTime
