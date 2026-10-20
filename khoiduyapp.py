import streamlit as st
import streamlit.components.v1 as components

# Cấu hình giao diện trang Streamlit
st.set_page_config(
    page_title="3D Escape Room Game",
    page_icon="🚪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ẩn thanh header/footer mặc định của Streamlit để tăng trải nghiệm chơi game
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            padding-left: 0rem !important;
            padding-right: 0rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Mã nguồn HTML / JS Game 3D
game_html_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <style>
        body {
            margin: 0;
            overflow: hidden;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #1a1a1a;
            color: #fff;
            user-select: none;
        }
        #canvas-container {
            width: 100vw;
            height: 100vh;
            display: block;
        }
        #ui-overlay {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 20px;
            box-sizing: border-box;
        }
        .hud-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(0,0,0,0.6);
            padding: 10px 20px;
            border-radius: 8px;
            backdrop-filter: blur(5px);
        }
        .hud-title {
            font-size: 20px;
            font-weight: bold;
            color: #4cd137;
        }
        .hud-hint {
            background: rgba(255,255,255,0.1);
            padding: 8px 15px;
            border-radius: 5px;
            font-size: 14px;
            max-width: 350px;
            text-align: right;
        }
        #keypad-modal {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: rgba(20, 20, 20, 0.95);
            border: 2px solid #4cd137;
            border-radius: 12px;
            padding: 20px;
            display: none;
            flex-direction: column;
            align-items: center;
            pointer-events: auto;
            box-shadow: 0 0 20px rgba(76, 209, 55, 0.4);
        }
        .keypad-display {
            width: 100%;
            height: 40px;
            background: #000;
            color: #4cd137;
            font-family: monospace;
            font-size: 24px;
            text-align: center;
            line-height: 40px;
            margin-bottom: 15px;
            border-radius: 4px;
            letter-spacing: 5px;
        }
        .keypad-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
        }
        .keypad-btn {
            width: 50px;
            height: 50px;
            background: #333;
            color: #fff;
            font-size: 18px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .keypad-btn:active {
            background: #4cd137;
            color: #000;
        }
        #message-toast {
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0,0,0,0.85);
            color: #fbc531;
            padding: 10px 25px;
            border-radius: 20px;
            font-size: 16px;
            display: none;
            border: 1px solid #fbc531;
        }
        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 8px;
            height: 8px;
            background: rgba(255,255,255,0.5);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div id="canvas-container"></div>
    <div id="crosshair"></div>
    
    <div id="ui-overlay">
        <div class="hud-header">
            <div class="hud-title" id="level-title">Màn 1: Cánh cửa khởi đầu</div>
            <div class="hud-hint" id="level-hint">Manh mối: Chạm vào chìa khóa trên bàn để mở cửa.</div>
        </div>
        <div id="message-toast"></div>
    </div>

    <!-- Keypad cho màn câu đố mã số -->
    <div id="keypad-modal">
        <div class="keypad-display" id="keypad-input">----</div>
        <div class="keypad-grid">
            <button class="keypad-btn" onclick="pressKey('1')">1</button>
            <button class="keypad-btn" onclick="pressKey('2')">2</button>
            <button class="keypad-btn" onclick="pressKey('3')">3</button>
            <button class="keypad-btn" onclick="pressKey('4')">4</button>
            <button class="keypad-btn" onclick="pressKey('5')">5</button>
            <button class="keypad-btn" onclick="pressKey('6')">6</button>
            <button class="keypad-btn" onclick="pressKey('7')">7</button>
            <button class="keypad-btn" onclick="pressKey('8')">8</button>
            <button class="keypad-btn" onclick="pressKey('9')">9</button>
            <button class="keypad-btn" style="background:#e84118;" onclick="clearKeypad()">C</button>
            <button class="keypad-btn" onclick="pressKey('0')">0</button>
            <button class="keypad-btn" style="background:#4cd137;" onclick="submitKeypad()">OK</button>
        </div>
    </div>

    <!-- Import thư viện 3D & Vật lý -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cannon.js/0.6.2/cannon.min.js"></script>

    <script>
        let scene, camera, renderer, controls, world;
        let raycaster = new THREE.Raycaster();
        let mouse = new THREE.Vector2();
        
        let currentLevel = 1;
        let inventory = { hasKey: false, hasTorch: false };
        let levelObjects = [];
        let physicsBodies = [];
        let doorMesh;
        let isDoorOpen = false;

        const levelsData = [
            { id: 1, title: "Màn 1: Cánh cửa khởi đầu", hint: "Chạm vào chìa khóa trên bàn để nhặt, sau đó chạm vào cửa." },
            { id: 2, title: "Màn 2: Mật mã rương gỗ", hint: "Quan sát màu sắc các khối hộp trong phòng để tìm mã gồm 3 chữ số (Đỏ, Xanh, Vàng)." },
            { id: 3, title: "Màn 3: Công tắc ẩn", hint: "Có 3 gạt tay trên tường. Hãy gạt đúng thứ tự: Trái -> Phải -> Giữa." },
            { id: 4, title: "Màn 4: Trọng lực vật lý", hint: "Thả đủ 3 khối hộp nặng lên đĩa cân vật lý để kích hoạt mở cửa." },
            { id: 5, title: "Màn 5: Căn phòng tối", hint: "Tìm ngọn đuốc trên kệ để thắp sáng phòng và nhìn rõ chìa khóa." },
            { id: 6, title: "Màn 6: Xoay đĩa cổ đại", hint: "Xoay khối đá trung tâm sao cho mặt có ký hiệu hướng về phía cửa." },
            { id: 7, title: "Màn 7: Phương trình màu sắc", hint: "Giải mã: Đỏ(1) + Xanh(2) + Vàng(3). Nhập tổng kết quả vào ổ khóa." },
            { id: 8, title: "Màn 8: Đòn đẩy vật lý", hint: "Đẩy khối đá nặng va vào nút bấm trên tường để kích hoạt cửa." },
            { id: 9, title: "Màn 9: Mật mã chuỗi chạm", hint: "Chạm vào 4 trụ đá theo đúng thứ tự độ cao: Thấp nhất -> Cao nhất." },
            { id: 10, title: "Màn 10: Thử thách cuối cùng", hint: "Giải bài toán logic tổng hợp: Nhặt chìa khóa, gạt cần và nhập mã '9999'." }
        ];

        let keypadTargetCode = "";
        let keypadInputBuffer = "";
        let leverOrderTracker = [];

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1e1e24);
            scene.fog = new THREE.FogExp2(0x1e1e24, 0.05);

            camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 3, 7);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            document.getElementById('canvas-container').appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.maxPolarAngle = Math.PI / 2 - 0.05;

            world = new CANNON.World();
            world.gravity.set(0, -9.82, 0);

            setupLighting();
            loadLevel(currentLevel);

            window.addEventListener('resize', onWindowResize);
            window.addEventListener('pointerdown', onPointerDown);

            animate();
        }

        function setupLighting() {
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
            scene.add(ambientLight);

            const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(5, 10, 5);
            dirLight.castShadow = true;
            dirLight.shadow.mapSize.width = 1024;
            dirLight.shadow.mapSize.height = 1024;
            scene.add(dirLight);
        }

        function createRoom() {
            const floorGeo = new THREE.PlaneGeometry(10, 10);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x353b48, roughness: 0.8 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            floor.receiveShadow = true;
            scene.add(floor);

            const floorBody = new CANNON.Body({ mass: 0, shape: new CANNON.Plane() });
            floorBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);
            world.addBody(floorBody);

            const wallMat = new THREE.MeshStandardMaterial({ color: 0x2f3640 });
            const backWall = new THREE.Mesh(new THREE.BoxGeometry(10, 6, 0.2), wallMat);
            backWall.position.set(0, 3, -5);
            backWall.receiveShadow = true;
            scene.add(backWall);

            const doorGeo = new THREE.BoxGeometry(1.6, 3, 0.1);
            const doorMat = new THREE.MeshStandardMaterial({ color: 0x8c7ae6, metalness: 0.5 });
            doorMesh = new THREE.Mesh(doorGeo, doorMat);
            doorMesh.position.set(0, 1.5, -4.9);
            doorMesh.castShadow = true;
            doorMesh.name = "exitDoor";
            scene.add(doorMesh);
        }

        function clearLevel() {
            levelObjects.forEach(obj => scene.remove(obj));
            physicsBodies.forEach(body => world.remove(body));
            levelObjects = [];
            physicsBodies = [];
            isDoorOpen = false;
            leverOrderTracker = [];
            if (doorMesh) doorMesh.position.set(0, 1.5, -4.9);
        }

        function loadLevel(lvl) {
            clearLevel();
            createRoom();

            const data = levelsData[lvl - 1];
            document.getElementById('level-title').innerText = data.title;
            document.getElementById('level-hint').innerText = "Gợi ý: " + data.hint;

            switch (lvl) {
                case 1:
                    createTableWithKey(0, 0, 1);
                    break;
                case 2:
                    createBox(1.5, 0.5, 0, 0xe74c3c);
                    createBox(-1.5, 0.5, 1, 0x3498db);
                    createBox(-1.5, 1.2, 1, 0x3498db);
                    createBox(0, 0.5, 2, 0xf1c40f);
                    createBox(0.6, 0.5, 2, 0xf1c40f);
                    createBox(0.3, 1.2, 2, 0xf1c40f);
                    keypadTargetCode = "123";
                    createKeypadConsole();
                    break;
                case 3:
                    createLever(-2, 2, -4.8, "lever1");
                    createLever(0, 2, -4.8, "lever2");
                    createLever(2, 2, -4.8, "lever3");
                    break;
                case 4:
                    createScalePlatform(0, 0.1, -2);
                    createPhysicsCube(-1.5, 1, 0);
                    createPhysicsCube(-1.8, 1, 1);
                    createPhysicsCube(1.5, 1, 0);
                    break;
                case 5:
                    scene.background = new THREE.Color(0x050508);
                    scene.fog.color = new THREE.Color(0x050508);
                    createTorchItem(2, 1, -2);
                    createHiddenKeyInDark(-2, 0.2, -3);
                    break;
                case 6:
                    createRotatableRune(0, 1.5, -2);
                    break;
                case 7:
                    keypadTargetCode = "6";
                    createKeypadConsole();
                    break;
                case 8:
                    createPhysicsHeavyBoulder(2, 1, 0);
                    createWallButton(-2, 1.5, -4.8);
                    break;
                case 9:
                    createPillar(-2.2, 1.0, -3, 1);
                    createPillar(-0.7, 1.5, -3, 2);
                    createPillar(0.7, 2.0, -3, 3);
                    createPillar(2.2, 2.5, -3, 4);
                    break;
                case 10:
                    keypadTargetCode = "9999";
                    createKeypadConsole();
                    createTableWithKey(-2, 0, 0);
                    createLever(2, 2, -4.8, "masterLever");
                    break;
            }
        }

        function createTableWithKey(x, y, z) {
            const table = new THREE.Mesh(new THREE.BoxGeometry(2, 1, 1.2), new THREE.MeshStandardMaterial({ color: 0x78e08f }));
            table.position.set(x, y + 0.5, z);
            scene.add(table);
            levelObjects.push(table);

            const key = new THREE.Mesh(new THREE.TorusGeometry(0.15, 0.04, 8, 16), new THREE.MeshStandardMaterial({ color: 0xf6b93b, metalness: 0.8 }));
            key.position.set(x, y + 1.1, z);
            key.name = "keyItem";
            scene.add(key);
            levelObjects.push(key);
        }

        function createBox(x, y, z, color) {
            const mesh = new THREE.Mesh(new THREE.BoxGeometry(0.6, 0.6, 0.6), new THREE.MeshStandardMaterial({ color: color }));
            mesh.position.set(x, y, z);
            mesh.castShadow = true;
            scene.add(mesh);
            levelObjects.push(mesh);
        }

        function createKeypadConsole() {
            const consoleMesh = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1, 0.2), new THREE.MeshStandardMaterial({ color: 0x2f3542 }));
            consoleMesh.position.set(1.5, 1.5, -4.8);
            consoleMesh.name = "keypadConsole";
            scene.add(consoleMesh);
            levelObjects.push(consoleMesh);
        }

        function createLever(x, y, z, name) {
            const base = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.5, 0.2), new THREE.MeshStandardMaterial({ color: 0x57606f }));
            base.position.set(x, y, z);
            const handle = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 0.8), new THREE.MeshStandardMaterial({ color: 0xe84118 }));
            handle.position.set(x, y, z + 0.1);
            handle.rotation.x = Math.PI / 4;
            handle.name = name;
            scene.add(base, handle);
            levelObjects.push(base, handle);
        }

        function createPhysicsCube(x, y, z) {
            const mesh = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.5, 0.5), new THREE.MeshStandardMaterial({ color: 0x00a8ff }));
            mesh.castShadow = true;
            scene.add(mesh);
            levelObjects.push(mesh);

            const body = new CANNON.Body({ mass: 2, shape: new CANNON.Box(new CANNON.Vec3(0.25, 0.25, 0.25)) });
            body.position.set(x, y, z);
            world.addBody(body);
            physicsBodies.push({ mesh: mesh, body: body });
            mesh.userData = { body: body };
        }

        function createScalePlatform(x, y, z) {
            const platform = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 0.1, 32), new THREE.MeshStandardMaterial({ color: 0x44bd32 }));
            platform.position.set(x, y, z);
            scene.add(platform);
            levelObjects.push(platform);
        }

        function createTorchItem(x, y, z) {
            const torch = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.08, 0.6), new THREE.MeshStandardMaterial({ color: 0xe1b12c }));
            torch.position.set(x, y, z);
            torch.name = "torchItem";
            scene.add(torch);
            levelObjects.push(torch);
        }

        function createHiddenKeyInDark(x, y, z) {
            const key = new THREE.Mesh(new THREE.TorusGeometry(0.12, 0.03, 8, 16), new THREE.MeshStandardMaterial({ color: 0xf5cd79 }));
            key.position.set(x, y, z);
            key.name = "keyItem";
            scene.add(key);
            levelObjects.push(key);
        }

        function createRotatableRune(x, y, z) {
            const rune = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.8, 0.8), new THREE.MeshStandardMaterial({ color: 0x9c88ff }));
            rune.position.set(x, y, z);
            rune.name = "rotatableRune";
            scene.add(rune);
            levelObjects.push(rune);
        }

        function createPhysicsHeavyBoulder(x, y, z) {
            const mesh = new THREE.Mesh(new THREE.SphereGeometry(0.5, 16, 16), new THREE.MeshStandardMaterial({ color: 0x7f8c8d }));
            mesh.castShadow = true;
            scene.add(mesh);
            levelObjects.push(mesh);

            const body = new CANNON.Body({ mass: 5, shape: new CANNON.Sphere(0.5) });
            body.position.set(x, y, z);
            world.addBody(body);
            physicsBodies.push({ mesh: mesh, body: body });
        }

        function createWallButton(x, y, z) {
            const btn = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, 0.2), new THREE.MeshStandardMaterial({ color: 0xc0392b }));
            btn.position.set(x, y, z);
            btn.rotation.x = Math.PI / 2;
            scene.add(btn);
            levelObjects.push(btn);
        }

        function createPillar(x, y, z, order) {
            const pillar = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.3, y * 2), new THREE.MeshStandardMaterial({ color: 0x00d2d3 }));
            pillar.position.set(x, y, z);
            pillar.name = "pillar_" + order;
            scene.add(pillar);
            levelObjects.push(pillar);
        }

        function onPointerDown(event) {
            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(scene.children);

            if (intersects.length > 0) {
                const clickedObj = intersects[0].object;

                if (clickedObj.name === "keyItem") {
                    inventory.hasKey = true;
                    scene.remove(clickedObj);
                    showToast("Đã nhặt được Chìa Khóa!");
                }

                if (clickedObj.name === "exitDoor") {
                    if (currentLevel === 1 || currentLevel === 5 || currentLevel === 10) {
                        if (inventory.hasKey) {
                            openDoorAndNextLevel();
                        } else {
                            showToast("Cửa đã khóa! Cần tìm chìa khóa.");
                        }
                    } else if (isDoorOpen) {
                        nextLevel();
                    } else {
                        showToast("Cửa đang đóng chặt!");
                    }
                }

                if (clickedObj.name === "keypadConsole") {
                    document.getElementById('keypad-modal').style.display = 'flex';
                }

                if (clickedObj.name.startsWith("lever")) {
                    clickedObj.rotation.x *= -1;
                    leverOrderTracker.push(clickedObj.name);
                    checkLeverSequence();
                }

                if (clickedObj.name.startsWith("pillar_")) {
                    const pillarId = parseInt(clickedObj.name.split("_")[1]);
                    handlePillarSequence(pillarId);
                }

                if (clickedObj.name === "rotatableRune") {
                    clickedObj.rotation.y += Math.PI / 2;
                    if (Math.abs(clickedObj.rotation.y % (Math.PI * 2)) < 0.1) {
                        showToast("Cổ vật đã xoay đúng hướng!");
                        openDoorAndNextLevel();
                    }
                }

                if (clickedObj.name === "torchItem") {
                    scene.background = new THREE.Color(0x1e1e24);
                    scene.fog.color = new THREE.Color(0x1e1e24);
                    const pointLight = new THREE.PointLight(0xffa500, 2, 10);
                    camera.add(pointLight);
                    scene.add(camera);
                    scene.remove(clickedObj);
                    showToast("Đã thắp sáng căn phòng!");
                }

                if (clickedObj.userData && clickedObj.userData.body) {
                    const body = clickedObj.userData.body;
                    body.applyImpulse(new CANNON.Vec3(0, 2, -5), body.position);
                }
            }
        }

        function checkLeverSequence() {
            const correctOrder = ["lever1", "lever3", "lever2"];
            if (leverOrderTracker.length === 3) {
                if (JSON.stringify(leverOrderTracker) === JSON.stringify(correctOrder)) {
                    showToast("Mật mã cần gạt chính xác!");
                    openDoorAndNextLevel();
                } else {
                    showToast("Sai thứ tự! Đã đặt lại.");
                    leverOrderTracker = [];
                }
            }
        }

        let pillarStep = 1;
        function handlePillarSequence(id) {
            if (id === pillarStep) {
                pillarStep++;
                showToast(`Đúng trụ thứ ${id}!`);
                if (pillarStep > 4) {
                    showToast("Đã mở khóa các trụ!");
                    openDoorAndNextLevel();
                }
            } else {
                showToast("Sai thứ tự! Chọn lại từ trụ thấp nhất.");
                pillarStep = 1;
            }
        }

        function pressKey(num) {
            if (keypadInputBuffer.length < 4) {
                keypadInputBuffer += num;
                document.getElementById('keypad-input').innerText = keypadInputBuffer;
            }
        }

        function clearKeypad() {
            keypadInputBuffer = "";
            document.getElementById('keypad-input').innerText = "----";
        }

        function submitKeypad() {
            if (keypadInputBuffer === keypadTargetCode) {
                showToast("Mật mã chính xác!");
                document.getElementById('keypad-modal').style.display = 'none';
                clearKeypad();
                openDoorAndNextLevel();
            } else {
                showToast("Mật mã sai! Hãy thử lại.");
                clearKeypad();
            }
        }

        function openDoorAndNextLevel() {
            isDoorOpen = true;
            showToast("Cửa đang mở! Chuẩn bị sang màn tiếp...");
            let openProgress = 0;
            const interval = setInterval(() => {
                if (doorMesh) {
                    doorMesh.position.x += 0.05;
                    openProgress += 0.05;
                    if (openProgress >= 1.8) {
                        clearInterval(interval);
                        setTimeout(() => { nextLevel(); }, 1000);
                    }
                }
            }, 30);
        }

        function nextLevel() {
            if (currentLevel < 10) {
                currentLevel++;
                inventory = { hasKey: false, hasTorch: false };
                loadLevel(currentLevel);
            } else {
                alert("Chúc mừng! Bạn đã xuất sắc vượt qua 10 căn phòng bí mật!");
                currentLevel = 1;
                loadLevel(currentLevel);
            }
        }

        function showToast(msg) {
            const toast = document.getElementById('message-toast');
            toast.innerText = msg;
            toast.style.display = 'block';
            setTimeout(() => { toast.style.display = 'none'; }, 3000);
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        function animate() {
            requestAnimationFrame(animate);
            world.step(1 / 60);

            physicsBodies.forEach(item => {
                item.mesh.position.copy(item.body.position);
                item.mesh.quaternion.copy(item.body.quaternion);
            });

            if (currentLevel === 4 && !isDoorOpen) {
                let count = 0;
                physicsBodies.forEach(item => {
                    if (item.body.position.z < -1.5 && item.body.position.y < 0.5) count++;
                });
                if (count >= 3) {
                    showToast("Đủ trọng lượng! Mở cửa.");
                    openDoorAndNextLevel();
                }
            }

            if (currentLevel === 8 && !isDoorOpen) {
                physicsBodies.forEach(item => {
                    if (item.body.position.distanceTo(new CANNON.Vec3(-2, 1.5, -4.8)) < 1.0) {
                        showToast("Khối đá đã đè vào công tắc!");
                        openDoorAndNextLevel();
                    }
                });
            }

            controls.update();
            renderer.render(scene, camera);
        }

        window.onload = init;
    </script>
</body>
</html>
"""

# Nhúng Game HTML/JS vào ứng dụng Streamlit
components.html(game_html_code, height=800, scrolling=False)
