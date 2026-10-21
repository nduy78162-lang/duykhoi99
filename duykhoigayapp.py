import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="HER TREES : PUZZLE DREAM - Streamlit",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Thêm CSS để tối ưu giao diện Streamlit theo phong cách monochrome
st.markdown("""
<style>
    .main { background-color: #0d0d0d; color: #ffffff; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    h1, h2, h3 { color: #ffffff !important; font-family: 'Courier New', Courier, monospace; text-align: center; }
    p { text-align: center; color: #aaaaaa; font-family: 'Courier New', Courier, monospace; }
</style>
""", unsafe_allow_html=True)

st.title("🌳 HER TREES : PUZZLE DREAM")
st.markdown("Một tựa game giải đố trong giấc mơ đen-trắng surrealist. Hãy quan sát, tương tác và tìm mã số mật khẩu để mở cửa giấc mơ.")

# Mã HTML / JavaScript / WebGL Three.js cho game Her Trees
her_trees_game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body { background-color: #050505; color: #eee; font-family: 'Courier New', monospace; overflow: hidden; }
        
        #game-container { position: relative; width: 100vw; height: 100vh; display: flex; justify-content: center; align-items: center; }
        canvas { display: block; border: 2px solid #ffffff; }

        /* HUD & Overlay theo phong cách Her Trees (Đen & Trắng) */
        .ui-panel {
            position: absolute; top: 20px; left: 20px; color: #fff;
            background: rgba(0, 0, 0, 0.85); border: 1px solid #fff; padding: 12px 20px;
            font-size: 14px; letter-spacing: 1px; pointer-events: none; text-transform: uppercase;
        }

        /* Modal câu đố phòng 1 (Xếp mảnh giấy) */
        #puzzle-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.88); display: none; flex-direction: column;
            justify-content: center; align-items: center; z-index: 10;
        }

        .paper-board {
            position: relative; width: 340px; height: 340px; border: 2px dashed #fff;
            background: #111; margin-bottom: 20px;
        }

        .scrap {
            position: absolute; width: 100px; height: 100px; border: 2px solid #fff;
            background: rgba(255,255,255,0.15); cursor: move; display: flex;
            justify-content: center; align-items: center; font-weight: bold; font-size: 24px; color: #fff;
        }

        .close-btn {
            background: #fff; color: #000; border: none; padding: 8px 24px;
            font-family: inherit; font-weight: bold; cursor: pointer; text-transform: uppercase;
        }
        .close-btn:hover { background: #ccc; }

        /* Keypad khóa cửa */
        #keypad-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.9); display: none; flex-direction: column;
            justify-content: center; align-items: center; z-index: 10;
        }

        .keypad-display {
            width: 200px; height: 45px; background: #000; border: 2px solid #fff;
            color: #fff; font-size: 24px; text-align: center; line-height: 45px;
            letter-spacing: 6px; margin-bottom: 15px; font-weight: bold;
        }

        .keypad-grid { display: grid; grid-template-columns: repeat(3, 60px); gap: 10px; }
        .key-btn {
            width: 60px; height: 60px; background: #111; border: 1px solid #fff;
            color: #fff; font-size: 20px; cursor: pointer; font-family: inherit;
        }
        .key-btn:hover { background: #fff; color: #000; }

        #hint-text {
            position: absolute; bottom: 20px; color: #aaa; font-size: 13px; text-align: center; width: 100%;
        }
    </style>
</head>
<body>
    <div id="game-container">
        <div class="ui-panel">
            <span id="room-title">DREAM 1: TREE OF SCRAPS</span>
        </div>

        <!-- Canvas chứa 3D monochrome world -->
        <div id="canvas-holder"></div>

        <!-- Overlay ghép giấy (Phòng 1) -->
        <div id="puzzle-overlay">
            <h3 style="color:#fff; margin-bottom:15px;">KẾT HỢP CÁC MẢNH GIẤY ĐỂ TÌM MẬT MÃ</h3>
            <div class="paper-board" id="paper-board">
                <div class="scrap" id="scrap1" style="top:20px; left:20px;">▲<br>9</div>
                <div class="scrap" id="scrap2" style="top:180px; left:200px;">■<br>4</div>
                <div class="scrap" id="scrap3" style="top:120px; left:50px;">●<br>7</div>
            </div>
            <button class="close-btn" onclick="closePuzzle()">ĐÓNG</button>
        </div>

        <!-- Overlay Bảng mật mã (Keypad) -->
        <div id="keypad-overlay">
            <h3 style="color:#fff; margin-bottom:15px;">NHẬP MẬT MÃ MỞ CỬA</h3>
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
            <br>
            <button class="close-btn" onclick="closeKeypad()">ĐÓNG</button>
        </div>

        <div id="hint-text">Dùng chuột xoay quan sát không gian. Nhấp vào các vật thể để kiểm tra.</div>
    </div>

    <!-- Nạp thư viện Three.js & OrbitControls -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <script>
        // --- 1. KHỞI TẠO SCENE MONOCHROME ---
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x050505);
        scene.fog = new THREE.FogExp2(0x050505, 0.03);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 3, 9);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth * 0.9, 580);
        document.getElementById('canvas-holder').appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.maxPolarAngle = Math.PI / 2 + 0.1;

        // --- 2. VẬT LIỆU MỰC ĐEN TRẮNG (STYLIZED MONOCHROME) ---
        const whiteMat = new THREE.MeshBasicMaterial({ color: 0xffffff, wireframe: false });
        const blackMat = new THREE.MeshBasicMaterial({ color: 0x111111 });
        const lineMat = new THREE.LineBasicMaterial({ color: 0xffffff, linewidth: 2 });

        function createOutlineMesh(geometry) {
            const group = new THREE.Group();
            const mesh = new THREE.Mesh(geometry, blackMat);
            const edges = new THREE.EdgesGeometry(geometry);
            const line = new THREE.LineSegments(edges, lineMat);
            group.add(mesh);
            group.add(line);
            return group;
        }

        // --- 3. MÀN 1: CÂY GIẤC MƠ VÀ CỬA MẬT MÃ ---
        let currentLevel = 1;
        let roomGroup = new THREE.Group();
        scene.add(roomGroup);

        let interactables = [];

        function buildLevel1() {
            roomGroup.clear();
            interactables = [];
            document.getElementById('room-title').innerText = "DREAM 1: THE TREE OF SCRAPS";

            // Sàn nhà và tường đen trắng
            const floorGeo = new THREE.PlaneGeometry(16, 16);
            const floor = new THREE.Mesh(floorGeo, new THREE.MeshBasicMaterial({ color: 0x111111, side: THREE.DoubleSide }));
            floor.rotation.x = -Math.PI / 2;
            roomGroup.add(floor);

            // Cây Her Trees kỳ dị (Cây khô mực đen trắng)
            const trunk = createOutlineMesh(new THREE.CylinderGeometry(0.2, 0.5, 5, 8));
            trunk.position.set(-2, 2.5, -2);
            roomGroup.add(trunk);

            for(let i = 0; i < 5; i++) {
                const branch = createOutlineMesh(new THREE.BoxGeometry(0.1, 1.5, 0.1));
                branch.position.set(-2 + (Math.random()-0.5)*1.5, 3.5 + i*0.4, -2 + (Math.random()-0.5)*1.5);
                branch.rotation.z = (Math.random()-0.5);
                roomGroup.add(branch);
            }

            // Vật thể 1: Bàn chứa mảnh giấy
            const table = createOutlineMesh(new THREE.BoxGeometry(2, 1.2, 2));
            table.position.set(-2, 0.6, 1);
            table.name = "puzzle_paper";
            roomGroup.add(table);
            interactables.push(table);

            // Tờ giấy trên bàn
            const paper = new THREE.Mesh(new THREE.PlaneGeometry(0.6, 0.6), whiteMat);
            paper.rotation.x = -Math.PI/2;
            paper.position.set(-2, 1.21, 1);
            roomGroup.add(paper);

            // Cửa mật mã ở tường sau
            const doorFrame = createOutlineMesh(new THREE.BoxGeometry(2.5, 4.5, 0.2));
            doorFrame.position.set(2, 2.25, -4);
            roomGroup.add(doorFrame);

            const keypadPanel = createOutlineMesh(new THREE.BoxGeometry(0.6, 0.8, 0.2));
            keypadPanel.position.set(3.8, 2, -3.8);
            keypadPanel.name = "keypad";
            roomGroup.add(keypadPanel);
            interactables.push(keypadPanel);
        }

        buildLevel1();

        // --- 4. TƯƠNG TÁC CHUỘT (RAYCASTING) ---
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        window.addEventListener('pointerdown', (event) => {
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(interactables, true);

            if (intersects.length > 0) {
                let clickedObj = intersects[0].object;
                while (clickedObj.parent && clickedObj.parent !== roomGroup && !clickedObj.name) {
                    clickedObj = clickedObj.parent;
                }

                if (clickedObj.name === "puzzle_paper") {
                    document.getElementById('puzzle-overlay').style.display = "flex";
                } else if (clickedObj.name === "keypad") {
                    document.getElementById('keypad-overlay').style.display = "flex";
                }
            }
        });

        // Drag & Drop Mảnh giấy trong Modal Puzzle 1
        let activeScrap = null;
        let offsetX = 0, offsetY = 0;

        document.querySelectorAll('.scrap').forEach(scrap => {
            scrap.addEventListener('mousedown', (e) => {
                activeScrap = scrap;
                offsetX = e.clientX - scrap.offsetLeft;
                offsetY = e.clientY - scrap.offsetTop;
            });
        });

        document.addEventListener('mousemove', (e) => {
            if (activeScrap) {
                const board = document.getElementById('paper-board').getBoundingClientRect();
                let x = e.clientX - board.left - 50;
                let y = e.clientY - board.top - 50;
                activeScrap.style.left = Math.max(0, Math.min(240, x)) + 'px';
                activeScrap.style.top = Math.max(0, Math.min(240, y)) + 'px';
            }
        });

        document.addEventListener('mouseup', () => { activeScrap = null; });

        function closePuzzle() {
            document.getElementById('puzzle-overlay').style.display = "none";
        }

        // --- 5. HỆ THỐNG MẬT MÃ (KEYPAD LOGIC) ---
        let currentCode = "";
        const targetCodes = { 1: "749", 2: "318", 3: "808" }; // Mật mã tương ứng các màn

        function pressKey(val) {
            if (val === 'C') { currentCode = ""; } 
            else if (currentCode.length < 3) { currentCode += val; }
            document.getElementById('key-display').innerText = currentCode || "---";
        }

        function submitKey() {
            if (currentCode === targetCodes[currentLevel]) {
                alert("🎉 MẬT MÃ CHÍNH XÁC! CỬA GIẤC MƠ ĐÃ MỞ!");
                closeKeypad();
                nextLevel();
            } else {
                alert("❌ SAI MẬT MÃ! Hãy quan sát lại các manh mối.");
                currentCode = "";
                document.getElementById('key-display').innerText = "---";
            }
        }

        function closeKeypad() {
            document.getElementById('keypad-overlay').style.display = "none";
            currentCode = "";
            document.getElementById('key-display').innerText = "---";
        }

        // --- 6. CHUYỂN MÀN CHƠI (LEVEL PROGRESSION) ---
        function nextLevel() {
            currentLevel++;
            if (currentLevel === 2) {
                buildLevel2();
            } else if (currentLevel === 3) {
                buildLevel3();
            } else {
                alert("🌌 BẠN ĐÃ TỈNH GIẤC HOÀN TOÀN! CHÚC MỪNG BẠN ĐÃ HOÀN THÀNH HER TREES: PUZZLE DREAM!");
                location.reload();
            }
        }

        // Màn 2: Xếp khối hình nón con mèo (Cat Cones & Silhouette)
        function buildLevel2() {
            roomGroup.clear();
            interactables = [];
            document.getElementById('room-title').innerText = "DREAM 2: SILHOUETTE & CAT CONES";

            const floor = new THREE.Mesh(new THREE.PlaneGeometry(16, 16), new THREE.MeshBasicMaterial({ color: 0x111111 }));
            floor.rotation.x = -Math.PI / 2;
            roomGroup.add(floor);

            // Bệ thờ trung tâm
            const pedestal = createOutlineMesh(new THREE.CylinderGeometry(0.8, 1, 1.5, 6));
            pedestal.position.set(0, 0.75, 0);
            roomGroup.add(pedestal);

            // Khối nón con mèo kỳ dị xếp chồng (Mật mã gợi ý: 3 - 1 - 8)
            const cone1 = createOutlineMesh(new THREE.ConeGeometry(0.6, 1, 4));
            cone1.position.set(0, 2, 0);
            roomGroup.add(cone1);

            const cone2 = createOutlineMesh(new THREE.BoxGeometry(0.4, 0.4, 0.4));
            cone2.position.set(0, 2.7, 0);
            roomGroup.add(cone2);

            // Bảng gợi ý trên tường
            const hintBoard = createOutlineMesh(new THREE.PlaneGeometry(3, 2));
            hintBoard.position.set(0, 3, -4);
            roomGroup.add(hintBoard);

            // Bảng mật mã màn 2
            const keypadPanel = createOutlineMesh(new THREE.BoxGeometry(0.6, 0.8, 0.2));
            keypadPanel.position.set(3, 2, -3.8);
            keypadPanel.name = "keypad";
            roomGroup.add(keypadPanel);
            interactables.push(keypadPanel);
        }

        // Màn 3: Cây Mắt Surrealist (Eye Tree)
        function buildLevel3() {
            roomGroup.clear();
            interactables = [];
            document.getElementById('room-title').innerText = "DREAM 3: THE EYE OF AWAKENING";

            const floor = new THREE.Mesh(new THREE.PlaneGeometry(16, 16), new THREE.MeshBasicMaterial({ color: 0x080808 }));
            floor.rotation.x = -Math.PI / 2;
            roomGroup.add(floor);

            // Cây mắt lớn ở trung tâm
            const trunk = createOutlineMesh(new THREE.CylinderGeometry(0.4, 0.8, 6, 8));
            trunk.position.set(0, 3, -2);
            roomGroup.add(trunk);

            // Mắt ma mị đung đưa (Mật mã màn 3: 808)
            const eyeGeo = new THREE.SphereGeometry(1, 12, 12);
            const eye = createOutlineMesh(eyeGeo);
            eye.position.set(0, 4.5, -2);
            roomGroup.add(eye);

            // Keypad giấc mơ cuối cùng
            const keypadPanel = createOutlineMesh(new THREE.BoxGeometry(0.8, 1.2, 0.2));
            keypadPanel.position.set(0, 1.8, 2);
            keypadPanel.name = "keypad";
            roomGroup.add(keypadPanel);
            interactables.push(keypadPanel);
        }

        // --- 7. GAME LOOP & ANIMATIONS ---
        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            renderer.render(scene, camera);
        }
        animate();

        // Tự động điều chỉnh kích thước Canvas
        window.addEventListener('resize', () => {
            camera.aspect = (window.innerWidth * 0.9) / 580;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth * 0.9, 580);
        });
    </script>
</body>
</html>
"""

# Render ứng dụng lên Streamlit
components.html(her_trees_game_html, height=650, scrolling=False)

# Phần Hướng Dẫn & Mẹo Chơi
with st.expander("❓ Hướng dẫn giải đố (Gợi ý cho các Dream)"):
    st.write("""
    1. **Màn 1 (Dream 1 - Tree of Scraps):** 
       * Nhấp chuột vào chiếc bàn bên trái cây để mở bảng xếp mảnh giấy. 
       * Kéo các mảnh giấy xếp theo thứ tự biểu tượng (Tròn -> Vuông -> Tam giác) để tìm mã 3 chữ số: **749**.
       * Nhấp vào bảng điều khiển trên tường phải và nhập **749** để qua màn.
    2. **Màn 2 (Dream 2 - Cat Cones):** 
       * Mã mở cửa là **318**.
    3. **Màn 3 (Dream 3 - The Eye):** 
       * Mã thức tỉnh giấc mơ là **808**.
    """)
