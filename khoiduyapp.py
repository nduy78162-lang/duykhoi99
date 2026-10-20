import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="3D Escape Room - Bàn Phím",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
        body { margin: 0; overflow: hidden; background-color: #000; font-family: sans-serif; }
        #blocker {
            position: absolute; width: 100%; height: 100%; background-color: rgba(0,0,0,0.6);
            display: flex; flex-direction: column; justify-content: center; align-items: center; color: white; z-index: 10;
        }
        #instructions { font-size: 24px; text-align: center; cursor: pointer; padding: 20px; background: rgba(255,255,255,0.1); border-radius: 10px; border: 2px solid #fff; }
        #crosshair { position: absolute; top: 50%; left: 50%; width: 10px; height: 10px; background: white; border-radius: 50%; transform: translate(-50%, -50%); pointer-events: none; z-index: 5; }
        #hud { position: absolute; top: 20px; left: 20px; color: #00ff00; font-size: 18px; pointer-events: none; z-index: 5; background: rgba(0,0,0,0.5); padding: 10px; border-radius: 8px; }
        #toast { position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%); background: rgba(0,0,0,0.8); color: yellow; padding: 10px 20px; font-size: 18px; border-radius: 10px; display: none; z-index: 5; }
        
        /* Keypad UI */
        #keypad-modal { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #222; padding: 20px; border-radius: 10px; border: 2px solid #0f0; display: none; z-index: 20; text-align: center; pointer-events: auto; }
        #keypad-display { background: #000; color: #0f0; font-size: 30px; margin-bottom: 15px; padding: 10px; letter-spacing: 5px; border-radius: 5px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }
        .btn { padding: 15px; font-size: 20px; background: #444; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #666; }
        .btn-ok { background: #27ae60; } .btn-clear { background: #c0392b; }
    </style>
</head>
<body>
    <div id="blocker">
        <div id="instructions">
            <b>CLICK VÀO ĐÂY ĐỂ CHƠI</b><br/><br/>
            WASD: Di chuyển<br/>
            Chuột: Xoay góc nhìn<br/>
            Space: Nhảy<br/>
            Click Chuột Trái (hoặc phím E): Tương tác vật thể
        </div>
    </div>
    
    <div id="crosshair"></div>
    <div id="hud">
        <div id="level-text">Màn: 1</div>
        <div id="hint-text">Gợi ý: Tìm chìa khóa trên bàn.</div>
        <div id="inventory-text">Túi đồ: Trống</div>
    </div>
    <div id="toast"></div>

    <div id="keypad-modal">
        <div id="keypad-display">----</div>
        <div class="grid">
            <button class="btn" onclick="press('1')">1</button> <button class="btn" onclick="press('2')">2</button> <button class="btn" onclick="press('3')">3</button>
            <button class="btn" onclick="press('4')">4</button> <button class="btn" onclick="press('5')">5</button> <button class="btn" onclick="press('6')">6</button>
            <button class="btn" onclick="press('7')">7</button> <button class="btn" onclick="press('8')">8</button> <button class="btn" onclick="press('9')">9</button>
            <button class="btn btn-clear" onclick="press('C')">C</button> <button class="btn" onclick="press('0')">0</button> <button class="btn btn-ok" onclick="press('OK')">OK</button>
        </div>
    </div>

    <!-- Scripts -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/PointerLockControls.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cannon.js/0.6.2/cannon.min.js"></script>

    <script>
        let camera, scene, renderer, controls, world;
        let playerBody;
        let time = Date.now();
        
        let objectsToUpdate = [];
        let interactiveObjects = [];
        
        // Input state
        let moveForward = false, moveBackward = false, moveLeft = false, moveRight = false, canJump = false;
        let velocity = new THREE.Vector3();
        let direction = new THREE.Vector3();

        // Game state
        let currentLevel = 1;
        let hasKey = false;
        let doorMesh = null;
        let doorOpen = false;
        
        let keypadTarget = "";
        let keypadInput = "";
        let leverSequence = [];
        let pillarSequence = 1;

        // Level Config
        const levels = [
            { id: 1, hint: "Nhặt chìa khóa trên bàn (Click trái) và chạm cửa để mở." },
            { id: 2, hint: "Đẩy khối hộp vật lý màu xanh đè lên công tắc đỏ trên sàn." },
            { id: 3, hint: "Nhìn mã số trên tường và nhập vào bảng điều khiển (Bên phải)." },
            { id: 4, hint: "Nhảy qua bục vật lý (Space) để lấy chìa khóa." },
            { id: 5, hint: "Kéo 3 cần gạt theo thứ tự: Trái, Phải, Giữa." },
            { id: 6, hint: "Phòng tối. Tìm đuốc phát sáng để thấy đường và chìa khóa." },
            { id: 7, hint: "Xếp khối hộp đè lên nhau để leo lên bục lấy chìa khóa." },
            { id: 8, hint: "Chạm 4 cột đá theo thứ tự từ Thấp đến Cao." },
            { id: 9, hint: "Giải toán: Xanh (2) + Đỏ (5) + Vàng (1) = ? Nhập mã." },
            { id: 10, hint: "Màn cuối: Đẩy hộp vào nút, gạt cần, nhập mã 2026." }
        ];

        init();
        animate();

        function init() {
            // Three.js Scene
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x111111);
            scene.fog = new THREE.Fog(0x111111, 0, 20);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);

            // Lighting
            const ambient = new THREE.AmbientLight(0x404040, 1.5);
            scene.add(ambient);
            const light = new THREE.PointLight(0xffffff, 1, 30);
            light.position.set(0, 5, 0);
            light.castShadow = true;
            scene.add(light);

            // Cannon.js Physics World
            world = new CANNON.World();
            world.gravity.set(0, -20, 0);
            world.broadphase = new CANNON.NaiveBroadphase();
            world.solver.iterations = 10;

            // Player Physics Body (Sphere)
            const physicsMaterial = new CANNON.Material("playerMaterial");
            const playerShape = new CANNON.Sphere(1.5);
            playerBody = new CANNON.Body({ mass: 5, material: physicsMaterial });
            playerBody.addShape(playerShape);
            playerBody.position.set(0, 5, 5);
            playerBody.linearDamping = 0.9;
            world.addBody(playerBody);

            // Floor Physics
            const groundShape = new CANNON.Plane();
            const groundBody = new CANNON.Body({ mass: 0 });
            groundBody.addShape(groundShape);
            groundBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1,0,0), -Math.PI/2);
            world.addBody(groundBody);

            // Floor Mesh
            const floorGeo = new THREE.PlaneGeometry(50, 50);
            const floorMat = new THREE.MeshStandardMaterial({ color: 0x333333, roughness: 0.8 });
            const floorMesh = new THREE.Mesh(floorGeo, floorMat);
            floorMesh.rotation.x = -Math.PI / 2;
            floorMesh.receiveShadow = true;
            scene.add(floorMesh);

            // Renderer
            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.shadowMap.enabled = true;
            document.body.appendChild(renderer.domElement);

            // Controls
            controls = new THREE.PointerLockControls(camera, document.body);
            const blocker = document.getElementById('blocker');
            const instructions = document.getElementById('instructions');

            instructions.addEventListener('click', function () {
                controls.lock();
            });
            controls.addEventListener('lock', function () {
                blocker.style.display = 'none';
                document.getElementById('keypad-modal').style.display = 'none';
            });
            controls.addEventListener('unlock', function () {
                blocker.style.display = 'flex';
            });
            scene.add(controls.getObject());

            // Keyboard Listeners
            document.addEventListener('keydown', onKeyDown);
            document.addEventListener('keyup', onKeyUp);
            document.addEventListener('mousedown', onMouseClick); // Tương tác bằng chuột trái

            window.addEventListener('resize', onWindowResize);

            // Load First Level
            loadLevel(currentLevel);
        }

        // --- HỆ THỐNG VẬT LÝ VÀ DI CHUYỂN ---
        function onKeyDown(event) {
            switch (event.code) {
                case 'KeyW': case 'ArrowUp': moveForward = true; break;
                case 'KeyA': case 'ArrowLeft': moveLeft = true; break;
                case 'KeyS': case 'ArrowDown': moveBackward = true; break;
                case 'KeyD': case 'ArrowRight': moveRight = true; break;
                case 'Space': 
                    if (canJump) { playerBody.velocity.y = 12; canJump = false; }
                    break;
                case 'KeyE': onMouseClick(); break; // Hỗ trợ nút E
            }
        }

        function onKeyUp(event) {
            switch (event.code) {
                case 'KeyW': case 'ArrowUp': moveForward = false; break;
                case 'KeyA': case 'ArrowLeft': moveLeft = false; break;
                case 'KeyS': case 'ArrowDown': moveBackward = false; break;
                case 'KeyD': case 'ArrowRight': moveRight = false; break;
            }
        }

        playerBody.addEventListener("collide", function(e){
            const contact = e.contact;
            if(contact.ni.y > 0.5) canJump = true; // Chạm đất mới được nhảy
        });

        // --- HỆ THỐNG TƯƠNG TÁC (RAYCASTER) ---
        function onMouseClick() {
            if (!controls.isLocked) return;

            const raycaster = new THREE.Raycaster();
            raycaster.setFromCamera(new THREE.Vector2(0, 0), camera);
            const intersects = raycaster.intersectObjects(interactiveObjects, false);

            if (intersects.length > 0) {
                const object = intersects[0].object;
                const dist = intersects[0].distance;
                if (dist > 4) {
                    showToast("Quá xa để tương tác!");
                    return;
                }

                handleInteraction(object);
            }
        }

        function handleInteraction(obj) {
            const name = obj.name;
            
            if (name === "key") {
                hasKey = true;
                updateHUD();
                scene.remove(obj);
                showToast("Đã lấy được Chìa Khóa!");
            }
            else if (name === "door") {
                if (doorOpen) return;
                // Kiểm tra điều kiện qua màn
                let canOpen = false;
                if ([1, 4, 6, 7].includes(currentLevel) && hasKey) canOpen = true;
                if (currentLevel === 2 || currentLevel === 8 || currentLevel === 10) canOpen = hasKey; // Màn 2,8 kiểm tra bằng logic trigger
                if (canOpen) openDoor();
                else showToast("Cửa khóa! Yêu cầu hoàn thành giải đố hoặc tìm chìa khóa.");
            }
            else if (name === "keypad") {
                document.exitPointerLock();
                document.getElementById('keypad-modal').style.display = 'block';
                keypadInput = "";
                document.getElementById('keypad-display').innerText = "----";
            }
            else if (name.startsWith("lever_")) {
                obj.rotation.x = Math.PI / 4; // Hoạt ảnh gạt
                leverSequence.push(name);
                checkLeverLogic();
            }
            else if (name === "torch") {
                scene.fog.near = 10; scene.fog.far = 50; // Sáng lên
                scene.add(new THREE.AmbientLight(0x404040, 2));
                scene.remove(obj);
                showToast("Cầm đuốc! Phòng đã sáng.");
            }
            else if (name.startsWith("pillar_")) {
                let id = parseInt(name.split("_")[1]);
                if (id === pillarSequence) {
                    pillarSequence++;
                    obj.material.color.setHex(0x00ff00);
                    showToast(`Cột ${id} đã sáng!`);
                    if (pillarSequence > 4) { hasKey = true; showToast("Cửa đã mở khóa!"); }
                } else {
                    showToast("Sai thứ tự! Chọn lại từ cột thấp nhất.");
                    pillarSequence = 1; // Reset
                }
            }
        }

        // --- GIAO DIỆN KEYPAD ---
        window.press = function(val) {
            if (val === 'C') { keypadInput = ""; }
            else if (val === 'OK') {
                if (keypadInput === keypadTarget) {
                    showToast("Mật mã đúng! Cửa mở.");
                    hasKey = true; openDoor();
                } else { showToast("Sai mật mã!"); }
                document.getElementById('keypad-modal').style.display = 'none';
                controls.lock();
            }
            else { if (keypadInput.length < 4) keypadInput += val; }
            document.getElementById('keypad-display').innerText = keypadInput === "" ? "----" : keypadInput;
        }

        function checkLeverLogic() {
            const answer = ["lever_left", "lever_right", "lever_mid"];
            if (leverSequence.length === 3) {
                if (JSON.stringify(leverSequence) === JSON.stringify(answer)) {
                    hasKey = true; showToast("Chuỗi cần gạt chính xác!");
                } else {
                    showToast("Sai trình tự!"); leverSequence = [];
                }
            }
        }

        function showToast(msg) {
            const toast = document.getElementById("toast");
            toast.innerText = msg;
            toast.style.display = "block";
            setTimeout(() => { toast.style.display = "none"; }, 3000);
        }

        function updateHUD() {
            document.getElementById("level-text").innerText = "Màn: " + currentLevel;
            document.getElementById("hint-text").innerText = "Gợi ý: " + levels[currentLevel-1].hint;
            document.getElementById("inventory-text").innerText = "Túi đồ: " + (hasKey ? "Chìa khóa 🔑" : "Trống");
        }

        // --- XÂY DỰNG MÀN CHƠI ---
        function clearLevel() {
            objectsToUpdate.forEach(o => { world.remove(o.body); scene.remove(o.mesh); });
            interactiveObjects.forEach(o => scene.remove(o));
            objectsToUpdate = []; interactiveObjects = [];
            
            if (doorMesh) scene.remove(doorMesh);
            hasKey = false; doorOpen = false;
            leverSequence = []; pillarSequence = 1;
            playerBody.position.set(0, 5, 5); playerBody.velocity.set(0,0,0);
            updateHUD();
        }

        function buildWalls() {
            const mat = new THREE.MeshStandardMaterial({color: 0x555555});
            const back = new THREE.Mesh(new THREE.BoxGeometry(20, 10, 1), mat);
            back.position.set(0, 5, -10); scene.add(back);
            
            const left = new THREE.Mesh(new THREE.BoxGeometry(1, 10, 20), mat);
            left.position.set(-10, 5, 0); scene.add(left);
            
            const right = new THREE.Mesh(new THREE.BoxGeometry(1, 10, 20), mat);
            right.position.set(10, 5, 0); scene.add(right);

            // Door
            doorMesh = new THREE.Mesh(new THREE.BoxGeometry(3, 6, 0.5), new THREE.MeshStandardMaterial({color: 0x8e44ad}));
            doorMesh.position.set(0, 3, -9.5);
            doorMesh.name = "door";
            scene.add(doorMesh);
            interactiveObjects.push(doorMesh);
        }

        function createPhysicsBox(w, h, d, mass, x, y, z, color) {
            const shape = new CANNON.Box(new CANNON.Vec3(w/2, h/2, d/2));
            const body = new CANNON.Body({ mass: mass });
            body.addShape(shape);
            body.position.set(x, y, z);
            world.addBody(body);

            const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), new THREE.MeshStandardMaterial({color: color}));
            scene.add(mesh);
            objectsToUpdate.push({ mesh, body });
            return {mesh, body};
        }

        function createItem(type, x, y, z) {
            let mesh;
            if (type === "key") {
                mesh = new THREE.Mesh(new THREE.TorusGeometry(0.3, 0.1, 8, 16), new THREE.MeshStandardMaterial({color: 0xffd700}));
                mesh.name = "key";
            } else if (type === "keypad") {
                mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1.5, 0.2), new THREE.MeshStandardMaterial({color: 0x222222}));
                mesh.name = "keypad";
            } else if (type === "lever") {
                mesh = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.1, 1), new THREE.MeshStandardMaterial({color: 0xff0000}));
                mesh.rotation.x = -Math.PI / 4;
            }
            mesh.position.set(x, y, z);
            scene.add(mesh);
            interactiveObjects.push(mesh);
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
                currentLevel++;
                loadLevel(currentLevel);
            } else {
                alert("CHÚC MỪNG BẠN ĐÃ THOÁT KHỎI 10 CĂN PHÒNG!");
                currentLevel = 1; loadLevel(1);
            }
        }

        function loadLevel(lvl) {
            clearLevel();
            buildWalls();
            scene.fog.near = 0.1; scene.fog.far = 100; // Reset fog

            switch(lvl) {
                case 1:
                    createPhysicsBox(2, 2, 2, 0, 0, 1, 0, 0x8B4513); // Bàn
                    createItem("key", 0, 2.5, 0);
                    break;
                case 2:
                    createPhysicsBox(1.5, 1.5, 1.5, 5, 0, 5, 2, 0x3498db); // Hộp đẩy
                    // Nút bấm trên sàn (Trigged by update loop)
                    const pad = new THREE.Mesh(new THREE.CylinderGeometry(1, 1, 0.2), new THREE.MeshStandardMaterial({color: 0xe74c3c}));
                    pad.position.set(0, 0.1, -4); pad.name="pad"; scene.add(pad); interactiveObjects.push(pad);
                    break;
                case 3:
                    createItem("keypad", 3, 3, -9.8); keypadTarget = "312";
                    // Wall Text Fake
                    const txtBox = new THREE.Mesh(new THREE.BoxGeometry(2, 1, 0.1), new THREE.MeshStandardMaterial({color: 0xffffff}));
                    txtBox.position.set(-3, 4, -9.8); scene.add(txtBox);
                    break;
                case 4:
                    createPhysicsBox(3, 1, 3, 0, 0, 1, 0, 0x27ae60);
                    createPhysicsBox(3, 1, 3, 0, 0, 3, -5, 0x27ae60);
                    createItem("key", 0, 4.5, -5);
                    break;
                case 5:
                    const l1 = createItem("lever", -3, 3, -9.8); l1.name="lever_left";
                    const l2 = createItem("lever", 0, 3, -9.8); l2.name="lever_mid";
                    const l3 = createItem("lever", 3, 3, -9.8); l3.name="lever_right";
                    break;
                case 6:
                    scene.fog.near = 1; scene.fog.far = 3; // Phòng tối
                    const torch = new THREE.Mesh(new THREE.CylinderGeometry(0.1,0.1,1), new THREE.MeshBasicMaterial({color:0xffaa00}));
                    torch.position.set(3, 1, 0); torch.name="torch"; scene.add(torch); interactiveObjects.push(torch);
                    createItem("key", -4, 1, -4);
                    break;
                case 7:
                    createPhysicsBox(2, 2, 2, 5, -3, 2, 0, 0x9b59b6);
                    createPhysicsBox(2, 2, 2, 5, 3, 2, 0, 0x9b59b6);
                    createItem("key", 0, 6, -8); // Trên cao
                    break;
                case 8:
                    const p1 = new THREE.Mesh(new THREE.CylinderGeometry(0.5,0.5,2), new THREE.MeshStandardMaterial({color:0x34495e})); p1.position.set(-4,1,-5); p1.name="pillar_1"; scene.add(p1); interactiveObjects.push(p1);
                    const p2 = new THREE.Mesh(new THREE.CylinderGeometry(0.5,0.5,3), new THREE.MeshStandardMaterial({color:0x34495e})); p2.position.set(-1.5,1.5,-5); p2.name="pillar_2"; scene.add(p2); interactiveObjects.push(p2);
                    const p3 = new THREE.Mesh(new THREE.CylinderGeometry(0.5,0.5,4), new THREE.MeshStandardMaterial({color:0x34495e})); p3.position.set(1.5,2,-5); p3.name="pillar_3"; scene.add(p3); interactiveObjects.push(p3);
                    const p4 = new THREE.Mesh(new THREE.CylinderGeometry(0.5,0.5,5), new THREE.MeshStandardMaterial({color:0x34495e})); p4.position.set(4,2.5,-5); p4.name="pillar_4"; scene.add(p4); interactiveObjects.push(p4);
                    break;
                case 9:
                    createItem("keypad", 0, 3, -9.8); keypadTarget = "8";
                    break;
                case 10:
                    createPhysicsBox(1.5, 1.5, 1.5, 5, -5, 5, 2, 0x3498db); // Đẩy
                    const btn = new THREE.Mesh(new THREE.BoxGeometry(2,0.2,2), new THREE.MeshStandardMaterial({color:0xe74c3c})); btn.position.set(-5, 0.1, -5); scene.add(btn);
                    createItem("keypad", 3, 3, -9.8); keypadTarget = "2026";
                    break;
            }
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        // --- GAME LOOP ---
        function animate() {
            requestAnimationFrame(animate);

            if (controls.isLocked === true) {
                // Vật lý FPS Movement
                let dt = (Date.now() - time) / 1000;
                world.step(1/60, dt, 3);
                
                // Cập nhật hướng di chuyển theo góc camera
                camera.getWorldDirection(direction);
                direction.y = 0; direction.normalize();
                
                const right = new THREE.Vector3();
                right.crossVectors(camera.up, direction).normalize();

                const speed = 20;
                let vX = 0, vZ = 0;
                
                if (moveForward) { vX += direction.x * speed; vZ += direction.z * speed; }
                if (moveBackward) { vX -= direction.x * speed; vZ -= direction.z * speed; }
                if (moveLeft) { vX -= right.x * speed; vZ -= right.z * speed; }
                if (moveRight) { vX += right.x * speed; vZ += right.z * speed; }

                // Áp dụng lực cho Physics Body
                playerBody.velocity.x = vX;
                playerBody.velocity.z = vZ;

                // Sync Camera với Cannon.js Body
                controls.getObject().position.copy(playerBody.position);
                controls.getObject().position.y += 1; // Mắt cao hơn tâm cơ thể
                
                // Đồng bộ hộp vật lý
                objectsToUpdate.forEach(obj => {
                    obj.mesh.position.copy(obj.body.position);
                    obj.mesh.quaternion.copy(obj.body.quaternion);
                });

                // Logic đặc biệt Level 2 & 10 (Công tắc đè bằng hộp)
                if ((currentLevel === 2 || currentLevel === 10) && !hasKey && objectsToUpdate.length > 0) {
                    let boxBody = objectsToUpdate[0].body;
                    let targetX = currentLevel === 2 ? 0 : -5;
                    if (Math.abs(boxBody.position.x - targetX) < 1.5 && Math.abs(boxBody.position.z - -4) < 1.5) {
                        hasKey = true; updateHUD(); showToast("Đã kích hoạt nút bấm! Cửa mở.");
                    }
                }
                
                // Quay chìa khóa tự động
                interactiveObjects.forEach(obj => {
                    if(obj.name === "key") obj.rotation.y += 0.05;
                });
            }

            time = Date.now();
            renderer.render(scene, camera);
        }
    </script>
</body>
</html>
"""

components.html(html_code, height=800, scrolling=False)
