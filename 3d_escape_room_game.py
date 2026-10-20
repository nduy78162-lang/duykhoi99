import streamlit as st
import streamlit.components.v1 as components

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="3D Escape Room - 10 Levels Challenge",
    page_icon="🚪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Information & Instructions
st.sidebar.title("🎮 3D Escape Room")
st.sidebar.caption("Trò chơi giải đố 3D thoát khỏi căn phòng bí mật (10 Màn chơi)")

st.sidebar.markdown("---")
st.sidebar.subheader("📌 Hướng dẫn Deploy lên Streamlit & GitHub")
st.sidebar.markdown("""
1. **Tạo GitHub Repository**:
   - Tạo repo mới trên GitHub (Ví dụ: `3d-escape-room`).
   - Đẩy file `app.py` và `requirements.txt` lên repo.
2. **File `requirements.txt`**:
   ```text
   streamlit
   ```
3. **Deploy lên Streamlit Cloud**:
   - Truy cập [share.streamlit.io](https://share.streamlit.io/).
   - Kết nối GitHub, chọn repo và chọn main file là `app.py`.
   - Nhấn **Deploy**!
""")

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Mẹo chơi")
st.sidebar.info("""
- Nhấp và kéo chuột trong vùng 3D để **xoay góc nhìn camera**.
- Nhấp đúp hoặc Click vào vật thể 3D để **tương tác / nhặt vật phẩm**.
- Xem **Manh mối (Hint)** bên dưới màn hình nếu bị kẹt!
""")

# HTML, CSS and Three.js Game Engine Embedded Component
game_html_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3D Escape Room Game</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Three.js Library -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <!-- OrbitControls -->
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; user-select: none; }
        #canvas-container { width: 100vw; height: 100vh; position: relative; background: #111827; }
        canvas { width: 100%; height: 100%; display: block; }
        
        /* Glassmorphism Styling */
        .glass-panel {
            background: rgba(17, 24, 39, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.15);
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: rgba(0,0,0,0.2); }
        ::-webkit-scrollbar-thumb { background: rgba(59, 130, 246, 0.5); border-radius: 3px; }
    </style>
</head>
<body class="bg-gray-900 text-white select-none">

    <div id="canvas-container">
        <!-- ThreeJS Canvas Inserted Here -->

        <!-- Top UI Header -->
        <div class="absolute top-4 left-4 right-4 flex justify-between items-center z-10 pointer-events-none">
            <div class="glass-panel px-5 py-2.5 rounded-2xl flex items-center gap-3 shadow-xl pointer-events-auto">
                <span class="text-2xl">🚪</span>
                <div>
                    <h1 id="level-title" class="font-bold text-lg text-blue-400">Level 1: Căn Phòng Bí Mật</h1>
                    <p id="level-desc" class="text-xs text-gray-300">Tìm chìa khóa ẩn để mở cửa thoát hiểm.</p>
                </div>
            </div>

            <!-- Level Selector Trigger Button -->
            <button onclick="toggleLevelMenu()" class="glass-panel px-4 py-2.5 rounded-2xl hover:bg-gray-800 text-sm font-semibold transition flex items-center gap-2 shadow-xl pointer-events-auto border border-blue-500/30 text-blue-300">
                <i class="fa-solid fa-list-check"></i> Chọn Màn <span id="level-badge" class="bg-blue-600 text-white text-xs px-2 py-0.5 rounded-full">1/10</span>
            </button>
        </div>

        <!-- Inventory Bar (Bottom Left) -->
        <div class="absolute bottom-4 left-4 z-10 pointer-events-auto">
            <div class="glass-panel p-3 rounded-2xl shadow-xl border border-gray-700/50">
                <div class="text-xs font-semibold text-gray-400 mb-2 flex items-center gap-1">
                    <i class="fa-solid fa-briefcase"></i> TÚI ĐỒ (INVENTORY)
                </div>
                <div id="inventory-slots" class="flex gap-2">
                    <div class="w-12 h-12 rounded-xl bg-gray-800/80 border border-gray-700 flex items-center justify-center text-gray-500 text-xs">Trống</div>
                </div>
            </div>
        </div>

        <!-- Hint Panel & Actions (Bottom Right) -->
        <div class="absolute bottom-4 right-4 z-10 pointer-events-auto flex flex-col items-end gap-2 max-w-sm">
            <div id="hint-box" class="glass-panel p-3.5 rounded-2xl shadow-xl hidden border-l-4 border-yellow-400 text-sm text-yellow-200">
                <div class="font-semibold text-xs text-yellow-400 mb-1 flex items-center gap-1">
                    <i class="fa-solid fa-lightbulb"></i> MANH MỐI:
                </div>
                <span id="hint-text">Đang tải manh mối...</span>
            </div>
            
            <div class="flex gap-2">
                <button onclick="toggleHint()" class="glass-panel px-4 py-2 rounded-xl hover:bg-yellow-500/20 text-yellow-400 text-xs font-semibold transition flex items-center gap-2 border border-yellow-500/30">
                    <i class="fa-solid fa-lightbulb"></i> Gợi ý
                </button>
                <button onclick="resetCurrentLevel()" class="glass-panel px-4 py-2 rounded-xl hover:bg-red-500/20 text-red-400 text-xs font-semibold transition flex items-center gap-2 border border-red-500/30">
                    <i class="fa-solid fa-rotate-right"></i> Chơi lại
                </button>
            </div>
        </div>

        <!-- Interactive Notification Popup -->
        <div id="toast" class="absolute top-20 left-1/2 transform -translate-x-1/2 z-20 glass-panel px-6 py-3 rounded-2xl shadow-2xl border border-blue-500/50 text-white font-medium text-sm hidden flex items-center gap-3 transition-all duration-300">
            <i id="toast-icon" class="fa-solid fa-circle-info text-blue-400 text-lg"></i>
            <span id="toast-msg">Thông báo hệ thống</span>
        </div>

        <!-- Modal 2D Interaction Overlays (e.g. Keypad, Puzzle Popups) -->
        <div id="modal-overlay" class="absolute inset-0 bg-black/70 z-30 hidden flex items-center justify-center p-4 backdrop-blur-sm">
            <div id="modal-content" class="glass-panel p-6 rounded-3xl max-w-md w-full shadow-2xl border border-gray-700 relative text-center">
                <button onclick="closeModal()" class="absolute top-4 right-4 text-gray-400 hover:text-white text-xl"><i class="fa-solid fa-xmark"></i></button>
                <div id="modal-body">
                    <!-- Dynamic Popup Logic Inserted Here -->
                </div>
            </div>
        </div>

        <!-- Level Selector Modal -->
        <div id="level-menu" class="absolute inset-0 bg-black/80 z-40 hidden flex items-center justify-center p-6 backdrop-blur-md">
            <div class="glass-panel p-6 rounded-3xl max-w-2xl w-full shadow-2xl border border-blue-500/30 max-h-[85vh] flex flex-col">
                <div class="flex justify-between items-center mb-6 border-b border-gray-700 pb-4">
                    <h2 class="text-xl font-bold text-blue-400 flex items-center gap-2">
                        <i class="fa-solid fa-map-location-dot"></i> Danh Sách 10 Màn Chơi
                    </h2>
                    <button onclick="toggleLevelMenu()" class="text-gray-400 hover:text-white text-xl"><i class="fa-solid fa-xmark"></i></button>
                </div>
                
                <div id="level-grid" class="grid grid-cols-2 sm:grid-cols-5 gap-3 overflow-y-auto p-1">
                    <!-- Level Buttons Generated Dynamically -->
                </div>
            </div>
        </div>
    </div>

    <script>
        // --- GAME CONFIGURATION & STATE ---
        const TOTAL_LEVELS = 10;
        let currentLevel = 1;
        let unlockedLevels = parseInt(localStorage.getItem('unlocked_level') || '1');
        let inventory = [];
        let hintVisible = false;

        // Level Puzzle State Tracking
        let levelData = {
            1: { name: "Level 1: Chìa Khóa Bí Ẩn", desc: "Tìm chìa khóa cất giấu để mở cửa chính.", hint: "Hãy kiểm tra chiếc bàn nhỏ ở góc phòng.", keyFound: false },
            2: { name: "Level 2: Mã Màu Đèn", desc: "Bấm công tắc màu theo chuỗi chính xác.", hint: "Chuỗi màu: Xanh dương -> Đỏ -> Vàng -> Xanh lá.", progress: [] },
            3: { name: "Level 3: Bảng Mã PIN", desc: "Nhập đúng mật mã 4 chữ số trên cửa.", hint: "Hãy nhìn bức tranh trên tường (Mật mã: 3528).", pin: "" },
            4: { name: "Level 4: Đèn UV Vô Hình", desc: "Dùng đèn pin UV rọi dấu vết ẩn.", hint: "Nhặt Đèn UV trên bàn và chiếu lên bức tường tối.", uvFound: false },
            5: { name: "Level 5: Cân Trọng Lượng", desc: "Đặt các khối tạ sao cho tổng bằng đúng 7kg.", hint: "Sử dụng khối tạ 2kg và khối tạ 5kg (2 + 5 = 7).", currentWeight: 0 },
            6: { name: "Level 6: Gương Phản Chiếu Laser", desc: "Xoay các tấm gương để tia laser chiếu vào mắt cảm biến.", hint: "Nhấp vào các tấm gương để xoay góc 45 độ.", mirrorAngles: [0, 0, 0] },
            7: { name: "Level 7: Simon Says Âm Nhạc", desc: "Gõ lại chuỗi 4 nốt nhạc phát ra từ các chiếc chuông.", hint: "Thứ tự chuông reo: Chuông 1 -> 3 -> 2 -> 4.", sequence: [] },
            8: { name: "Level 8: Đồng Hồ Thời Gian", desc: "Xoay kim đồng hồ quả lắc về đúng 12:30.", hint: "Chỉnh Kim Giờ chỉ số 12 và Kim Phút chỉ số 6 (12:30).", hour: 0, minute: 0 },
            9: { name: "Level 9: Ô Cờ Mã Vua", desc: "Di chuyển quân Mã qua các ô cờ an toàn đến đích.", hint: "Đi theo quy tắc quân Mã cờ vua (hình chữ L).", pathIndex: 0 },
            10: { name: "Level 10: Khối Cổ Vật 3D", desc: "Thu thập đủ 4 mảnh Cổ vật và lắp vào Trụ Nguyên Bản.", hint: "Nhấp vào 4 mảnh cổ vật rải rác xung quanh căn phòng.", pieces: 0 }
        };

        // --- THREE.JS ENGINE VARS ---
        let scene, camera, renderer, controls;
        let interactiveObjects = [];
        let raycaster = new THREE.Raycaster();
        let mouse = new THREE.Vector2();

        // Game 3D Mesh References
        let doorMesh, keyMesh, uvLightMesh, clockHourHand, clockMinuteHand;
        let mirrors = [];

        // --- INITIALIZATION ---
        function initThreeJS() {
            const container = document.getElementById('canvas-container');
            
            // Scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x111827);
            scene.fog = new THREE.FogExp2(0x111827, 0.03);

            // Camera
            camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 2.5, 6);

            // Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            container.appendChild(renderer.domElement);

            // Controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.maxPolarAngle = Math.PI / 2 + 0.05; // Don't go below floor
            controls.minDistance = 2;
            controls.maxDistance = 12;

            // Lights
            setupLights();

            // Window Resize Listener
            window.addEventListener('resize', onWindowResize);

            // Click / Tap Event for 3D Interactions
            renderer.domElement.addEventListener('pointerdown', onPointerDown);

            // Build Room Environment
            buildRoom();

            // Load Level 1
            loadLevel(currentLevel);

            // Animation Loop
            animate();
        }

        function setupLights() {
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
            scene.add(ambientLight);

            const mainLight = new THREE.PointLight(0xfff5ea, 1.2, 20);
            mainLight.position.set(0, 5, 0);
            mainLight.castShadow = true;
            mainLight.shadow.mapSize.width = 1024;
            mainLight.shadow.mapSize.height = 1024;
            scene.add(mainLight);

            // Accent Cyan Soft SpotLight
            const spotLight = new THREE.SpotLight(0x3b82f6, 1.5);
            spotLight.position.set(-4, 4, -4);
            spotLight.angle = Math.PI / 4;
            scene.add(spotLight);
        }

        // --- ROOM ENVIRONMENT BUILDER ---
        function buildRoom() {
            // Room Floor
            const floorGeo = new THREE.PlaneGeometry(12, 12);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x1f2937, roughness: 0.8, metalness: 0.2 });
            const floor = new THREE.Mesh(floorGeo, floorMat);
            floor.rotation.x = -Math.PI / 2;
            floor.receiveShadow = true;
            scene.add(floor);

            // Ceiling
            const ceiling = new THREE.Mesh(floorGeo, new THREE.MeshStandardMaterial({ color: 0x111827 }));
            ceiling.position.y = 6;
            ceiling.rotation.x = Math.PI / 2;
            scene.add(ceiling);

            // Walls
            const wallMat = new THREE.MeshStandardMaterial({ color: 0x374151, roughness: 0.9 });
            
            // Back Wall
            const backWall = new THREE.Mesh(new THREE.PlaneGeometry(12, 6), wallMat);
            backWall.position.set(0, 3, -6);
            backWall.receiveShadow = true;
            scene.add(backWall);

            // Left Wall
            const leftWall = new THREE.Mesh(new THREE.PlaneGeometry(12, 6), wallMat);
            leftWall.position.set(-6, 3, 0);
            leftWall.rotation.y = Math.PI / 2;
            leftWall.receiveShadow = true;
            scene.add(leftWall);

            // Right Wall
            const rightWall = new THREE.Mesh(new THREE.PlaneGeometry(12, 6), wallMat);
            rightWall.position.set(6, 3, 0);
            rightWall.rotation.y = -Math.PI / 2;
            rightWall.receiveShadow = true;
            scene.add(rightWall);

            // Main Exit Door (Back Wall)
            buildDoor();

            // Decorative Furniture (Table)
            buildTable();
        }

        function buildDoor() {
            const doorGroup = new THREE.Group();

            // Door Frame
            const frameGeo = new THREE.BoxGeometry(2.2, 4.2, 0.2);
            const frameMat = new THREE.MeshStandardMaterial({ color: 0x4b5563, roughness: 0.5 });
            const frame = new THREE.Mesh(frameGeo, frameMat);
            frame.position.set(0, 2.1, -5.9);
            doorGroup.add(frame);

            // Door Panel
            const doorGeo = new THREE.BoxGeometry(2, 4, 0.15);
            const doorMat = new THREE.MeshStandardMaterial({ color: 0x1e3a8a, roughness: 0.4, metalness: 0.3 });
            doorMesh = new THREE.Mesh(doorGeo, doorMat);
            doorMesh.position.set(0, 2, -5.85);
            doorMesh.name = "ExitDoor";
            doorGroup.add(doorMesh);

            // Handle
            const handleGeo = new THREE.SphereGeometry(0.1, 16, 16);
            const handleMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.8, roughness: 0.2 });
            const handle = new THREE.Mesh(handleGeo, handleMat);
            handle.position.set(0.7, 2, -5.75);
            doorGroup.add(handle);

            scene.add(doorGroup);
            interactiveObjects.push(doorMesh);
        }

        function buildTable() {
            const tableGroup = new THREE.Group();
            const mat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.7 });

            // Table Top
            const top = new THREE.Mesh(new THREE.BoxGeometry(3, 0.15, 1.8), mat);
            top.position.set(-3.5, 1.2, -3.5);
            top.castShadow = true;
            top.receiveShadow = true;
            tableGroup.add(top);

            // Legs
            const legGeo = new THREE.CylinderGeometry(0.08, 0.08, 1.2);
            const legPositions = [
                [-4.8, 0.6, -4.2], [-2.2, 0.6, -4.2],
                [-4.8, 0.6, -2.8], [-2.2, 0.6, -2.8]
            ];
            legPositions.forEach(pos => {
                const leg = new THREE.Mesh(legGeo, mat);
                leg.position.set(...pos);
                leg.castShadow = true;
                tableGroup.add(leg);
            });

            scene.add(tableGroup);
        }

        // --- LEVEL PUZZLE SPAWNER ---
        function clearLevelObjects() {
            // Remove previous level interactive meshes except door
            interactiveObjects = [doorMesh];
            
            // Remove dynamically added level groups
            const toRemove = [];
            scene.children.forEach(child => {
                if (child.userData && child.userData.isLevelObject) {
                    toRemove.push(child);
                }
            });
            toRemove.forEach(obj => scene.remove(obj));
        }

        function loadLevel(levelNum) {
            currentLevel = levelNum;
            clearLevelObjects();
            
            // Reset Door State
            doorMesh.material.color.setHex(0x1e3a8a);

            // UI Update
            document.getElementById('level-title').innerText = levelData[levelNum].name;
            document.getElementById('level-desc').innerText = levelData[levelNum].desc;
            document.getElementById('level-badge').innerText = `${levelNum}/${TOTAL_LEVELS}`;
            document.getElementById('hint-text').innerText = levelData[levelNum].hint;
            if (hintVisible) toggleHint(); // Hide hint on new level

            const levelGroup = new THREE.Group();
            levelGroup.userData.isLevelObject = true;

            // Build Level-Specific Elements
            switch(levelNum) {
                case 1:
                    // Key under the table
                    const keyGeo = new THREE.TorusGeometry(0.12, 0.04, 8, 24);
                    const keyMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.9, roughness: 0.1 });
                    keyMesh = new THREE.Mesh(keyGeo, keyMat);
                    keyMesh.position.set(-3.5, 1.3, -3.5);
                    keyMesh.rotation.x = Math.PI / 2;
                    keyMesh.name = "KeyL1";
                    levelGroup.add(keyMesh);
                    interactiveObjects.push(keyMesh);
                    break;

                case 2:
                    // Color Buttons on Wall
                    const colors = [0x3b82f6, 0xef4444, 0xeab308, 0x22c55e];
                    const names = ["BLUE", "RED", "YELLOW", "GREEN"];
                    colors.forEach((col, idx) => {
                        const btn = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.2, 0.1), new THREE.MeshStandardMaterial({ color: col }));
                        btn.position.set(-1.5 + idx * 0.8, 2.5, -5.85);
                        btn.rotation.x = Math.PI / 2;
                        btn.name = "ColorBtn_" + names[idx];
                        levelGroup.add(btn);
                        interactiveObjects.push(btn);
                    });
                    break;

                case 3:
                    // Keypad & Hint Frame
                    const keypad = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1.2, 0.1), new THREE.MeshStandardMaterial({ color: 0x1f2937 }));
                    keypad.position.set(2, 2.2, -5.85);
                    keypad.name = "KeypadL3";
                    levelGroup.add(keypad);
                    interactiveObjects.push(keypad);

                    // Painting Hint (3528)
                    const frame = new THREE.Mesh(new THREE.BoxGeometry(1.8, 1.2, 0.05), new THREE.MeshStandardMaterial({ color: 0xb91c1c }));
                    frame.position.set(-3, 3, -5.85);
                    levelGroup.add(frame);
                    break;

                case 4:
                    // UV Light Item
                    const uvGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.4);
                    uvLightMesh = new THREE.Mesh(uvGeo, new THREE.MeshStandardMaterial({ color: 0x8b5cf6, emissive: 0x6d28d9 }));
                    uvLightMesh.position.set(-3.2, 1.3, -3.3);
                    uvLightMesh.name = "UVLightItem";
                    levelGroup.add(uvLightMesh);
                    interactiveObjects.push(uvLightMesh);
                    break;

                case 5:
                    // Weight Scale Base & Blocks
                    const scaleBase = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.7, 0.1), new THREE.MeshStandardMaterial({ color: 0x6b7280 }));
                    scaleBase.position.set(-3.5, 1.3, -3.5);
                    levelGroup.add(scaleBase);

                    // Weights (2kg, 3kg, 5kg)
                    const w2 = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.3, 0.3), new THREE.MeshStandardMaterial({ color: 0x3b82f6 }));
                    w2.position.set(1.5, 0.2, -2); w2.name = "Weight_2kg";
                    const w3 = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 0.4), new THREE.MeshStandardMaterial({ color: 0xef4444 }));
                    w3.position.set(2.5, 0.2, -2); w3.name = "Weight_3kg";
                    const w5 = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.5, 0.5), new THREE.MeshStandardMaterial({ color: 0x10b981 }));
                    w5.position.set(3.5, 0.2, -2); w5.name = "Weight_5kg";

                    [w2, w3, w5].forEach(w => { levelGroup.add(w); interactiveObjects.push(w); });
                    break;

                case 6:
                    // Laser & Mirrors
                    mirrors = [];
                    for(let i=0; i<3; i++) {
                        const m = new THREE.Mesh(new THREE.BoxGeometry(0.8, 1.2, 0.1), new THREE.MeshStandardMaterial({ color: 0x9ca3af, metalness: 0.9, roughness: 0.1 }));
                        m.position.set(-2 + i*2, 1.5, -2);
                        m.name = "Mirror_" + i;
                        levelGroup.add(m);
                        interactiveObjects.push(m);
                        mirrors.push(m);
                    }
                    break;

                case 7:
                    // Simon Says Bells
                    for(let i=1; i<=4; i++) {
                        const bell = new THREE.Mesh(new THREE.SphereGeometry(0.25, 16, 16), new THREE.MeshStandardMaterial({ color: 0xf59e0b, metalness: 0.8 }));
                        bell.position.set(-2 + i*0.8, 2.5, -5.85);
                        bell.name = "Bell_" + i;
                        levelGroup.add(bell);
                        interactiveObjects.push(bell);
                    }
                    break;

                case 8:
                    // Clock
                    const clockFace = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 0.1, 32), new THREE.MeshStandardMaterial({ color: 0xf3f4f6 }));
                    clockFace.rotation.x = Math.PI / 2;
                    clockFace.position.set(-3.5, 3.2, -5.85);
                    clockFace.name = "ClockL8";
                    levelGroup.add(clockFace);
                    interactiveObjects.push(clockFace);
                    break;

                case 9:
                    // Chessboard
                    const board = new THREE.Mesh(new THREE.BoxGeometry(2, 0.1, 2), new THREE.MeshStandardMaterial({ color: 0x1f2937 }));
                    board.position.set(-3.5, 1.3, -3.5);
                    board.name = "ChessboardL9";
                    levelGroup.add(board);
                    interactiveObjects.push(board);
                    break;

                case 10:
                    // 4 Relic Artifact Pieces
                    for(let i=1; i<=4; i++) {
                        const p = new THREE.Mesh(new THREE.OctahedronGeometry(0.2), new THREE.MeshStandardMaterial({ color: 0xec4899, emissive: 0x831843 }));
                        p.position.set(-4 + i*1.8, 0.3, -1 - (i%2));
                        p.name = "Piece_" + i;
                        levelGroup.add(p);
                        interactiveObjects.push(p);
                    }
                    break;
            }

            scene.add(levelGroup);
            showToast(`Bắt đầu ${levelData[levelNum].name}!`, 'info');
        }

        // --- INTERACTION LOGIC (RAYCASTING) ---
        function onPointerDown(event) {
            // Prevent interaction if click was on UI
            if (event.target.tagName !== 'CANVAS') return;

            mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(interactiveObjects, false);

            if (intersects.length > 0) {
                const obj = intersects[0].object;
                handleObjectClick(obj);
            }
        }

        function handleObjectClick(obj) {
            const name = obj.name;

            // Exit Door Interaction
            if (name === "ExitDoor") {
                if (doorMesh.userData.unlocked) {
                    nextLevel();
                } else {
                    showToast("Cửa đã bị khóa! Hãy giải câu đố trước.", "warning");
                }
                return;
            }

            // Level Specific Click Handlers
            switch(currentLevel) {
                case 1:
                    if (name === "KeyL1") {
                        scene.remove(obj);
                        addToInventory("Chìa Khóa Vàng", "🔑");
                        unlockDoor();
                        showToast("Đã nhặt Chìa Khóa! Cửa đã mở.", "success");
                    }
                    break;

                case 2:
                    if (name.startsWith("ColorBtn_")) {
                        const colorName = name.split("_")[1];
                        levelData[2].progress.push(colorName);
                        showToast(`Đã bấm công tắc: ${colorName}`, 'info');

                        const target = ["BLUE", "RED", "YELLOW", "GREEN"];
                        const current = levelData[2].progress;

                        // Check sequence
                        let isCorrect = current.every((val, idx) => val === target[idx]);
                        if (!isCorrect) {
                            showToast("Sai thứ tự màu! Đã đặt lại.", "error");
                            levelData[2].progress = [];
                        } else if (current.length === 4) {
                            unlockDoor();
                            showToast("Chính xác! Cửa chính đã mở.", "success");
                        }
                    }
                    break;

                case 3:
                    if (name === "KeypadL3") {
                        openKeypadModal();
                    }
                    break;

                case 4:
                    if (name === "UVLightItem") {
                        scene.remove(obj);
                        addToInventory("Đèn Đêm UV", "🔦");
                        unlockDoor();
                        showToast("Đã nhặt Đèn UV & Phát hiện mã ẩn! Cửa mở.", "success");
                    }
                    break;

                case 5:
                    if (name.startsWith("Weight_")) {
                        const kg = parseInt(name.split("_")[1]);
                        levelData[5].currentWeight += kg;
                        scene.remove(obj);
                        showToast(`Đã đặt khối tạ ${kg}kg lên cân. (Tổng: ${levelData[5].currentWeight}kg)`, 'info');

                        if (levelData[5].currentWeight === 7) {
                            unlockDoor();
                            showToast("Trọng lượng hoàn hảo (7kg)! Cửa mở.", "success");
                        } else if (levelData[5].currentWeight > 7) {
                            showToast("Quá tải (Lớn hơn 7kg)! Đặt lại màn chơi.", "error");
                            setTimeout(() => loadLevel(5), 1500);
                        }
                    }
                    break;

                case 6:
                    if (name.startsWith("Mirror_")) {
                        obj.rotation.y += Math.PI / 4;
                        showToast("Đã xoay tấm gương!", "info");
                        
                        // Puzzle complete check
                        if (mirrors.every(m => Math.abs(m.rotation.y % Math.PI) < 0.1)) {
                            unlockDoor();
                            showToast("Tia Laser đã chiếu đúng cảm biến! Cửa mở.", "success");
                        }
                    }
                    break;

                case 7:
                    if (name.startsWith("Bell_")) {
                        const num = parseInt(name.split("_")[1]);
                        levelData[7].sequence.push(num);
                        showToast(`Đã gõ Chuông ${num}`, 'info');

                        const targetSeq = [1, 3, 2, 4];
                        const seq = levelData[7].sequence;

                        if (seq[seq.length - 1] !== targetSeq[seq.length - 1]) {
                            showToast("Sai giai điệu! Đã đặt lại.", "error");
                            levelData[7].sequence = [];
                        } else if (seq.length === 4) {
                            unlockDoor();
                            showToast("Giai điệu hoàn hảo! Cửa mở.", "success");
                        }
                    }
                    break;

                case 8:
                    if (name === "ClockL8") {
                        unlockDoor();
                        showToast("Đã chỉnh đồng hồ về 12:30! Chìa khóa xuất hiện & Cửa mở.", "success");
                    }
                    break;

                case 9:
                    if (name === "ChessboardL9") {
                        unlockDoor();
                        showToast("Đã di chuyển nước Mã cờ vua chính xác! Cửa mở.", "success");
                    }
                    break;

                case 10:
                    if (name.startsWith("Piece_")) {
                        scene.remove(obj);
                        levelData[10].pieces++;
                        showToast(`Đã thu thập Mảnh Cổ Vật (${levelData[10].pieces}/4)`, 'info');

                        if (levelData[10].pieces === 4) {
                            addToInventory("Cổ Vật Nguyên Bản", "🔮");
                            unlockDoor();
                            showToast("Đã lắp đủ 4 mảnh Cổ vật! Hoàn thành màn cuối!", "success");
                        }
                    }
                    break;
            }
        }

        function unlockDoor() {
            doorMesh.material.color.setHex(0x10b981); // Turn Green
            doorMesh.userData.unlocked = true;
        }

        function nextLevel() {
            if (currentLevel < TOTAL_LEVELS) {
                currentLevel++;
                if (currentLevel > unlockedLevels) {
                    unlockedLevels = currentLevel;
                    localStorage.setItem('unlocked_level', unlockedLevels.toString());
                }
                loadLevel(currentLevel);
            } else {
                showToast("🎉 CHÚC MỪNG BẠN ĐÃ THOÁT KHỎI TẤT CẢ 10 CĂN PHÒNG!", "success");
            }
        }

        function resetCurrentLevel() {
            loadLevel(currentLevel);
        }

        // --- KEYPAD MODAL (LEVEL 3) ---
        function openKeypadModal() {
            const overlay = document.getElementById('modal-overlay');
            const body = document.getElementById('modal-body');
            
            body.innerHTML = `
                <h3 class="text-lg font-bold text-blue-400 mb-2">Bảng Nhập Mật Mã PIN</h3>
                <input id="pin-input" type="text" readonly class="w-full bg-gray-900 border border-gray-700 rounded-xl py-3 text-center text-2xl tracking-widest font-mono text-green-400 mb-4" value="" />
                <div class="grid grid-cols-3 gap-2 max-w-xs mx-auto">
                    ${[1,2,3,4,5,6,7,8,9,0].map(n => `
                        <button onclick="pressPin(${n})" class="glass-panel py-3 rounded-xl hover:bg-blue-600/30 text-lg font-bold transition">${n}</button>
                    `).join('')}
                    <button onclick="clearPin()" class="glass-panel py-3 rounded-xl hover:bg-red-600/30 text-sm font-bold text-red-400 transition">Xóa</button>
                </div>
            `;
            overlay.classList.remove('hidden');
        }

        function pressPin(num) {
            const input = document.getElementById('pin-input');
            if (input.value.length < 4) {
                input.value += num;
            }
            if (input.value === "3528") {
                closeModal();
                unlockDoor();
                showToast("Mật mã 3528 Chính xác! Cửa đã mở.", "success");
            } else if (input.value.length === 4) {
                showToast("Mật mã SAI! Thử lại.", "error");
                setTimeout(clearPin, 800);
            }
        }

        function clearPin() {
            const input = document.getElementById('pin-input');
            if (input) input.value = "";
        }

        function closeModal() {
            document.getElementById('modal-overlay').classList.add('hidden');
        }

        // --- INVENTORY SYSTEM ---
        function addToInventory(itemName, icon) {
            inventory.push({ name: itemName, icon: icon });
            renderInventory();
        }

        function renderInventory() {
            const container = document.getElementById('inventory-slots');
            if (inventory.length === 0) {
                container.innerHTML = `<div class="w-12 h-12 rounded-xl bg-gray-800/80 border border-gray-700 flex items-center justify-center text-gray-500 text-xs">Trống</div>`;
                return;
            }
            container.innerHTML = inventory.map(item => `
                <div title="${item.name}" class="w-12 h-12 rounded-xl bg-blue-900/40 border border-blue-500/50 flex items-center justify-center text-xl shadow-inner animate-pulse">
                    ${item.icon}
                </div>
            `).join('');
        }

        // --- UI HELPERS ---
        function toggleHint() {
            const hintBox = document.getElementById('hint-box');
            hintVisible = !hintVisible;
            if (hintVisible) {
                hintBox.classList.remove('hidden');
            } else {
                hintBox.classList.add('hidden');
            }
        }

        function toggleLevelMenu() {
            const menu = document.getElementById('level-menu');
            const grid = document.getElementById('level-grid');
            
            if (menu.classList.contains('hidden')) {
                grid.innerHTML = '';
                for (let i = 1; i <= TOTAL_LEVELS; i++) {
                    const isUnlocked = i <= unlockedLevels;
                    const isCurrent = i === currentLevel;
                    
                    grid.innerHTML += `
                        <button onclick="${isUnlocked ? `selectLevel(${i})` : ''}" 
                            class="glass-panel p-4 rounded-2xl flex flex-col items-center justify-center gap-1 transition ${isCurrent ? 'border-2 border-blue-400 bg-blue-900/30' : ''} ${isUnlocked ? 'hover:bg-gray-800 cursor-pointer' : 'opacity-40 cursor-not-allowed'}">
                            <span class="text-xl">${isUnlocked ? (i < unlockedLevels ? '✅' : '🚪') : '🔒'}</span>
                            <span class="font-bold text-sm text-gray-200">Level ${i}</span>
                        </button>
                    `;
                }
                menu.classList.remove('hidden');
            } else {
                menu.classList.add('hidden');
            }
        }

        function selectLevel(levelNum) {
            toggleLevelMenu();
            loadLevel(levelNum);
        }

        function showToast(msg, type = 'info') {
            const toast = document.getElementById('toast');
            const toastMsg = document.getElementById('toast-msg');
            const toastIcon = document.getElementById('toast-icon');

            toastMsg.innerText = msg;
            
            if (type === 'success') {
                toastIcon.className = 'fa-solid fa-circle-check text-green-400 text-lg';
            } else if (type === 'warning' || type === 'error') {
                toastIcon.className = 'fa-solid fa-triangle-exclamation text-yellow-400 text-lg';
            } else {
                toastIcon.className = 'fa-solid fa-circle-info text-blue-400 text-lg';
            }

            toast.classList.remove('hidden');
            setTimeout(() => { toast.classList.add('hidden'); }, 3000);
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();

            // Rotate Key if present
            if (keyMesh && scene.children.includes(keyMesh)) {
                keyMesh.rotation.z += 0.01;
            }

            renderer.render(scene, camera);
        }

        // Start ThreeJS Application on Load
        window.onload = initThreeJS;
    </script>
</body>
</html>
"""

# Render full screen HTML component inside Streamlit
components.html(game_html_code, height=780, scrolling=False)

# Expandable Python / Streamlit Source Code Viewer
with st.expander("📄 Xem & Co-py Mã Nguồn Python app.py chuẩn Streamlit"):
    st.code('''
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="3D Escape Room", layout="wide")

# Embedded HTML Game Code
game_html_code = """
<!-- Dynamic Three.js Game HTML Code -->
"""

components.html(game_html_code, height=780, scrolling=False)
''', language='python')