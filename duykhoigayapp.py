import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="HER TREES : PUZZLE DREAM (2D)",
    page_icon="🌳",
    layout="wide"
)

# Tối ưu giao diện Streamlit theo tone màu đen huyền bí
st.markdown("""
<style>
    .stApp { background-color: #080808; color: #ffffff; }
    header { visibility: hidden; }
    footer { visibility: hidden; }
    h1 { color: #ffffff !important; font-family: 'Courier New', Courier, monospace; text-align: center; margin-bottom: 5px; }
    p { text-align: center; color: #888888; font-family: 'Courier New', Courier, monospace; }
</style>
""", unsafe_allow_html=True)

st.title("🌳 HER TREES : PUZZLE DREAM (2D)")
st.markdown("Trò chơi giải đố Point & Click 2D đen-trắng. Nhấp chuột vào các vật thể để tìm manh mối và mở cửa giấc mơ.")

# Mã Game HTML5 Canvas 2D
game_2d_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body { background: #080808; color: #fff; font-family: 'Courier New', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }
        
        #game-wrapper { position: relative; width: 850px; height: 520px; border: 2px solid #fff; background: #000; box-shadow: 0 0 20px rgba(255,255,255,0.1); }
        canvas { display: block; cursor: pointer; }

        /* HUD Title */
        #hud-title {
            position: absolute; top: 15px; left: 20px;
            font-size: 14px; letter-spacing: 2px; font-weight: bold;
            background: rgba(0,0,0,0.8); padding: 5px 12px; border: 1px solid #fff;
        }

        /* Overlay Ghép mảnh giấy (Puzzle 1) */
        .overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.92); display: none; flex-direction: column;
            justify-content: center; align-items: center; z-index: 10;
        }

        .paper-board {
            position: relative; width: 320px; height: 320px; border: 2px dashed #fff;
            background: #111; margin: 15px 0;
        }

        .scrap {
            position: absolute; width: 90px; height: 90px; border: 2px solid #fff;
            background: #222; cursor: move; display: flex; flex-direction: column;
            justify-content: center; align-items: center; font-weight: bold; font-size: 20px; color: #fff;
        }

        /* Keypad Khóa cửa */
        .keypad-display {
            width: 180px; height: 40px; background: #000; border: 2px solid #fff;
            color: #fff; font-size: 22px; text-align: center; line-height: 40px;
            letter-spacing: 6px; margin-bottom: 15px; font-weight: bold;
        }
        .keypad-grid { display: grid; grid-template-columns: repeat(3, 55px); gap: 8px; }
        .key-btn {
            width: 55px; height: 55px; background: #111; border: 1px solid #fff;
            color: #fff; font-size: 18px; cursor: pointer; font-family: inherit;
        }
        .key-btn:hover { background: #fff; color: #000; }

        .btn-close {
            background: #fff; color: #000; border: none; padding: 6px 20px;
            font-family: inherit; font-weight: bold; cursor: pointer; text-transform: uppercase; margin-top: 10px;
        }
        .btn-close:hover { background: #ccc; }
    </style>
</head>
<body>

    <div id="game-wrapper">
        <div id="hud-title">DREAM 1: THE INK TREE</div>
        <canvas id="gameCanvas" width="850" height="520"></canvas>

        <!-- Modal Ghép Mảnh Giấy -->
        <div id="paper-modal" class="overlay">
            <div style="font-size:14px; letter-spacing:1px;">GẮP CÁC MẢNH GIẤY ĐỂ TÌM MẬT MÃ</div>
            <div class="paper-board" id="paper-board">
                <div class="scrap" id="scrap1" style="top:20px; left:20px;">●<br><span style="font-size:24px;">7</span></div>
                <div class="scrap" id="scrap2" style="top:180px; left:190px;">■<br><span style="font-size:24px;">4</span></div>
                <div class="scrap" id="scrap3" style="top:110px; left:40px;">▲<br><span style="font-size:24px;">9</span></div>
            </div>
            <button class="btn-close" onclick="closeOverlay('paper-modal')">ĐÓNG</button>
        </div>

        <!-- Modal Bảng Số Khóa Cửa -->
        <div id="keypad-modal" class="overlay">
            <div style="font-size:14px; letter-spacing:1px; margin-bottom:10px;">NHẬP MẬT MÃ MỞ CỬA</div>
            <div class="keypad-display" id="key-display">---</div>
            <div class="keypad-grid">
                <button class="key-btn" onclick="pressKey('1')">1</button>
                <button class="key-btn" onclick="pressKey('2')">2</button>
                <button class="key-btn" onclick="pressKey('3')">3</button>
                <button class="key-btn" onclick="pressKey('4')">4</button>
                <button class="key-btn" onclick="pressKey('5')">5</button>
                <button class="key-btn" onclick="pressKey('6')">6</button>
                <button class="key-btn" onclick="pressKey('7')">7</button>
                <button class="key-btn" onclick="pressKey('8')">8</button>
                <button class="key-btn" onclick="pressKey('9')">9</button>
                <button class="key-btn" onclick="pressKey('C')">C</button>
                <button class="key-btn" onclick="pressKey('0')">0</button>
                <button class="key-btn" onclick="submitKey()">OK</button>
            </div>
            <button class="btn-close" onclick="closeOverlay('keypad-modal')">ĐÓNG</button>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        let currentLevel = 1;
        let eyeOpen = false;

        // Vùng nhấp chuột (Hotspots) cho 2D Point & Click
        const hotspots = {
            1: [
                { id: 'paper', x: 120, y: 320, w: 140, h: 100 }, // Cái bàn chứa giấy
                { id: 'keypad', x: 680, y: 220, w: 60, h: 90 }   // Bảng nhập mã bên cạnh cửa
            ],
            2: [
                { id: 'cat_puzzle', x: 360, y: 200, w: 130, h: 160 }, // Đồng hồ mèo
                { id: 'keypad', x: 680, y: 220, w: 60, h: 90 }
            ],
            3: [
                { id: 'eye_tree', x: 350, y: 150, w: 150, h: 180 },  // Cây Mắt
                { id: 'keypad', x: 680, y: 220, w: 60, h: 90 }
            ]
        };

        // --- VẼ ĐỒ HỌA 2D THEO PHONG CÁCH HER TREES ---
        function renderScene() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#050505';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.strokeStyle = '#ffffff';
            ctx.fillStyle = '#ffffff';
            ctx.lineWidth = 2;

            // Sàn nhà và Đường tường
            ctx.beginPath();
            ctx.moveTo(0, 420); ctx.lineTo(850, 420);
            ctx.moveTo(150, 0); ctx.lineTo(150, 420);
            ctx.moveTo(700, 0); ctx.lineTo(700, 420);
            ctx.stroke();

            // Vẽ Cửa Giấc Mơ ở bên phải
            ctx.strokeRect(710, 160, 110, 260);
            ctx.strokeRect(680, 230, 20, 30); // Ô Keypad
            ctx.beginPath(); ctx.arc(725, 290, 5, 0, Math.PI*2); ctx.stroke(); // Tay cầm cửa

            if (currentLevel === 1) {
                drawDream1();
            } else if (currentLevel === 2) {
                drawDream2();
            } else if (currentLevel === 3) {
                drawDream3();
            }
        }

        // Màn 1: Cây mực & Bàn chứa mảnh giấy
        function drawDream1() {
            // Cây mực quái dị
            ctx.beginPath();
            ctx.moveTo(380, 420); ctx.lineTo(390, 220); ctx.lineTo(350, 160);
            ctx.moveTo(390, 260); ctx.lineTo(430, 180);
            ctx.moveTo(390, 310); ctx.lineTo(340, 270);
            ctx.stroke();

            // Các vòng tròn kỳ dị trên cây
            [ [350, 160], [430, 180], [340, 270], [390, 220] ].forEach(pt => {
                ctx.beginPath(); ctx.arc(pt[0], pt[1], 12, 0, Math.PI*2); ctx.stroke();
            });

            // Bàn đựng mảnh giấy (Bên trái)
            ctx.strokeRect(120, 340, 140, 80);
            ctx.fillRect(150, 325, 30, 15); // Tờ giấy màu trắng
        }

        // Màn 2: Mèo Kỳ Diệu & Hình Chiếu
        function drawDream2() {
            // Khối Mèo kỳ ảo trung tâm
            ctx.strokeRect(380, 240, 90, 180); // Bệ thờ
            
            // Đầu Mèo Hình Học
            ctx.beginPath();
            ctx.moveTo(400, 180); ctx.lineTo(425, 230); ctx.lineTo(450, 180); // Tai
            ctx.lineTo(440, 240); ctx.lineTo(410, 240); ctx.closePath();
            ctx.stroke();

            // Kim đồng hồ gợi ý số 3 - 1 - 8
            ctx.font = "16px Courier New";
            ctx.fillText("Ⅲ - Ⅰ - Ⅷ", 385, 160);
        }

        // Màn 3: Cây Mắt Surrealism
        function drawDream3() {
            // Thân cây lớn
            ctx.strokeRect(400, 260, 50, 160);

            // Con mắt khổng lồ
            ctx.beginPath();
            ctx.ellipse(425, 200, 50, 30, 0, 0, Math.PI * 2);
            ctx.stroke();

            if (eyeOpen) {
                // Tròng mắt mở ra hiện số 808
                ctx.beginPath(); ctx.arc(425, 200, 18, 0, Math.PI*2); ctx.fill();
                ctx.fillStyle = '#000';
                ctx.font = "bold 12px Courier New";
                ctx.fillText("808", 414, 204);
            } else {
                // Mắt nhắm
                ctx.beginPath();
                ctx.moveTo(375, 200); ctx.lineTo(475, 200);
                ctx.stroke();
            }
        }

        renderScene();

        // --- XỬ LÝ SỰ KIỆN CLICK CHUỘT (POINT & CLICK) ---
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            const currentHotspots = hotspots[currentLevel];
            currentHotspots.forEach(spot => {
                if (mouseX >= spot.x && mouseX <= spot.x + spot.w &&
                    mouseY >= spot.y && mouseY <= spot.y + spot.h) {
                    
                    if (spot.id === 'paper') {
                        document.getElementById('paper-modal').style.display = 'flex';
                    } else if (spot.id === 'keypad') {
                        document.getElementById('keypad-modal').style.display = 'flex';
                    } else if (spot.id === 'eye_tree') {
                        eyeOpen = !eyeOpen;
                        renderScene();
                    }
                }
            });
        });

        // --- KÉO THẢ MẢNH GIẤY (PUZZLE 1) ---
        let activeScrap = null;
        document.querySelectorAll('.scrap').forEach(scrap => {
            scrap.addEventListener('mousedown', () => { activeScrap = scrap; });
        });
        document.addEventListener('mousemove', (e) => {
            if (activeScrap) {
                const board = document.getElementById('paper-board').getBoundingClientRect();
                let x = e.clientX - board.left - 45;
                let y = e.clientY - board.top - 45;
                activeScrap.style.left = Math.max(0, Math.min(230, x)) + 'px';
                activeScrap.style.top = Math.max(0, Math.min(230, y)) + 'px';
            }
        });
        document.addEventListener('mouseup', () => { activeScrap = null; });

        // --- BẢNG PHÍM MẬT MÃ (KEYPAD LOGIC) ---
        let inputCode = "";
        const answers = { 1: "749", 2: "318", 3: "808" };

        function pressKey(val) {
            if (val === 'C') { inputCode = ""; }
            else if (inputCode.length < 3) { inputCode += val; }
            document.getElementById('key-display').innerText = inputCode || "---";
        }

        function submitKey() {
            if (inputCode === answers[currentLevel]) {
                alert("🎉 MẬT MÃ CHÍNH XÁC! CỬA GIẤC MƠ ĐÃ MỞ!");
                closeOverlay('keypad-modal');
                inputCode = "";
                document.getElementById('key-display').innerText = "---";
                nextDream();
            } else {
                alert("❌ SAI MẬT MÃ! Hãy tìm manh mối trong phòng.");
                inputCode = "";
                document.getElementById('key-display').innerText = "---";
            }
        }

        function closeOverlay(id) {
            document.getElementById(id).style.display = 'none';
        }

        function nextDream() {
            currentLevel++;
            if (currentLevel === 2) {
                document.getElementById('hud-title').innerText = "DREAM 2: THE CAT CONE";
            } else if (currentLevel === 3) {
                document.getElementById('hud-title').innerText = "DREAM 3: THE AWAKENING EYE";
            } else {
                alert("🌌 BẠN ĐÃ TỈNH GIẤC HOÀN TOÀN! CHÚC MỪNG BẠN ĐÃ TÌM THẤY LỐI THOÁT!");
                currentLevel = 1;
                document.getElementById('hud-title').innerText = "DREAM 1: THE INK TREE";
            }
            renderScene();
        }
    </script>
</body>
</html>
"""

# Render ứng dụng lên Streamlit
components.html(game_2d_html, height=560, scrolling=False)

# Mẹo giải đố
with st.expander("💡 Mẹo giải mật mã các màn chơi"):
    st.write("""
    * **Dream 1:** Bấm vào cái bàn bên trái để xếp mảnh giấy theo thứ tự hình (Tròn -> Vuông -> Tam giác). Mật mã là **749**.
    * **Dream 2:** Đọc các chữ số La Mã trên đầu con mèo. Mật mã là **318**.
    * **Dream 3:** Nhấp chuột trực tiếp vào con mắt khổng lồ giữa cây để mở mắt. Mật mã là **808**.
    """)
