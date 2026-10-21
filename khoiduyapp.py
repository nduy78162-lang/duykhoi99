import streamlit as st

st.set_page_config(
    page_title="3D Multi-Stage Puzzle Game", page_icon="🎮", layout="wide"
)

# Nhúng mã nguồn HTML/JS/Three.js trực tiếp vào Streamlit
html_code = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>3D Puzzle Adventure</title>
    <style>
        body { margin: 0; overflow: hidden; background: #111; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; user-select: none; }
        #ui-layer {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; display: flex; flex-direction: column; justify-content: space-between;
            padding: 20px; box-sizing: border-box;
        }
        .hud { pointer-events: auto; background: rgba(0,0,0,0.7); color: #fff; padding: 15px 25px; border-radius: 12px; backdrop-filter: blur(5px); border: 1px solid rgba(255,255,255,0.1); }
        #controls {
            position: absolute; bottom: 30px; left: 50%; transform: translateX(-50%);
            display: grid; grid-template-columns: repeat(3, 60px); grid-template-rows: repeat(2, 60px);
            gap: 10px; pointer-events: auto; z-index: 10;
        }
        .btn-ctrl { background: rgba(255,255,255,0.2); border: 2px solid #fff; color: #fff; font-size: 20px; border-radius: 50%; cursor: pointer; transition: 0.2s; display: flex; align-items: center; justify-content: center; }
        .btn-ctrl:active { background: rgba(255,255,255,0.5); transform: scale(0.95); }
        #btn-up { grid-column: 2; grid-row: 1; }
        #btn-left { grid-column: 1; grid-row: 2; }
        #btn-down { grid-column: 2; grid-row: 2; }
        #btn-right { grid-column: 3; grid-row: 2; }
        
        /* Modal Màn chơi */
        #modal {
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            background: rgba(20, 20, 30, 0.95); padding: 30px; border-radius: 20px; color: white;
            text-align: center; pointer-events: auto; width: 350px; border: 2px solid #00ffcc;
            box-shadow: 0 0 30px rgba(0,255,204,0.4); display: none;
        }
        input, button.action-btn { padding: 12px; margin: 10px 0; width: 80%; border-radius: 8px; border: none; font-size: 16px; }
        button.action-btn { background: #00ffcc; color: #000; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button.action-btn:hover { background: #00b386; color: #fff; }
    </style>
</head>
<body>
    <div id="ui-layer">
        <div class="hud" id="stage-title">Màn 1: Đoán Số May Mắn</div>
        <div id="modal">
            <h2 id="modal-title">Tiêu đề</h2>
            <div id="modal-content">Nội dung</div>
        </div>
    </div>

    <!-- Nút điều khiển di động -->
    <div id="controls">
        <button class="btn-ctrl" id="btn-up">▲</button>
        <button class="btn-ctrl" id="btn-left">◀</button>
        <button class="btn-ctrl" id="btn-down">▼</button>
        <button class="btn-ctrl" id="btn-right">▶</button>
    </div>

    <!-- Thư viện Three.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        let scene, camera, renderer, player;
        let currentStage = 1;
        let keys = {w: false, a: false, s: false, d: false};
        let touchMove = {x: 0, y: 0};
        let isDragging = false, previousMousePosition = {x: 0, y: 0};

        init();
        animate();

        function init() {
            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x1a1a2e);

            camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 5, 10);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            // Ánh sáng
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
            scene.add(ambientLight);
            const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
            dirLight.position.set(10, 20, 10);
            scene.add(dirLight);

            loadStage(currentStage);

            // Sự kiện bàn phím
            window.addEventListener('keydown', (e) => handleKey(e, true));
            window.addEventListener('keyup', (e) => handleKey(e, false));

            // Sự kiện chuột xoay màn hình
            window.addEventListener('mousedown', (e) => { isDragging = true; previousMousePosition = {x: e.clientX, y: e.clientY}; });
            window.addEventListener('mousemove', (e) => {
                if (!isDragging) return;
                let deltaX = e.clientX - previousMousePosition.x;
                camera.rotation.y -= deltaX * 0.005;
                previousMousePosition = {x: e.clientX, y: e.clientY};
            });
            window.addEventListener('mouseup', () => isDragging = false);

            // Sự kiện cảm ứng điện thoại
            let touchStartX = 0;
            window.addEventListener('touchstart', (e) => { touchStartX = e.touches[0].clientX; });
            window.addEventListener('touchmove', (e) => {
                let deltaX = e.touches[0].clientX - touchStartX;
                camera.rotation.y -= deltaX * 0.005;
                touchStartX = e.touches[0].clientX;
            });

            // Gắn sự kiện nút ảo
            bindTouchBtn('btn-up', 'w');
            bindTouchBtn('btn-down', 's');
            bindTouchBtn('btn-left', 'a');
            bindTouchBtn('btn-right', 'd');

            window.addEventListener('resize', onWindowResize);
        }

        function bindTouchBtn(id, key) {
            const btn = document.getElementById(id);
            btn.addEventListener('touchstart', () => keys[key] = true);
            btn.addEventListener('touchend', () => keys[key] = false);
            btn.addEventListener('mousedown', () => keys[key] = true);
            btn.addEventListener('mouseup', () => keys[key] = false);
        }

        function handleKey(e, isDown) {
            switch(e.key.toLowerCase()) {
                case 'w': case 'arrowup': keys.w = isDown; break;
                case 's': case 'arrowdown': keys.s = isDown; break;
                case 'a': case 'arrowleft': keys.a = isDown; break;
                case 'd': case 'arrowright': keys.d = isDown; break;
            }
        }

        // --- QUẢN LÝ CÁC MÀN CHƠI ---
        function loadStage(stage) {
            // Xóa vật thể cũ
            scene.children = scene.children.filter(child => child.isLight);
            document.getElementById('modal').style.display = 'none';

            if (stage === 1) {
                document.getElementById('stage-title').innerText = "Màn 1: Đoán Số May Mắn (1 - 10)";
                createPlayer();
                showModal("Thử Thách Đoán Số", `
                    <p>Tôi đang giữ một số bí mật từ 1 đến 10.</p>
                    <input type="number" id="guess-input" min="1" max="10" placeholder="Nhập số...">
                    <button class="action-btn" onclick="checkStage1()">Đoán Ngay</button>
                `);
            } else if (stage === 2) {
                document.getElementById('stage-title').innerText = "Màn 2: Sắp Xếp Hình Khối 3D";
                createPlayer();
                showModal("Thử Thách Ghép Hình", `
                    <p>Hãy chọn khối hình khớp với màu xanh lá!</p>
                    <button class="action-btn" onclick="nextStage()">Hoàn Thành</button>
                `);
                // Tạo các khối 3D trực quan
                let geo = new THREE.BoxGeometry(2,2,2);
                let mat1 = new THREE.MeshStandardMaterial({color: 0xff0000});
                let mat2 = new THREE.MeshStandardMaterial({color: 0x00ff00});
                let m1 = new THREE.Mesh(geo, mat1); m1.position.set(-3, 0, -5); scene.add(m1);
                let m2 = new THREE.Mesh(geo, mat2); m2.position.set(3, 0, -5); scene.add(m2);
            } else if (stage === 3) {
                document.getElementById('stage-title').innerText = "Màn 3: Vượt Chướng Ngại Vật";
                createPlayer();
                // Tạo các vật cản
                for(let i=0; i<5; i++) {
                    let obs = new THREE.Mesh(new THREE.BoxGeometry(1, 3, 1), new THREE.MeshStandardMaterial({color: 0xff5722}));
                    obs.position.set((Math.random()-0.5)*10, 0, -10 - (i*5));
                    scene.add(obs);
                }
            } else if (stage === 4) {
                document.getElementById('stage-title').innerText = "Màn 4: Thoát Khỏi Mê Cung";
                createPlayer();
                // Tạo mê cung đơn giản
                let mazeFloor = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), new THREE.MeshStandardMaterial({color: 0x333333}));
                mazeFloor.rotation.x = -Math.PI/2;
                scene.add(mazeFloor);
            } else if (stage === 5) {
                document.getElementById('stage-title').innerText = "Màn 5: Câu Hỏi Hóc Búa Cuối Cùng";
                showModal("Câu Hỏi Trí Tuệ", `
                    <p>Cái gì đi bằng 4 chân buổi sáng, 2 chân buổi trưa, và 3 chân buổi chiều?</p>
                    <input type="text" id="riddle-input" placeholder="Đáp án...">
                    <button class="action-btn" onclick="checkStage5()">Trả Lời</button>
                `);
            }
        }

        function createPlayer() {
            const geometry = new THREE.ConeGeometry(0.8, 2, 8);
            const material = new THREE.MeshStandardMaterial({ color: 0x00ffcc });
            player = new THREE.Mesh(geometry, material);
            player.rotation.x = Math.PI / 2;
            player.position.set(0, 0, 0);
            scene.add(player);
        }

        function showModal(title, content) {
            document.getElementById('modal-title').innerText = title;
            document.getElementById('modal-content').innerHTML = content;
            document.getElementById('modal').style.display = 'block';
        }

        // Logic kiểm tra các màn
        let secretNum = Math.floor(Math.random() * 5) + 1;
        function checkStage1() {
            let val = parseInt(document.getElementById('guess-input').value);
            if (val === secretNum) {
                alert("Chính xác! Chuyển sang Màn 2.");
                currentStage = 2;
                loadStage(currentStage);
            } else {
                alert("Sai rồi! Số bí mật là từ 1 đến 5. Thử lại nhé.");
            }
        }

        function checkStage5() {
            let ans = document.getElementById('riddle-input').value.toLowerCase();
            if (ans.includes("con người") || ans.includes("người")) {
                alert("Chúc mừng bạn đã phá đảo toàn bộ tựa game 3D!");
                location.reload();
            } else {
                alert("Gợi ý: Đó là một loài sinh vật sống trên Trái Đất!");
            }
        }

        function nextStage() {
            currentStage++;
            loadStage(currentStage);
        }

        // Vòng lặp game & xử lý di chuyển vật lý
        function animate() {
            requestAnimationFrame(animate);

            if (player) {
                let speed = 0.1;
                if (keys.w) player.position.z -= speed;
                if (keys.s) player.position.z += speed;
                if (keys.a) player.position.x -= speed;
                if (keys.d) player.position.x += speed;

                // Camera đi theo nhân vật
                camera.position.x = player.position.x;
                camera.position.z = player.position.z + 8;

                // Logic hoàn thành Màn 3 & 4 (Chạy tới đích)
                if (currentStage === 3 && player.position.z < -25) {
                    currentStage = 4; loadStage(4);
                }
                if (currentStage === 4 && player.position.z < -12) {
                    currentStage = 5; loadStage(5);
                }
            }

            renderer.render(scene, camera);
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }
    </script>
</body>
</html>
"""

# Hiển thị game trong ứng dụng Streamlit
st.components.v1.html(html_code, height=750, scrolling=False)
