import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="HER TREES : LOGIC PUZZLE",
    page_icon="🌳",
    layout="wide"
)

# Style giao diện Streamlit Monochrome
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #ffffff; }
    header, footer { visibility: hidden; }
    h1 { color: #ffffff !important; font-family: 'Courier New', monospace; text-align: center; }
    p { text-align: center; color: #aaaaaa; font-family: 'Courier New', monospace; }
</style>
""", unsafe_allow_html=True)

st.title("🌳 HER TREES : PUZZLE DREAM")
st.markdown("Quan sát các biểu tượng và sơ đồ trên tường để tìm ra quy luật logic mở cửa.")

# Mã Game HTML5 Canvas 2D với Quy luật logic
game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body { background: #050505; color: #fff; font-family: 'Courier New', monospace; display: flex; justify-content: center; align-items: center; height: 100vh; overflow: hidden; }
        
        #game-wrapper { position: relative; width: 850px; height: 520px; border: 2px solid #fff; background: #000; box-shadow: 0 0 25px rgba(255,255,255,0.15); }
        canvas { display: block; cursor: pointer; }

        #hud-title {
            position: absolute; top: 15px; left: 20px;
            font-size: 13px; letter-spacing: 2px; font-weight: bold;
            background: rgba(0,0,0,0.85); padding: 6px 14px; border: 1px solid #fff;
        }

        /* Overlay Ghép Mảnh Giấy */
        .overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.94); display: none; flex-direction: column;
            justify-content: center; align-items: center; z-index: 10;
        }

        .paper-board {
            position: relative; width: 380px; height: 260px; border: 2px solid #fff;
            background: #111; margin: 15px 0; display: flex; justify-content: space-around; align-items: center;
        }

        .slot {
            width: 100px; height: 120px; border: 2px dashed #555;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            color: #777; font-size: 12px; text-align: center;
        }

        .scrap {
            position: absolute; width: 90px; height: 100px; border: 2px solid #fff;
            background: #222; cursor: move; display: flex; flex-direction: column;
            justify-content: center; align-items: center; font-weight: bold; font-size: 22px; color: #fff;
        }

        /* Keypad Khóa Cửa */
        .keypad-display {
            width: 180px; height: 42px; background: #000; border: 2px solid #fff;
            color: #fff; font-size: 24px; text-align: center; line-height: 42px;
            letter-spacing: 8px; margin-bottom: 15px; font-weight: bold;
        }
        .keypad-grid { display: grid; grid-template-columns: repeat(3, 55px); gap: 8px; }
        .key-btn {
            width: 55px; height: 55px; background: #111; border: 1px solid #fff;
            color: #fff; font-size: 18px; cursor: pointer; font-family: inherit;
        }
        .key-btn:hover { background: #fff; color: #000; }

        .btn-close {
            background: #fff; color: #000; border: none; padding: 8px 24px;
            font-family: inherit; font-weight: bold; cursor: pointer; text-transform: uppercase; margin-top: 10px;
        }
        .btn-close:hover { background: #ccc; }
    </style>
</head>
<body>

    <div id="game-wrapper">
        <div id="hud-title">DREAM 1: QUY LUẬT SỐ GÓC</div>
        <canvas id="gameCanvas" width="850" height="520"></canvas>

        <!-- Modal Ghép Mảnh Giấy (Level 1) -->
        <div id="paper-modal" class="overlay">
            <div style="font-size:14px; letter-spacing:1px; text-align:center;">
                QUY LUẬT: SẮP XẾP MẢNH GIẤY THEO SỐ GÓC TĂNG DẦN
            </div>
            
            <div class="paper-board" id="paper-board">
                <div class="slot"><br>0 GÓC<br>(Hình tròn)</div>
                <div class="slot"><br>3 GÓC<br>(Tam giác)</div>
                <div class="slot"><br>4 GÓC<br>(Hình vuông)</div>

                <!-- Các mảnh giấy có thể kéo thả -->
                <div class="scrap" id="scrap1" style="top:140px; left:20px;">▲<br><span>9</span></div>
                <div class="scrap" id="scrap2" style="top:140px; left:145px;">●<br><span>7</span></div>
                <div class="scrap" id="scrap3" style="top:140px; left:270px;">■<br><span>4</span></div>
            </div>

            <button class="btn-close" onclick="closeOverlay('paper-modal')">ĐÓNG</button>
        </div>

        <!-- Modal Keypad Mật Mã -->
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

        const hotspots = {
            1: [
                { id: 'paper', x: 100, y: 320, w: 150, h: 100 },
                { id: 'keypad', x: 680, y: 220, w: 60, h: 90 }
            ],
            2: [
                { id: 'cat', x: 360, y: 180, w: 140, h: 200 },
                { id: 'keypad', x: 680, y: 220, w: 60, h: 90 }
            ],
            3: [
                { id: 'eye_tree', x: 350, y: 140, w: 150, h: 200 },
                { id: 'keypad', x: 680, y: 220, w: 60, h: 90 }
            ]
        };

        function renderScene() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#050505';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.strokeStyle = '#ffffff';
            ctx.fillStyle = '#ffffff';
            ctx.lineWidth = 2;

            // Đường phòng & Sàn
            ctx.beginPath();
            ctx.moveTo(0, 420); ctx.lineTo(850, 420);
            ctx.moveTo(150, 0); ctx.lineTo(150, 420);
            ctx.moveTo(700, 0); ctx.lineTo(700, 420);
            ctx.stroke();

            // Cửa mật mã
            ctx.strokeRect(710, 160, 110, 260);
            ctx.strokeRect(680, 230, 20, 30);
            ctx.beginPath(); ctx.arc(725, 290, 5, 0, Math.PI*2); ctx.stroke();

            if (currentLevel === 1) drawDream1();
            else if (currentLevel === 2) drawDream2();
            else if (currentLevel === 3) drawDream3();
        }

        // Màn 1: Sơ đồ gợi ý quy luật vẽ trực tiếp lên tường
        function drawDream1() {
            // Sơ đồ gợi ý quy luật góc trên tường
            ctx.font = "14px Courier New";
            ctx.fillText("QUY LUẬT TƯỜNG:", 220, 80);
            ctx.fillText("(0 góc) ➔ (3 góc) ➔ (4 góc)", 220, 110);

            // Cây góc cạnh
            ctx.beginPath();
            ctx.moveTo(420, 420); ctx.lineTo(420, 200);
            ctx.moveTo(420, 300); ctx.lineTo(360, 220);
            ctx.moveTo(420, 260); ctx.lineTo(470, 190);
            ctx.stroke();

            // Bàn chứa mảnh giấy
            ctx.strokeRect(100, 340, 150, 80);
            ctx.fillRect(140, 325, 35, 15);
            ctx.fillStyle = '#000';
            ctx.font = "10px Courier New";
            ctx.fillText("SCRAPS", 142, 336);
            ctx.fillStyle = '#fff';
        }

        // Màn 2: Tượng Mèo & Gợi ý đếm chi tiết [Tai - Mắt - Râu]
        function drawDream2() {
            // Sơ đồ gợi ý trên tường
            ctx.font = "14px Courier New";
            ctx.fillText("MẬT MÃ = [SỐ TAI] - [SỐ MẮT] - [SỐ RÂU]", 220, 80);

            // Bệ thờ Mèo
            ctx.strokeRect(380, 260, 90, 160);

            // Tượng Mèo Surrealism (2 Tai, 1 Mắt ở trán, 4 Sợi râu)
            ctx.beginPath();
            // Tai trái & phải (2 Tai)
            ctx.moveTo(390, 200); ctx.lineTo(410, 150); ctx.lineTo(420, 200);
            ctx.moveTo(430, 200); ctx.lineTo(440, 150); ctx.lineTo(460, 200);
            // Đầu
            ctx.strokeRect(390, 200, 70, 60);

            // 1 Con mắt ở trán
            ctx.beginPath(); ctx.arc(425, 220, 8, 0, Math.PI*2); ctx.stroke();
            ctx.beginPath(); ctx.arc(425, 220, 3, 0, Math.PI*2); ctx.fill();

            // 4 Sợi râu (2 bên trái, 2 bên phải)
            ctx.beginPath();
            ctx.moveTo(370, 235); ctx.lineTo(390, 238);
            ctx.moveTo(370, 248); ctx.lineTo(390, 248);
            ctx.moveTo(460, 238); ctx.lineTo(480, 235);
            ctx.moveTo(460, 248); ctx.lineTo(480, 248);
            ctx.stroke();
        }

        // Màn 3: Cây Mắt Thức Tỉnh (808)
        function drawDream3() {
            ctx.font = "14px Courier New";
            ctx.fillText("NHẤP VÀO CON MẮT ĐỂ THỨC TỈNH GIẤC MƠ", 240, 80);

            // Cây chính
            ctx.strokeRect(400, 260, 50, 160);

            // Cành trái & Cành phải chứa các điểm quả
            ctx.beginPath();
            ctx.moveTo(400, 300); ctx.lineTo(320, 240);
            ctx.moveTo(450, 300); ctx.lineTo(530, 240);
            ctx.stroke();

            // Con mắt khổng lồ ở trung tâm
            ctx.beginPath();
            ctx.ellipse(425, 200, 45, 25, 0, 0, Math.PI * 2);
            ctx.stroke();

            if (eyeOpen) {
                ctx.beginPath(); ctx.arc(425, 200, 15, 0, Math.PI*2); ctx.fill();
                ctx.fillStyle = '#000';
                ctx.font = "bold 11px Courier New";
                ctx.fillText("808", 416, 204);
                ctx.fillStyle = '#fff';
            } else {
                ctx.beginPath(); ctx.moveTo(380, 200); ctx.lineTo(470, 200); ctx.stroke();
            }
        }

        renderScene();

        // Xử lý click chuột
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            hotspots[currentLevel].forEach(spot => {
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

        // Kéo thả mảnh giấy
        let activeScrap = null;
        document.querySelectorAll('.scrap').forEach(scrap => {
            scrap.addEventListener('mousedown', () => { activeScrap = scrap; });
        });

        document.addEventListener('mousemove', (e) => {
            if (activeScrap) {
                const board = document.getElementById('paper-board').getBoundingClientRect();
                let x = e.clientX - board.left - 45;
                let y = e.clientY - board.top - 50;
                activeScrap.style.left = Math.max(0, Math.min(280, x)) + 'px';
                activeScrap.style.top = Math.max(0, Math.min(150, y)) + 'px';
            }
        });
        document.addEventListener('mouseup', () => { activeScrap = null; });

        // Logic Mật mã chuẩn xác theo quy luật từng màn
        let inputCode = "";
        const answers = { 
            1: "794", // 0 góc (7) -> 3 góc (9) -> 4 góc (4)
            2: "214", // 2 Tai - 1 Mắt - 4 Râu
            3: "808"  // Mắt thức tỉnh
        };

        function pressKey(val) {
            if (val === 'C') { inputCode = ""; }
            else if (inputCode.length < 3) { inputCode += val; }
            document.getElementById('key-display').innerText = inputCode || "---";
        }

        function submitKey() {
            if (inputCode === answers[currentLevel]) {
                alert("🎉 MẬT MÃ CHÍNH XÁC! CỬA ĐÃ MỞ!");
                closeOverlay('keypad-modal');
                inputCode = "";
                document.getElementById('key-display').innerText = "---";
                nextDream();
            } else {
                alert("❌ SAI MẬT MÃ! Hãy suy luận từ quy luật ghi trên tường.");
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
                document.getElementById('hud-title').innerText = "DREAM 2: QUY LUẬT TƯỢNG MÈO";
            } else if (currentLevel === 3) {
                document.getElementById('hud-title').innerText = "DREAM 3: CÂY MẮT THỨC TỈNH";
            } else {
                alert("🌌 BẠN ĐÃ TỈNH GIẤC VÀ THOÁT KHỎI GIẤC MƠ!");
                currentLevel = 1;
                document.getElementById('hud-title').innerText = "DREAM 1: QUY LUẬT SỐ GÓC";
            }
            renderScene();
        }
    </script>
</body>
</html>
"""

components.html(game_html, height=560, scrolling=False)
