import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(page_title="Streamlit 3D Puzzle Game", layout="wide")
st.title("🎮 Mini Game 3D Giải Đố - Phong cách Roblox")
st.markdown("Sử dụng các phím **W, A, S, D** trên bàn phím để di chuyển. **Nhiệm vụ:** Đẩy khối lập phương màu đỏ vào khu vực an toàn màu xanh lá!")

# Mã HTML và JavaScript (Three.js) cho Game 3D
game_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; overflow: hidden; background-color: #87CEEB; } /* Bầu trời xanh */
        canvas { display: block; border-radius: 10px; }
        #ui { 
            position: absolute; top: 15px; left: 15px; 
            color: white; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            font-size: 24px; font-weight: bold; 
            text-shadow: 2px 2px 4px #000; 
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div id="ui">Nhiệm vụ: Đẩy khối đỏ vào vùng xanh lá!</div>
    <!-- Tải thư viện Three.js -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
        // 1. Khởi tạo Scene, Camera và Renderer
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x87CEEB); // Màu trời Roblox

        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({antialias: true});
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        // 2. Thêm Ánh sáng (Lighting)
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
        dirLight.position.set(10, 20, 10);
        scene.add(dirLight);

        // 3. Tạo Mặt đất (Sàn nhà)
        const floorGeo = new THREE.PlaneGeometry(100, 100);
        const floorMat = new THREE.MeshStandardMaterial({color: 0x4C8B3E}); // Màu cỏ
        const floor = new THREE.Mesh(floorGeo, floorMat);
        floor.rotation.x = -Math.PI / 2;
        scene.add(floor);

        // 4. Tạo Nhân vật người chơi (Khối màu xanh dương)
        const playerGeo = new THREE.BoxGeometry(1, 1, 1);
        const playerMat = new THREE.MeshStandardMaterial({color: 0x2A75FF});
        const player = new THREE.Mesh(playerGeo, playerMat);
        player.position.set(0, 0.5, 5);
        scene.add(player);

        // 5. Tạo Khối hộp giải đố (Khối màu đỏ cần đẩy)
        const boxGeo = new THREE.BoxGeometry(1.5, 1.5, 1.5);
        const boxMat = new THREE.MeshStandardMaterial({color: 0xFF3333});
        const box = new THREE.Mesh(boxGeo, boxMat);
        box.position.set(0, 0.75, 0);
        scene.add(box);

        // 6. Tạo Vùng Đích (Vùng màu xanh lá mờ)
        const targetGeo = new THREE.BoxGeometry(2.5, 0.1, 2.5);
        const targetMat = new THREE.MeshStandardMaterial({color: 0x00FF00, transparent: true, opacity: 0.5});
        const target = new THREE.Mesh(targetGeo, targetMat);
        target.position.set(0, 0.05, -5);
        scene.add(target);

        // Đặt góc Camera
        camera.position.set(0, 6, 10);

        // 7. Hệ thống điều khiển (WASD)
        const keys = { w: false, a: false, s: false, d: false };
        window.addEventListener('keydown', (e) => {
            const key = e.key.toLowerCase();
            if(keys.hasOwnProperty(key)) keys[key] = true;
        });
        window.addEventListener('keyup', (e) => {
            const key = e.key.toLowerCase();
            if(keys.hasOwnProperty(key)) keys[key] = false;
        });

        // Hàm kiểm tra va chạm bằng Box3
        function checkCollision(obj1, obj2) {
            const box1 = new THREE.Box3().setFromObject(obj1);
            const box2 = new THREE.Box3().setFromObject(obj2);
            return box1.intersectsBox(box2);
        }

        let gameWon = false;
        const speed = 0.15;

        // 8. Vòng lặp Game (Game Loop)
        function animate() {
            requestAnimationFrame(animate);

            if (!gameWon) {
                let prevX = player.position.x;
                let prevZ = player.position.z;

                // Di chuyển nhân vật
                if (keys.w) player.position.z -= speed;
                if (keys.s) player.position.z += speed;
                if (keys.a) player.position.x -= speed;
                if (keys.d) player.position.x += speed;

                // Xử lý va chạm vật lý: Đẩy hộp
                if (checkCollision(player, box)) {
                    let dx = player.position.x - prevX;
                    let dz = player.position.z - prevZ;
                    box.position.x += dx;
                    box.position.z += dz;
                }

                // Kiểm tra điều kiện thắng (Hộp nằm trong vùng đích)
                const targetBox = new THREE.Box3().setFromObject(target);
                const pushBox = new THREE.Box3().setFromObject(box);
                
                if (targetBox.intersectsBox(pushBox)) {
                    document.getElementById('ui').innerHTML = "🎉 Tuyệt vời! Bạn đã vượt qua màn chơi!<br>Nhấn F5 (hoặc Tải lại trang) để chơi lại.";
                    boxMat.color.setHex(0x00FF00); // Đổi hộp thành màu xanh lá khi thắng
                    gameWon = true;
                }

                // Camera đi theo nhân vật mượt mà
                camera.position.x += (player.position.x - camera.position.x) * 0.1;
                camera.position.z = player.position.z + 8;
                camera.lookAt(player.position);
            }

            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
"""

# Render HTML game lên Streamlit với chiều cao 600px
components.html(game_html, height=650, scrolling=False)

st.caption("Mẹo: Nhấp chuột vào khu vực game một lần trước khi dùng phím WASD để bắt đầu di chuyển nhân vật.")
