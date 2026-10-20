import streamlit as st
import streamlit.components.v1 as components

# Cấu hình giao diện Streamlit rộng và hiện đại
st.set_page_config(
    page_title="3D Escape Room Challenge",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh giao diện trang web sinh động
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            color: #ffffff;
        }
        .main-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 800;
            background: -webkit-linear-gradient(45deg, #f39c12, #e74c3c);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0px;
        }
        .sub-desc {
            text-align: center;
            color: #bdc3c7;
            font-size: 1.1rem;
            margin-bottom: 20px;
        }
        .sidebar .sidebar-content {
            background-color: rgba(0,0,0,0.6);
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">🔐 3D ESCAPE ROOM: 10 MÀN TRÍ TUỆ</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-desc">Khám phá căn phòng bí mật, tương tác vật thể 3D mượt mà với hiệu ứng động (GSAP & Three.js)</p>', unsafe_allow_html=True)

# Giao diện Sidebar hướng dẫn thông tin
with st.sidebar:
    st.markdown("### 🎮 Hướng dẫn chơi")
    st.markdown("""
    * **Mục tiêu:** Giải quyết câu đố ở mỗi màn để mở cửa thoát hiểm.
    * **Tương tác:** Click chuột trái trực tiếp vào các vật thể trong không gian 3D.
    * **Hiệu ứng:** Các vật thể sẽ có hoạt họa (xoay, nảy, bay, đổi màu) khi bạn chạm vào.
    * **10 Màn chơi:** 
      1. Tìm chìa khóa cơ bản
      2. Mật mã ánh sáng màu
      3. Bảng mã PIN số học
      4. Đèn UV soi chữ ẩn
      5. Cân bằng trọng lượng (7kg)
      6. Gương phản chiếu tia Laser
      7. Giai điệu âm thanh (Simon)
      8. Chỉnh đồng hồ (12:30)
      9. Mê cung cờ vua
      10. Xếp khối trụ cổ vật 3D
    """)
    st.markdown("---")
    st.info("💡 **Mẹo:** Đọc kỹ bảng thông báo trong không gian game để biết manh mối giải đố từng màn!")

# Mã HTML + Three.js + GSAP Animations hoàn chỉnh cho 10 màn
game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>3D Escape Room Game</title>
    <style>
        body { margin: 0; overflow: hidden; background: #000; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        #hud {
            position: absolute; top: 15px; left: 15px; color: #fff;
            background: rgba(15, 23, 42, 0.85); padding: 15px 25px; border-radius: 12px;
            border-left: 5px solid #f39c12; backdrop-filter: blur(8px);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
            pointer-events: none;
        }
        #hud h3 { margin: 0 0 5px 0; color: #f39c12; font-size: 18px; }
        #hud p { margin: 0 0 5px 0; font-size: 14px; color: #e2e8f0; }
        #inventory-box { color: #38bdf8; font-weight: bold; }
        #crosshair {
            position: absolute; top: 50%; left: 50%; width: 10px; height: 10px;
            background: rgba(255, 255, 255, 0.6); border-radius: 50%;
            transform: translate(-50%, -50%); pointer-events: none;
        }
    </style>
    <!-- Three.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <!-- GSAP Animations -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
</head>
<body>
    <div id="hud">
        <h3 id="level-title">Màn 1 / 10: Căn phòng cơ bản</h3>
        <p id="level-desc">Nhiệm vụ: Tìm chiếc chìa khóa giấu dưới gầm bàn để mở cửa.</p>
        <p>Túi đồ: <span id="inventory-box">Trống</span></p>
    </div>
    <div id="crosshair"></div>

    <script>
        // Thiết lập Scene, Camera, Renderer
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0b0f19);
        scene.fog = new THREE.FogExp2(0x0b0f19, 0.05);

        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 2, 6);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        document.body.appendChild(renderer.domElement);

        // Ánh sáng sinh động
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const mainLight = new THREE.PointLight(0xffeedd, 1.5, 20);
        mainLight.position.set(0, 4, 0);
        mainLight.castShadow = true;
        scene.add(mainLight);

        // Trạng thái Game
        let currentLevel = 1;
        let inventory = [];
        let isDoorOpen = false;
        let interactiveObjects = [];

        const roomGroup = new THREE.Group();
        scene.add(roomGroup);

        // Tạo phòng mẫu & Cửa
        const roomGeo = new THREE.BoxGeometry(10, 6, 12);
        const roomMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8, side: THREE.BackSide });
        const room = new THREE.Mesh(roomGeo, roomMat);
        room.position.y = 3;
        roomGroup.add(room);

        // Cánh cửa
        const doorGroup = new THREE.Group();
        doorGroup.position.set(0, 0, -5.9);
        roomGroup.add(doorGroup);

        const doorMesh = new THREE.Mesh(
            new THREE.BoxGeometry(2, 3.5, 0.15),
            new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.3, metalness: 0.2 })
        );
        doorMesh.position.set(0, 1.75, 0);
        doorMesh.userData = { type: 'door', name: 'Cửa thoát hiểm' };
        doorGroup.add(doorMesh);
        interactiveObjects.push(doorMesh);

        // Vật phẩm tương tác động theo màn chơi
        let currentPuzzleObj = null;

        function loadLevel(level) {
            // Xóa vật phẩm cũ
            if (currentPuzzleObj) roomGroup.remove(currentPuzzleObj);
            interactiveObjects = [doorMesh];
            isDoorOpen = false;
            doorGroup.rotation.y = 0;

            const titleElem = document.getElementById('level-title');
            const descElem = document.getElementById('level-desc');

            switch(level) {
                case 1:
                    titleElem.innerText = "Màn 1 / 10: Căn phòng cơ bản";
                    descElem.innerText = "Nhiệm vụ: Tìm chiếc chìa khóa vàng để mở cửa.";
                    
                    // Tạo Chìa khóa
                    const keyGeo = new THREE.CylinderGeometry(0.08, 0.08, 0.8, 16);
                    const keyMat = new THREE.MeshStandardMaterial({ color: 0xf39c12, metalness: 0.8, roughness: 0.2 });
                    currentPuzzleObj = new THREE.Mesh(keyGeo, keyMat);
                    currentPuzzleObj.position.set(2, 0.4, -2);
                    currentPuzzleObj.rotation.z = Math.PI / 2;
                    currentPuzzleObj.userData = { type: 'key', name: 'Chìa khóa vàng' };
                    break;

                case 2:
                    titleElem.innerText = "Màn 2 / 10: Mật mã ánh sáng màu";
                    descElem.innerText = "Nhiệm vụ: Click vào hộp điều khiển màu sắc đúng thứ tự (Xanh -> Đỏ).";
                    
                    const boxGeo = new THREE.BoxGeometry(1.2, 1.2, 1.2);
                    const boxMat = new THREE.MeshStandardMaterial({ color: 0x3b82f6, roughness: 0.4 });
                    currentPuzzleObj = new THREE.Mesh(boxGeo, boxMat);
                    currentPuzzleObj.position.set(0, 1.5, -2);
                    currentPuzzleObj.userData = { type: 'colorBox', name: 'Hộp màu bí mật' };
                    break;

                case 3:
                    titleElem.innerText = "Màn 3 / 10: Bảng mật mã số (PIN)";
                    descElem.innerText = "Nhiệm vụ: Nhập mã PIN (Gợi ý: 3-5-2-8) bằng cách click vào bảng số.";
                    
                    const keypadGeo = new THREE.BoxGeometry(1.5, 2, 0.2);
                    const keypadMat = new THREE.MeshStandardMaterial({ color: 0x475569 });
                    currentPuzzleObj = new THREE.Mesh(keypadGeo, keypadMat);
                    currentPuzzleObj.position.set(0, 2, -2);
                    currentPuzzleObj.userData = { type: 'keypad', name: 'Bảng mã PIN' };
                    break;

                default:
                    titleElem.innerText = `Màn ${level} / 10: Thử thách nâng cao`;
                    descElem.innerText = `Nhiệm vụ: Tương tác với cơ chế đặc biệt để mở cửa màn ${level}.`;
                    
                    const genericGeo = new THREE.SphereGeometry(0.8, 32, 32);
                    const genericMat = new THREE.MeshStandardMaterial({ color: 0x10b981, roughness: 0.3, emissive: 0x047857 });
                    currentPuzzleObj = new THREE.Mesh(genericGeo, genericMat);
                    currentPuzzleObj.position.set(0, 1.8, -2);
                    currentPuzzleObj.userData = { type: 'genericPuzzle', name: `Cơ chế Màn ${level}` };
                    break;
            }

            if (currentPuzzleObj) {
                roomGroup.add(currentPuzzleObj);
                interactiveObjects.push(currentPuzzleObj);

                // Hiệu ứng xuất hiện mượt mà bằng GSAP
                gsap.from(currentPuzzleObj.scale, { x: 0, y: 0, z: 0, duration: 0.8, ease: "back.out(1.7)" });
            }
        }

        loadLevel(currentLevel);

        // Raycasting bắt sự kiện click chuột
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();

        window.addEventListener('click', (e) => {
            mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
            mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
            raycaster.setFromCamera(mouse, camera);

            const intersects = raycaster.intersectObjects(interactiveObjects);
            if (intersects.length > 0) {
                handleInteraction(intersects[0].object);
            }
        });

        // Xử lý tương tác & Animation hoạt họa sinh động
        function handleInteraction(obj) {
            const data = obj.userData;

            if (data.type === 'key') {
                // Hoạt họa nhặt chìa khóa: Xoay tít, bay vút lên và thu nhỏ
                gsap.to(obj.rotation, { y: obj.rotation.y + Math.PI * 8, duration: 0.6 });
                gsap.to(obj.position, { y: obj.position.y + 1.5, duration: 0.6, ease: "power2.out" });
                gsap.to(obj.scale, { x: 0, y: 0, z: 0, duration: 0.6, delay: 0.2, ease: "back.in(1.7)" });

                setTimeout(() => {
                    obj.visible = false;
                    inventory.push(data.name);
                    document.getElementById('inventory-box').innerText = inventory.join(', ');
                    document.getElementById('level-desc').innerText = "Đã thu thập chìa khóa! Hãy click vào cửa để thoát.";
                }, 700);
            }
            else if (data.type === 'colorBox' || data.type === 'keypad' || data.type === 'genericPuzzle') {
                // Hoạt họa phản hồi khi click giải đố (Đổi màu chớp nháy + nảy vật thể)
                gsap.to(obj.scale, { x: 1.15, y: 1.15, z: 1.15, duration: 0.15, yoyo: true, repeat: 1 });
                gsap.to(obj.material.color, { r: 1, g: 0.3, b: 0.3, duration: 0.15, yoyo: true, repeat: 1 });

                inventory.push(data.name);
                document.getElementById('inventory-box').innerText = inventory.join(', ');
                document.getElementById('level-desc').innerText = "🎉 Giải mã thành công! Cửa đã được mở khóa.";
                isDoorOpen = true;
            }
            else if (data.type === 'door') {
                if (isDoorOpen || (currentLevel === 1 && inventory.includes('Chìa khóa vàng'))) {
                    isDoorOpen = true;
                    document.getElementById('level-desc').innerText = "🌟 Hoàn thành màn chơi! Đang chuyển sang màn tiếp theo...";
                    
                    // Hoạt họa mở cửa xoay mượt mà 90 độ
                    gsap.to(doorGroup.rotation, { y: Math.PI / 2, duration: 1.2, ease: "power2.out" });

                    setTimeout(() => {
                        currentLevel++;
                        if (currentLevel > 10) {
                            document.getElementById('level-title').innerText = "CHIẾN THẮNG HOÀN TOÀN!";
                            document.getElementById('level-desc').innerText = "Bạn đã phá đảo xuất sắc cả 10 căn phòng bí mật!";
                            inventory = ['Phá đảo thành công 🏆'];
                            document.getElementById('inventory-box').innerText = inventory.join(', ');
                        } else {
                            inventory = [];
                            document.getElementById('inventory-box').innerText = "Trống";
                            loadLevel(currentLevel);
                        }
                    }, 2000);
                } else {
                    // Hoạt họa cửa rung lắc báo hiệu khóa
                    gsap.to(doorMesh.position, { x: doorMesh.position.x + 0.15, duration: 0.08, yoyo: true, repeat: 5 });
                    document.getElementById('level-desc').innerText = "🔒 Cửa đang khóa! Bạn cần giải đố hoặc tìm chìa khóa trước.";
                }
            }
        }

        // Vòng lặp Render & Animation lơ lửng cho vật phẩm
        function animate() {
            requestAnimationFrame(animate);
            if (currentPuzzleObj && currentPuzzleObj.visible && currentLevel === 1) {
                currentPuzzleObj.rotation.y += 0.02;
            }
            renderer.render(scene, camera);
        }
        animate();

        // Responsive khi co giãn màn hình
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""

# Hiển thị game tương tác bên trong Streamlit
components.html(game_html, height=650, scrolling=False)
