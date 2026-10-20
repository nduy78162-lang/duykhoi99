import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="3D Escape Room - Game Trí Tuệ",
    page_icon="🚪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ẩn các thành phần thừa của Streamlit
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container { padding: 0rem !important; }
    </style>
""", unsafe_allow_html=True)

html_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>3D Escape Room</title>
    <style>
        body { margin: 0; overflow: hidden; background-color: #0d0d11; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; user-select: none; }
        
        /* ---------------- GIAO DIỆN BẮT ĐẦU (MAIN MENU) ---------------- */
        #main-menu {
            position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;
            background: radial-gradient(circle, rgba(26,26,41,0.85) 0%, rgba(10,10,15,0.98) 100%);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            z-index: 100; backdrop-filter: blur(8px); transition: opacity 0.5s ease;
        }
        
        .game-title {
            font-size: 56px; font-weight: 900; color: #4cd137;
            text-transform: uppercase; letter-spacing: 6px;
            text-shadow: 0 0 20px rgba(76, 209, 55, 0.6), 0 0 40px rgba(76, 209, 55, 0.2);
            margin-bottom: 10px; animation: pulse 2s infinite alternate;
        }
        
        .game-subtitle {
            font-size: 18px; color: #a4b0be; margin-bottom: 40px; letter-spacing: 2px;
        }

        .menu-btn-container {
            display: flex; flex-direction: column; gap: 18px; width: 280px;
        }

        .menu-btn {
            padding: 15px 25px; font-size: 18px; font-weight: bold;
            color: #ffffff; background: rgba(255, 255, 255, 0.05);
            border: 2px solid #4cd137; border-radius: 8px; cursor: pointer;
            transition: all 0.3s ease; text-transform: uppercase; letter-spacing: 1px;
            box-shadow: 0 0 10px rgba(76, 209, 55, 0.1);
        }

        .menu-btn:hover {
            background: #4cd137; color: #000000;
            box-shadow: 0 0 25px rgba(76, 209, 55, 0.8); transform: translateY(-2px);
        }

        /* ---------------- POPUP MODALS (HƯỚNG DẪN / CHỌN MÀN) ---------------- */
        .modal-overlay {
            position: absolute; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0, 0, 0, 0.85); display: none; justify-content: center;
            align-items: center; z-index: 101; backdrop-filter: blur(5px);
        }

        .modal-card {
            background: #1e1e2e; border: 2px solid #4cd137; border-radius: 12px;
            padding: 30px; width: 500px; max-width: 90%; color: #fff;
            box-shadow: 0 0 30px rgba(0, 0, 0, 0.8); text-align: center;
        }

        .modal-card h2 { color: #4cd137; margin-top: 0; font-size: 28px; }

        .level-grid {
            display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; margin: 20px 0;
        }

        .level-btn {
            padding: 15px 0; font-size: 18px; font-weight: bold;
            background: #2f3542; color: #fff; border: 1px solid #747d8c;
            border-radius: 6px; cursor: pointer; transition: 0.2s;
        }

        .level-btn:hover { background: #4cd137; color: #000; border-color: #4cd137; }

        .close-btn {
            background: #e84118; color: white; border: none; padding: 10px 20px;
            border-radius: 6px; cursor: pointer; font-size: 16px; margin-top: 15px;
        }

        /* ---------------- GAME IN-PLAY UI ---------------- */
        #blocker {
            position: absolute; width: 100%; height: 100%; background: rgba(0,0,0,0.7);
            display: none; flex-direction: column; justify-content: center;
            align-items: center; color: white; z-index: 50;
        }
        #instructions-click {
            font-size: 22px; text-align: center; cursor: pointer; padding: 25px 40px;
            background: rgba(255,255,255,0.05); border-radius: 10px; border: 2px solid #4cd137;
            box-shadow: 0 0 20px rgba(76, 209, 55, 0.3);
        }

        #crosshair { position: absolute; top: 50%; left: 50%; width: 8px; height: 8px; background: #fff; border-radius: 50%; transform: translate(-50%, -50%); pointer-events: none; z-index: 10; }
        
        #hud {
            position: absolute; top: 20px; left: 20px; color: #4cd137; font-size: 16px;
            pointer-events: none; z-index: 10; background: rgba(0,0,0,0.65);
            padding: 15px; border-radius: 8px; border: 1px solid rgba(76, 209, 55, 0.3);
        }

        .menu-hud-btn {
            pointer-events: auto; margin-top: 10px; background: rgba(255,255,255,0.1);
            color: #fff; border: 1px solid #aaa; padding: 5px 10px; border-radius: 4px; cursor: pointer;
        }
        .menu-hud-btn:hover { background: #e84118; border-color: #e84118; }

        #toast { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.85); color: #fbc531; padding: 10px 25px; font-size: 18px; border-radius: 20px; border: 1px solid #fbc531; display: none; z-index: 10; }

        /* Keypad UI Modal */
        #keypad-modal { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #1a1a1a; padding: 20px; border-radius: 10px; border: 2px solid #4cd137; display: none; z-index: 80; text-align: center; }
        #keypad-display { background: #000; color: #4cd137; font-size: 30px; margin-bottom: 15px; padding: 10px; letter-spacing: 5px; border-radius: 5px; font-family: monospace; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .btn { padding: 15px; font-size: 20px; background: #333; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #555; }
        .btn-ok { background: #27ae60; } .btn-clear { background: #c0392b; }

        @keyframes pulse {
            0% { transform: scale(1); text-shadow: 0 0 20px rgba(76, 209, 55, 0.6); }
            100% { transform: scale(1.03); text-shadow: 0 0 35px rgba(76, 209, 55, 0.9); }
        }
    </style>
</head>
<body>

    <!-- 1. GIAO DIỆN BẮT ĐẦU (MAIN MENU) -->
    <div id="main-menu">
        <div class="game-title">ESCAPE ROOM 3D</div>
        <div class="game-subtitle">THÁCH THỨC TRÍ TUỆ & KHẢ NĂNG THOÁT HẠI</div>
        <div class="menu-btn-container">
            <button class="menu-btn" onclick="startNewGame()">▶ Bắt đầu chơi</button>
            <button class="menu-btn" onclick="openModal('level-modal')">🚪 Chọn màn chơi</button>
            <button class="menu-btn" onclick="openModal('guide-modal')">📖 Hướng dẫn</button>
        </div>
    </div>

    <!-- 2. POPUP CHỌN MÀN CHƠI -->
    <div id="level-modal" class="modal-overlay">
        <div class="modal-card">
            <h2>CHỌN MÀN CHƠI (1 - 10)</h2>
            <div class="level-grid">
                <button class="level-btn" onclick="selectLevel(1)">1</button>
                <button class="level-btn" onclick="selectLevel(2)">2</button>
                <button class="level-btn" onclick="selectLevel(3)">3</button>
                <button class="level-btn" onclick="selectLevel(4)">4</button>
                <button class="level-btn" onclick="selectLevel(5)">5</button>
                <button class="level-btn" onclick="selectLevel(6)">6</button>
                <button class="level-btn" onclick="selectLevel(7)">7</button>
                <button class="level-btn" onclick="selectLevel(8)">8</button>
                <button class="level-btn" onclick="selectLevel(9)">9</button>
                <button class="level-btn" onclick="selectLevel(10)">10</button>
            </div>
            <button class="close-btn" onclick="closeModal('level-modal')">Đóng</button>
        </div>
    </div>

    <!-- 3. POPUP HƯỚNG DẪN CHƠI -->
    <div id="guide-modal" class="modal-overlay">
        <div class="modal-card">
            <h2>HƯỚNG DẪN ĐIỀU KHIỂN</h2>
            <div style="text-align: left; line-height: 1.8; margin: 20px 0; font-size: 16px;">
                • <b>W, A, S, D</b>: Di chuyển nhân vật<br/>
                • <b>Di chuyển chuột</b>: Xoay góc nhìn 360°<br/>
                • <b>Phím Space</b>: Nhảy lên bục<br/>
                • <b>Click Chuột Trái (hoặc phím E)</b>: Tương tác / Nhặt đồ / Mở cửa / Gạt cần<br/>
                • <b>Đẩy vật thể</b>: Đi thẳng vào hộp/khối đá vật lý để đẩy
            </div>
            <button class="close-btn" onclick="closeModal('guide-modal')">Đã hiểu</button>
        </div>
    </div>

    <!-- 4. KHU VỰC GAME & HUD -->
    <div id="blocker">
        <div id="instructions-click">
            <b>SẴN SÀNG CHƠI</b><br/><br/>
            Click chuột vào đây để điều khiển góc nhìn!
        </div>
    </div>
    
    <div id="crosshair"></div>
    
    <div id="hud">
        <div id="level-text">Màn: 1</div>
        <div id="hint-text" style="max-width: 300px; margin: 5px 0;">Gợi ý: Tìm chìa khóa trên bàn.</div>
        <div id="inventory-text">Túi đồ: Trống</div>
        <button class="menu-hud-btn" onclick="returnToMainMenu()">☰ Menu Chính</button>
    </div>
    
    <div id="toast"></div>

    <!-- Keypad Modal -->
    <div id="keypad-modal">
        <div id="keypad-display">----</div>
        <div class="grid">
            <button class="btn" onclick="press('1')">1</button> <button class="btn" onclick="press('2')">2</button> <button class="btn" onclick="press('3')">3</button>
            <button class="btn" onclick="press('4')">4</button> <button class="btn" onclick="press('5')">5</button> <button class="btn" onclick="press('6')">6</button>
            <button class="btn" onclick="press('7')">7</button> <button class="btn" onclick="press('8')">8</button> <button class="btn" onclick="press('9')">9</button>
            <button class="btn btn-clear" onclick="press('C')">C</button> <button class="btn" onclick="press('0')">0</button> <button class="btn btn-ok" onclick="press('OK')">OK</button>
        </div>
    </div>

    <!-- Library Scripts -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cannon.js/0.6.2/cannon.min.js"></script>

    <script>
        let camera, scene, renderer, controls, world;
        let playerBody;
        let time = Date.now();
        
        let objectsToUpdate = [];
        let interactiveObjects = [];
        
        let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false, canJump = false;
        let currentLevel = 1;
        let hasKey = false;
        let doorMesh = null;
        let doorOpen = false;
        
        let keypadTarget = "";
        let keypadInput = "";
        let leverSequence = [];
        let pillarSequence = 1;

        const levels = [
            { id: 1, hint: "Nhặt chìa khóa trên bàn (Click trái) và chạm cửa để mở." },
            { id: 2, hint: "Đẩy khối hộp vật lý màu xanh đè lên công tắc màu đỏ trên sàn." },
            { id: 3, hint: "Nhìn mã số trên tường và nhập vào bảng điều khiển (Bên phải)." },
            { id: 4, hint: "Nhảy qua bục vật lý (Space) để lấy chìa khóa." },
            { id: 5, hint: "Kéo 3 cần gạt theo thứ tự: Trái, Phải, Giữa." },
            { id: 6, hint: "Phòng tối. Tìm đuốc phát sáng để thấy đường và chìa khóa." },
            { id: 7, hint: "Xếp khối hộp đè lên nhau để leo lên bục lấy chìa khóa." },
            { id: 8, hint: "Chạm 4 cột đá theo thứ tự từ Thấp đến Cao." },
            { id: 9, hint: "Giải toán đố: Xanh (2) + Đỏ (5) + Vàng (1) = ? Nhập mã." },
            { id: 10, hint: "Màn cuối: Đẩy hộp vào nút, gạt cần, nhập mã 2026." }
        ];

        init();
        animate();

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x0d0d11);
            scene.fog = new THREE.Fog(0x0d0d11, 0, 25);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

            const ambient = new THREE.AmbientLight(0xffffff, 0.8);
            scene.add(ambient);
            const light = new THREE.PointLight(0xffffff, 1, 30);
            light.position.set(0, 6, 0);
            scene.add(light);

            // Physics World
            world = new CANNON.World();
            world.gravity.set(0, -20, 0);
            world.broadphase = new CANNON.NaiveBroadphase();

            // Player Physics
            const playerShape = new CANNON.Sphere(1.5);
            playerBody = new CANNON.Body({ mass: 5 });
            playerBody.addShape(playerShape);
            playerBody.position.set(0, 5, 5);
            playerBody.linearDamping = 0.9;
            world.addBody(playerBody);

            // Floor Physics
            const groundBody = new CANNON.Body({ mass: 0, shape: new CANNON.Plane() });
            groundBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1,0,0), -Math.PI/2);
            world.addBody(groundBody);

            // Floor Mesh
            const floorMesh = new THREE.Mesh(new THREE.PlaneGeometry(50, 50), new THREE.MeshStandardMaterial({ color: 0x22222a }));
            floorMesh.rotation.x = -Math.PI / 2;
            scene.add(floorMesh);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // Controls
            controls = new THREE.PointerLockControls(camera, document.body);
            const blocker = document.getElementById('blocker');
            const instructions = document.getElementById('instructions-click');

            instructions.addEventListener('click', function () { controls.lock(); });
            controls.addEventListener('lock', function () { blocker.style.display = 'none'; });
            controls.addEventListener('unlock', function () {
                if(document.getElementById('main-menu').style.display === 'none' &&
                   document.getElementById('keypad-modal').style.display === 'none') {
                    blocker.style.display = 'flex';
                }
            });
            scene.add(controls.getObject());

            document.addEventListener('keydown', onKeyDown);
            document.addEventListener('keyup', onKeyUp);
            document.addEventListener('mousedown', onMouseClick);
            window.addEventListener('resize', onWindowResize);

            loadLevel(currentLevel);
        }

        /* ---------------- QUẢN LÝ GIAO DIỆN MENU ---------------- */
        function startNewGame() {
            document.getElementById('main-menu').style.opacity = '0';
            setTimeout(() => {
                document.getElementById('main-menu').style.display = 'none';
                document.getElementById('blocker').style.display = 'flex';
            }, 500);
        }

        function returnToMainMenu() {
            controls.unlock();
            document.getElementById('blocker').style.display = 'none';
            document.getElementById('main-menu').style.display = 'flex';
            document.getElementById('main-menu').style.opacity = '1';
        }

        function openModal(id) { document.getElementById(id).style.display = 'flex'; }
        function closeModal(id) { document.getElementById(id).style.display = 'none'; }

        function selectLevel(lvl) {
            currentLevel = lvl;
            loadLevel(currentLevel);
            closeModal('level-modal');
            startNewGame();
        }

        /* ---------------- GAMEPLAY CONTROLS ---------------- */
        function onKeyDown(event) {
            switch (event.code) {
                case 'KeyW': moveForward = true; break;
                case 'KeyA': moveLeft = true; break;
                case 'KeyS': moveBackward = true; break;
                case 'KeyD': moveRight = true; break;
                case 'Space': if (canJump) { playerBody.velocity.y = 12; canJump = false; } break;
                case 'KeyE': onMouseClick(); break;
            }
        }

        function onKeyUp(event) {
            switch (event.code) {
                case 'KeyW': moveForward = false; break;
                case 'KeyA': moveLeft = false; break;
                case 'KeyS': moveBackward = false; break;
                case 'KeyD': moveRight = false; break;
            }
        }

        playerBody.addEventListener("collide", function(e){
            if(e.contact.ni.y > 0.5) canJump = true;
        });

        function onMouseClick() {
            if (!controls.isLocked) return;
            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
            const intersects = raycaster.intersectObjects(interactiveObjects, false);

            if (intersects.length > 0) {
                const object = intersects[0].object;
                if (intersects[0].distance > 4.5) { showToast("Đến gần hơn để tương tác!"); return; }
                handleInteraction(object);
            }
        }

        function handleInteraction(obj) {
            const name = obj.name;
            if (name === "key") {
                hasKey = true; updateHUD(); scene.remove(obj); showToast("Đã nhặt Chìa Khóa!");
            } else if (name === "door") {
                if (doorOpen) return;
                let canOpen = false;
                if ([1, 4, 6, 7].includes(currentLevel) && hasKey) canOpen = true;
                if (canOpen) openDoor();
                else showToast("Cửa đã khóa! Hãy tìm cách giải đố.");
            } else if (name === "keypad") {
                document.exitPointerLock();
                document.getElementById('keypad-modal').style.display = 'block';
                keypadInput = ""; document.getElementById('keypad-display').innerText = "----";
            } else if (name.startsWith("lever_")) {
                obj.rotation.x = Math.PI / 4; leverSequence.push(name); checkLeverLogic();
            } else if (name === "torch") {
                scene.fog.far = 50; scene.add(new THREE.AmbientLight(0xffffff, 1.5));
                scene.remove(obj); showToast("Đã lấy đuốc thắp sáng!");
            } else if (name.startsWith("pillar_")) {
                let id = parseInt(name.split("_")[1]);
                if (id === pillarSequence) {
                    pillarSequence++; obj.material.color.setHex(0x4cd137); showToast(`Chạm đúng trụ ${id}!`);
                    if (pillarSequence > 4) { hasKey = true; openDoor(); }
                } else { showToast("Sai thứ tự! Chạm từ trụ thấp nhất."); pillarSequence = 1; }
            }
        }

        window.press = function(val) {
            if (val === 'C') keypadInput = "";
            else if (val === 'OK') {
                if (keypadInput === keypadTarget) {
                    showToast("Mật mã ĐÚNG!"); hasKey = true; openDoor();
                } else showToast("Mật mã SAI!");
                document.getElementById('keypad-modal').style.display = 'none'; controls.lock();
            } else { if (keypadInput.length < 4) keypadInput += val; }
            document.getElementById('keypad-display').innerText = keypadInput === "" ? "----" : keypadInput;
        }

        function checkLeverLogic() {
            const answer = ["lever_left", "lever_right", "lever_mid"];
            if (leverSequence.length === 3) {
                if (JSON.stringify(leverSequence) === JSON.stringify(answer)) {
                    hasKey = true; showToast("Gạt cần chính xác! Cửa mở."); openDoor();
                } else { showToast("Sai thứ tự gạt cần!"); leverSequence = []; }
            }
        }

        function showToast(msg) {
            const toast = document.getElementById("toast");
            toast.innerText = msg; toast.style.display = "block";
            setTimeout(() => { toast.style.display = "none"; }, 3000);
        }

        function updateHUD() {
            document.getElementById("level-text").innerText = "Màn: " + currentLevel;
            document.getElementById("hint-text").innerText = "Gợi ý: " + levels[currentLevel-1].hint;
            document.getElementById("inventory-text").innerText = "Túi đồ: " + (hasKey ? "Chìa khóa 🔑" : "Trống");
        }

        /* ---------------- DỰNG DỮ LIỆU LEVEL ---------------- */
        function clearLevel() {
            objectsToUpdate.forEach(o => { world.remove(o.body); scene.remove(o.mesh); });
            interactiveObjects.forEach(o => scene.remove(o));
            objectsToUpdate = []; interactiveObjects = [];
            if (doorMesh) scene.remove(doorMesh);
            hasKey = false; doorOpen = false; leverSequence = []; pillarSequence = 1;
            playerBody.position.set(0, 5, 5); playerBody.velocity.set(0,0,0);
            updateHUD();
        }

        function buildWalls() {
            const mat = new THREE.MeshStandardMaterial({color: 0x3d3d4e});
            const back = new THREE.Mesh(new THREE.BoxGeometry(20, 10, 1), mat); back.position.set(0, 5, -10); scene.add(back);
            const left = new THREE.Mesh(new THREE.BoxGeometry(1, 10, 20), mat); left.position.set(-10, 5, 0); scene.add(left);
            const right = new THREE.Mesh(new THREE.BoxGeometry(1, 10, 20), mat); right.position.set(10, 5, 0); scene.add(right);

            doorMesh = new THREE.Mesh(new THREE.BoxGeometry(3, 6, 0.5), new THREE.MeshStandardMaterial({color: 0x8e44ad}));
            doorMesh.position.set(0, 3, -9.5); doorMesh.name = "door";
            scene.add(doorMesh); interactiveObjects.push(doorMesh);
        }

        function createPhysicsBox(w, h, d, mass, x, y, z, color) {
            const body = new CANNON.Body({ mass: mass, shape: new CANNON.Box(new CANNON.Vec3(w/2, h/2, d/2)) });
            body.position.set(x, y, z); world.addBody(body);
            const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshStandardMaterial({color: color}));
            scene.add(mesh); objectsToUpdate.push({ mesh, body });
        }

        function createItem(type, x, y, z) {
            let mesh;
            if (type === "key") {
                mesh = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.1, 8, 16), new THREE.MeshStandardMaterial({color: 0xf1c40f}));
                mesh.name = "key";
            } else if (type === "keypad") {
                mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1.5, 0.2), new THREE.MeshStandardMaterial({color: 0x2c3e50}));
                mesh.name = "keypad";
            } else if (type === "lever") {
                mesh = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 1), new THREE.MeshStandardMaterial({color: 0xe74c3c}));
            }
            mesh.position.set(x, y, z); scene.add(mesh); interactiveObjects.push(mesh);
            return mesh;
        }

        function openDoor() {
            doorOpen = true;
            let p = 0;
            const iv = setInterval(() => {
                doorMesh.position.y -= 0.1; p += 0.1;
                if (p > 6) { clearInterval(iv); nextLevel(); }
            }, 30);
        }

        function nextLevel() {
            if (currentLevel < 10) {
                currentLevel++; loadLevel(currentLevel);
            } else {
                alert("XUẤT SẮC! BẠN ĐÃ THOÁT KHỎI TẤT CẢ 10 CĂN PHÒNG!");
                returnToMainMenu();
            }
        }

        function loadLevel(lvl) {
            clearLevel(); buildWalls();
            scene.fog.far = 25;

            switch(lvl) {
                case 1: createPhysicsBox(2, 2, 2, 0, 0, 1, 0, 0x8B4513); createItem("key", 0, 2.5, 0); break;
                case 2:
                    createPhysicsBox(1.5, 1.5, 1.5, 5, 0, 5, 2, 0x3498db);
                    const pad = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 0.2), new THREE.MeshStandardMaterial({color: 0xe74c3c}));
                    pad.position.set(0, 0.1, -4); scene.add(pad); break;
                case 3: createItem("keypad", 3, 3, -9.8); keypadTarget = "312"; break;
                case 4: createPhysicsBox(3, 1, 3, 0, 0, 1, 0, 0x27ae60); createPhysicsBox(3, 1, 3, 0, 0, 3, -5, 0x27ae60); createItem("key", 0, 4.5, -5); break;
                case 5: createItem("lever", -3, 3, -9.8).name="lever_left"; createItem("lever", 0, 3, -9.8).name="lever_mid"; createItem("lever", 3, 3, -9.8).name="lever_right"; break;
                case 6: scene.fog.far = 4; const torch = new THREE.Mesh(new THREE.CylinderGeometry(0.1,0.1,1), new THREE.MeshBasicMaterial({color:0xffaa00})); torch.position.set(3, 1, 0); torch.name="torch"; scene.add(torch); interactiveObjects.push(torch); createItem("key", -4, 1, -4); break;
                case 7: createPhysicsBox(2, 2, 2, 5, -3, 2, 0, 0x9b59b6); createPhysicsBox(2, 2, 2, 5, 3, 2, 0, 0x9b59b6); createItem("key", 0, 6, -8); break;
                case 8:
                    for(let i=1; i<=4; i++) {
                        let p = new THREE.Mesh(new THREE.CylinderGeometry(0.5,0.5,1+i), new THREE.MeshStandardMaterial({color:0x34495e}));
                        p.position.set(-5 + i*2.5, (1+i)/2, -5); p.name="pillar_"+i; scene.add(p); interactiveObjects.push(p);
                    } break;
                case 9: createItem("keypad", 0, 3, -9.8); keypadTarget = "8"; break;
                case 10: createPhysicsBox(1.5, 1.5, 1.5, 5, -5, 5, 2, 0x3498db); createItem("keypad", 3, 3, -9.8); keypadTarget = "2026"; break;
            }
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix(); renderer.setSize(window.innerWidth, window.innerHeight);
        }

        function animate() {
            requestAnimationFrame(animate);
            if (controls.isLocked) {
                let dt = (Date.now() - time) / 1000; world.step(1/60, dt, 3);
                let dir = new THREE.Vector3(); camera.getWorldDirection(dir); dir.y = 0; dir.normalize();
                let right = new THREE.Vector3().crossVectors(camera.up, dir).normalize();
                let vX = 0, vZ = 0;
                if (moveForward) { vX += dir.x * 20; vZ += dir.z * 20; }
                if (moveBackward) { vX -= dir.x * 20; vZ -= dir.z * 20; }
                if (moveLeft) { vX -= right.x * 20; vZ -= right.z * 20; }
                if (moveRight) { vX += right.x * 20; vZ += right.z * 20; }

                playerBody.velocity.x = vX; playerBody.velocity.z = vZ;
                controls.getObject().position.copy(playerBody.position);
                controls.getObject().position.y += 1;

                objectsToUpdate.forEach(obj => {
                    obj.mesh.position.copy(obj.body.position);
                    obj.mesh.quaternion.copy(obj.body.quaternion);
                });

                if (currentLevel === 2 && !hasKey && objectsToUpdate.length > 0) {
                    let b = objectsToUpdate[0].body;
                    if (Math.abs(b.position.x) < 1.5 && Math.abs(b.position.z - -4) < 1.5) {
                        hasKey = true; updateHUD(); showToast("Đã kích hoạt nút bấm vật lý! Cửa mở."); openDoor();
                    }
                }
                interactiveObjects.forEach(obj => { if(obj.name === "key") obj.rotation.y += 0.05; });
            }
            time = Date.now(); renderer.render(scene, camera);
        }
    </script>
</body>
</html>
"""

components.html(html_code, height=800, scrolling=False)
