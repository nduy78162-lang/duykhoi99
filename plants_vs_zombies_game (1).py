import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Plants vs. Zombies 2D - Streamlit Edition",
    page_icon="🌻",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { 
        background-color: #0b140b; 
        color: #ffffff; 
    }
    header, footer { 
        visibility: hidden; 
    }
    h1 { 
        color: #55ff55 !important; 
        font-family: 'Trebuchet MS', sans-serif; 
        text-align: center; 
        margin-bottom: 5px; 
        text-shadow: 2px 2px #000; 
    }
    p { 
        text-align: center; 
        color: #a5d6a7; 
        font-family: sans-serif; 
        margin-bottom: 10px; 
    }
</style>
""", unsafe_allow_html=True)

st.title("🌻 PLANTS VS. ZOMBIES 2D 🧟")
st.markdown("Chọn cây từ thanh công cụ bên trên và nhấp vào ô cỏ trống để trồng. Nhấp chọn **Mặt Trời ☀️** để thu thập năng lượng!")

pvz_game_html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body { 
            background: #081208; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            overflow: hidden; 
        }
        
        #game-container {
            position: relative;
            width: 880px;
            height: 560px;
            border: 4px solid #3d2514;
            border-radius: 12px;
            box-shadow: 0 0 40px rgba(0, 0, 0, 0.9);
            background: #111;
        }
        
        canvas { display: block; cursor: pointer; border-radius: 8px; }
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="pvzCanvas" width="880" height="560"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('pvzCanvas');
        const ctx = canvas.getContext('2d');

        // Bàn cờ 5 Hàng x 8 Cột
        const ROWS = 5;
        const COLS = 8;
        const CELL_W = 85;
        const CELL_H = 85;
        const OFFSET_X = 140; // Lề trái dành cho vùng nguy hiểm / nhà
        const OFFSET_Y = 100; // Lề trên dành cho Thanh UI

        // Trạng thái Game
        let suns = 150;
        let score = 0;
        let gameOver = false;
        let selectedPlant = null; // 'sunflower' hoặc 'peashooter'
        let frameCount = 0;

        // Danh sách thẻ cây
        const PLANT_TYPES = {
            'sunflower': { name: 'Sunflower', cost: 50, icon: '🌻' },
            'peashooter': { name: 'Peashooter', cost: 100, icon: '🫛' }
        };

        // Lưới bàn cờ 5x8
        let grid = Array(ROWS).fill(null).map(() => Array(COLS).fill(null));

        // Mảng chứa thực thể
        let plants = [];
        let zombies = [];
        let peas = [];
        let fallingSuns = [];
        let particles = [];

        // Vẽ Cây Hướng Dương (Sunflower)
        function drawSunflower(x, y, animFrame) {
            ctx.save();
            ctx.translate(x, y);

            // Nhún nhảy nhẹ theo nhịp
            const bob = Math.sin(animFrame * 0.1) * 2;

            // Thân cây
            ctx.beginPath();
            ctx.moveTo(0, 10);
            ctx.quadraticCurveTo(-5, 25, 0, 35);
            ctx.strokeStyle = '#2e7d32';
            ctx.lineWidth = 6;
            ctx.stroke();

            // Lá
            ctx.fillStyle = '#388e3c';
            ctx.beginPath(); ctx.ellipse(-12, 28, 10, 5, -0.4, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.ellipse(12, 28, 10, 5, 0.4, 0, Math.PI * 2); ctx.fill();

            // Cánh hoa (Petals)
            const petalCount = 10;
            ctx.fillStyle = '#ffeb3b';
            for (let i = 0; i < petalCount; i++) {
                const angle = (i * Math.PI * 2) / petalCount + Math.sin(animFrame * 0.05) * 0.1;
                const px = Math.cos(angle) * 18;
                const py = (bob - 5) + Math.sin(angle) * 18;
                ctx.beginPath();
                ctx.arc(px, py, 9, 0, Math.PI * 2);
                ctx.fill();
            }

            // Mắt xích trung tâm
            ctx.fillStyle = '#8d6e63';
            ctx.beginPath();
            ctx.arc(0, bob - 5, 14, 0, Math.PI * 2);
            ctx.fill();

            // Mắt & Nụ cười
            ctx.fillStyle = '#000';
            ctx.beginPath(); ctx.arc(-4, bob - 8, 2.2, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.arc(4, bob - 8, 2.2, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.arc(0, bob - 4, 5, 0, Math.PI); ctx.stroke();

            ctx.restore();
        }

        // Vẽ Cây Bắn Đậu (Peashooter)
        function drawPeashooter(x, y, animFrame) {
            ctx.save();
            ctx.translate(x, y);

            const recoil = Math.sin(animFrame * 0.15) * 1.5;

            // Thân
            ctx.beginPath();
            ctx.moveTo(0, 10);
            ctx.quadraticCurveTo(5, 25, 0, 35);
            ctx.strokeStyle = '#2e7d32';
            ctx.lineWidth = 6;
            ctx.stroke();

            // Lá
            ctx.fillStyle = '#388e3c';
            ctx.beginPath(); ctx.ellipse(-12, 30, 12, 6, -0.2, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.ellipse(12, 30, 12, 6, 0.2, 0, Math.PI * 2); ctx.fill();

            // Đầu Cây
            ctx.fillStyle = '#4caf50';
            ctx.beginPath();
            ctx.arc(-2 + recoil, -6, 16, 0, Math.PI * 2);
            ctx.fill();

            // Nòng bắn (Snout)
            ctx.beginPath();
            ctx.ellipse(12 + recoil, -6, 10, 8, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = '#1b5e20';
            ctx.beginPath();
            ctx.ellipse(16 + recoil, -6, 4, 7, 0, 0, Math.PI * 2);
            ctx.fill();

            // Mắt
            ctx.fillStyle = '#000';
            ctx.beginPath(); ctx.arc(2 + recoil, -10, 2.5, 0, Math.PI * 2); ctx.fill();

            ctx.restore();
        }

        // Vẽ Zombie
        function drawZombie(x, y, hp, maxHp, animFrame) {
            ctx.save();
            ctx.translate(x, y);

            const walkWobble = Math.sin(animFrame * 0.1) * 3;

            // Thân Zombie
            ctx.fillStyle = '#4e342e'; // Áo khoác nâu
            ctx.fillRect(-10, -10 + walkWobble, 20, 30);

            // Quần
            ctx.fillStyle = '#1a237e';
            ctx.fillRect(-9, 20 + walkWobble, 8, 18);
            ctx.fillRect(1, 20 + walkWobble, 8, 18);

            // Đầu
            ctx.fillStyle = '#81c784'; // Da xanh xám
            ctx.beginPath();
            ctx.arc(0, -22 + walkWobble, 14, 0, Math.PI * 2);
            ctx.fill();

            // Mắt đỏ & Răng
            ctx.fillStyle = '#d50000';
            ctx.beginPath(); ctx.arc(-4, -24 + walkWobble, 3, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = '#ffffff';
            ctx.beginPath(); ctx.arc(4, -24 + walkWobble, 2, 0, Math.PI * 2); ctx.fill();

            // Cánh tay giơ ra trước
            ctx.fillStyle = '#81c784';
            ctx.fillRect(-18, -6 + walkWobble, 14, 6);

            // Thanh máu Zombie
            if (hp < maxHp) {
                ctx.fillStyle = '#f44336';
                ctx.fillRect(-15, -42, 30, 4);
                ctx.fillStyle = '#4caf50';
                ctx.fillRect(-15, -42, 30 * Math.max(0, hp / maxHp), 4);
            }

            ctx.restore();
        }

        // Vẽ Mặt Trời
        function drawSun(x, y, animFrame) {
            ctx.save();
            ctx.translate(x, y);

            const rot = animFrame * 0.03;

            ctx.fillStyle = '#ffeb3b';
            ctx.beginPath();
            ctx.arc(0, 0, 15, 0, Math.PI * 2);
            ctx.fill();

            // Tia nắng xung quanh
            ctx.strokeStyle = '#fbc02d';
            ctx.lineWidth = 3;
            for (let i = 0; i < 8; i++) {
                const angle = (i * Math.PI * 2) / 8 + rot;
                ctx.beginPath();
                ctx.moveTo(Math.cos(angle) * 16, Math.sin(angle) * 16);
                ctx.lineTo(Math.cos(angle) * 23, Math.sin(angle) * 23);
                ctx.stroke();
            }

            ctx.restore();
        }

        function drawUI() {
            // Thanh hạt giống chính
            ctx.fillStyle = '#2b170c';
            ctx.fillRect(0, 0, canvas.width, OFFSET_Y);
            ctx.strokeStyle = '#4a2a18';
            ctx.lineWidth = 3;
            ctx.strokeRect(0, 0, canvas.width, OFFSET_Y);

            // Khung Mặt Trời
            ctx.fillStyle = '#140b05';
            ctx.fillRect(15, 15, 100, 70);
            ctx.strokeStyle = '#fbc02d';
            ctx.lineWidth = 2;
            ctx.strokeRect(15, 15, 100, 70);

            drawSun(38, 50, frameCount);

            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 20px sans-serif';
            ctx.fillText(suns, 62, 57);

            // Thẻ Cây Sunflower
            drawCard('sunflower', 130, 15, 'Sunflower', 50, '🌻');
            // Thẻ Cây Peashooter
            drawCard('peashooter', 240, 15, 'Peashooter', 100, '🫛');

            // Điểm số / Kills
            ctx.fillStyle = '#81c784';
            ctx.font = 'bold 18px sans-serif';
            ctx.fillText(`Zombies diệt: ${score}`, canvas.width - 200, 55);
        }

        function drawCard(type, x, y, name, cost, icon) {
            const canAfford = suns >= cost;
            const isSelected = selectedPlant === type;

            ctx.fillStyle = isSelected ? '#388e3c' : (canAfford ? '#3b2518' : '#1e130c');
            ctx.fillRect(x, y, 95, 70);
            ctx.strokeStyle = isSelected ? '#76ff03' : '#5a3d28';
            ctx.lineWidth = isSelected ? 3 : 1.5;
            ctx.strokeRect(x, y, 95, 70);

            ctx.font = '26px sans-serif';
            ctx.fillText(icon, x + 10, y + 42);
            ctx.font = 'bold 14px sans-serif';
            ctx.fillStyle = canAfford ? '#ffeb3b' : '#777777';
            ctx.fillText(`${cost}☀️`, x + 48, y + 42);
        }

        function drawLawn() {
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    const x = OFFSET_X + c * CELL_W;
                    const y = OFFSET_Y + r * CELL_H;

                    // Vẽ caro xanh cỏ
                    ctx.fillStyle = (r + c) % 2 === 0 ? '#43a047' : '#388e3c';
                    ctx.fillRect(x, y, CELL_W, CELL_H);
                    ctx.strokeStyle = 'rgba(0,0,0,0.06)';
                    ctx.strokeRect(x, y, CELL_W, CELL_H);
                }
            }

            // Vùng nguy hiểm bên trái (Đường đỏ)
            ctx.fillStyle = 'rgba(211, 47, 47, 0.3)';
            ctx.fillRect(0, OFFSET_Y, OFFSET_X, ROWS * CELL_H);
            ctx.fillStyle = '#ef5350';
            ctx.font = 'bold 14px sans-serif';
            ctx.fillText('NHA CUA BAN', 20, OFFSET_Y + (ROWS * CELL_H) / 2);
        }

        class Plant {
            constructor(r, c, type) {
                this.r = r;
                this.c = c;
                this.x = OFFSET_X + c * CELL_W + CELL_W / 2;
                this.y = OFFSET_Y + r * CELL_H + CELL_H / 2;
                this.type = type;
                this.hp = 100;
                this.timer = 0;
            }

            update() {
                this.timer++;

                // Sunflower tạo Sun mỗi 7.5 giây
                if (this.type === 'sunflower' && this.timer % 380 === 0) {
                    fallingSuns.push({
                        x: this.x + (Math.random() * 20 - 10),
                        y: this.y - 10,
                        targetY: this.y + 20,
                        timer: 0
                    });
                }

                // Peashooter bắn đạn mỗi 2 giây nếu có Zombie cùng hàng
                if (this.type === 'peashooter' && this.timer % 110 === 0) {
                    const hasZombie = zombies.some(z => z.r === this.r && z.x > this.x);
                    if (hasZombie) {
                        peas.push({
                            x: this.x + 20,
                            y: this.y - 10,
                            r: this.r,
                            damage: 25
                        });
                    }
                }
            }

            draw() {
                if (this.type === 'sunflower') drawSunflower(this.x, this.y, frameCount);
                else if (this.type === 'peashooter') drawPeashooter(this.x, this.y, frameCount);
            }
        }

        class Zombie {
            constructor(r) {
                this.r = r;
                this.x = canvas.width + 20;
                this.y = OFFSET_Y + r * CELL_H + CELL_H / 2;
                this.hp = 100;
                this.maxHp = 100;
                this.speed = 0.35 + Math.random() * 0.15;
            }

            update() {
                let eating = false;
                const cellC = Math.floor((this.x - OFFSET_X) / CELL_W);
                
                if (cellC >= 0 && cellC < COLS) {
                    const plant = grid[this.r][cellC];
                    if (plant && Math.abs(plant.x - this.x) < 25) {
                        eating = true;
                        plant.hp -= 0.6; // Cắn cây
                    }
                }

                if (!eating) {
                    this.x -= this.speed;
                }

                // Thua game nếu Zombie chạm vào khu vực nhà bên trái
                if (this.x <= OFFSET_X - 10) {
                    gameOver = true;
                }
            }

            draw() {
                drawZombie(this.x, this.y, this.hp, this.maxHp, frameCount);
            }
        }

        let zombieTimer = 0;
        let sunTimer = 0;

        function update() {
            if (gameOver) return;

            frameCount++;

            // 1. Sinh Mặt Trời tự nhiên từ trên trời
            sunTimer++;
            if (sunTimer % 240 === 0) {
                fallingSuns.push({
                    x: OFFSET_X + Math.random() * (COLS * CELL_W - 40),
                    y: OFFSET_Y - 20,
                    targetY: OFFSET_Y + 40 + Math.random() * (ROWS * CELL_H - 80),
                    timer: 0
                });
            }

            fallingSuns.forEach(s => {
                if (s.y < s.targetY) s.y += 1.5;
                s.timer++;
            });
            fallingSuns = fallingSuns.filter(s => s.timer < 500);

            // 2. Sinh Zombie định kỳ
            zombieTimer++;
            if (zombieTimer > 300) {
                zombieTimer = 0;
                const randomRow = Math.floor(Math.random() * ROWS);
                zombies.push(new Zombie(randomRow));
            }

            // 3. Cập nhật Cây & Dọn dẹp cây bị ăn hết máu
            plants.forEach(p => p.update());
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    if (grid[r][c] && grid[r][c].hp <= 0) {
                        grid[r][c] = null;
                    }
                }
            }
            plants = plants.filter(p => p.hp > 0);

            // 4. Cập nhật Đạn Đậu & Va chạm với Zombie
            peas.forEach(p => p.x += 6);
            peas.forEach(p => {
                zombies.forEach(z => {
                    if (z.r === p.r && Math.abs(z.x - p.x) < 20) {
                        z.hp -= p.damage;
                        p.hit = true;
                        
                        // Particle hiệu ứng trúng đạn
                        for (let i = 0; i < 4; i++) {
                            particles.push({
                                x: p.x, y: p.y,
                                vx: (Math.random() - 0.5) * 4,
                                vy: (Math.random() - 0.5) * 4,
                                life: 15,
                                color: '#76ff03'
                            });
                        }
                    }
                });
            });
            peas = peas.filter(p => !p.hit && p.x < canvas.width);

            // 5. Cập nhật Zombie & Xóa Zombie chết
            zombies.forEach(z => z.update());
            const initialCount = zombies.length;
            zombies = zombies.filter(z => z.hp > 0);
            score += (initialCount - zombies.length);

            // 6. Cập nhật Particles
            particles.forEach(pt => {
                pt.x += pt.vx;
                pt.y += pt.vy;
                pt.life--;
            });
            particles = particles.filter(pt => pt.life > 0);
        }

        function render() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            drawLawn();
            
            // Draw Plants
            plants.forEach(p => p.draw());

            // Draw Peas
            ctx.fillStyle = '#76ff03';
            peas.forEach(p => {
                ctx.beginPath();
                ctx.arc(p.x, p.y, 7, 0, Math.PI * 2);
                ctx.fill();
                ctx.strokeStyle = '#2e7d32';
                ctx.stroke();
            });

            // Draw Zombies
            zombies.forEach(z => z.draw());

            // Draw Suns
            fallingSuns.forEach(s => drawSun(s.x, s.y, frameCount));

            // Draw Particles
            particles.forEach(pt => {
                ctx.fillStyle = pt.color;
                ctx.fillRect(pt.x, pt.y, 3, 3);
            });

            // Draw UI
            drawUI();

            // Màn hình Thua Game (Game Over)
            if (gameOver) {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#f44336';
                ctx.font = 'bold 44px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('ZOMBIES ATE YOUR BRAINS!', canvas.width / 2, canvas.height / 2 - 20);

                ctx.fillStyle = '#ffffff';
                ctx.font = '20px sans-serif';
                ctx.fillText(`Bạn đã diệt được: ${score} Zombie`, canvas.width / 2, canvas.height / 2 + 30);
                ctx.fillText('Nhấp chuột vào màn hình để chơi lại', canvas.width / 2, canvas.height / 2 + 70);
                ctx.textAlign = 'left';
            }
        }

        function gameLoop() {
            update();
            render();
            requestAnimationFrame(gameLoop);
        }

        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            if (gameOver) {
                location.reload();
                return;
            }

            // 1. Nhặt Mặt Trời khi nhấp chuột
            for (let i = fallingSuns.length - 1; i >= 0; i--) {
                const s = fallingSuns[i];
                if (Math.hypot(s.x - mouseX, s.y - mouseY) < 30) {
                    suns += 25;
                    fallingSuns.splice(i, 1);

                    // Particle hiệu ứng thu thập Sun
                    for (let p = 0; p < 6; p++) {
                        particles.push({
                            x: mouseX, y: mouseY,
                            vx: (Math.random() - 0.5) * 5,
                            vy: (Math.random() - 0.5) * 5,
                            life: 20,
                            color: '#ffeb3b'
                        });
                    }
                    return;
                }
            }

            // 2. Chọn Thẻ Cây trên Thanh UI
            if (mouseY < OFFSET_Y) {
                if (mouseX >= 130 && mouseX <= 225) {
                    if (suns >= 50) selectedPlant = (selectedPlant === 'sunflower') ? null : 'sunflower';
                } else if (mouseX >= 240 && mouseX <= 335) {
                    if (suns >= 100) selectedPlant = (selectedPlant === 'peashooter') ? null : 'peashooter';
                }
                return;
            }

            // 3. Trồng cây vào ô cờ
            if (selectedPlant && mouseX >= OFFSET_X && mouseY >= OFFSET_Y) {
                const c = Math.floor((mouseX - OFFSET_X) / CELL_W);
                const r = Math.floor((mouseY - OFFSET_Y) / CELL_H);

                if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
                    if (!grid[r][c]) {
                        const cost = PLANT_TYPES[selectedPlant].cost;
                        if (suns >= cost) {
                            suns -= cost;
                            const newPlant = new Plant(r, c, selectedPlant);
                            grid[r][c] = newPlant;
                            plants.push(newPlant);
                            selectedPlant = null; // Trồng xong hủy chọn
                        }
                    }
                }
            }
        });

        // Bắt đầu Vòng lặp Game
        gameLoop();
    </script>
</body>
</html>
"""

components.html(pvz_game_html, height=600, scrolling=False)

with st.expander("📖 Hướng dẫn chơi & Quy tắc trò chơi"):
    st.write("""
    1. **Mục tiêu:** Bảo vệ ngôi nhà của bạn (phía bên trái) khỏi bầy Zombie tràn qua từ phía bên phải.
    2. **Mặt trời (Sun ☀️):** Thu thập các quả cầu ánh nắng rơi xuống hoặc được tạo ra bởi **Sunflower** (nhấp chuột vào để nhặt, mỗi quả cộng **+25 Sun**).
    3. **Trồng cây:**
       * 🌻 **Sunflower (50 Sun):** Sinh ánh nắng định kỳ.
       * 🫛 **Peashooter (100 Sun):** Bắn đạn đậu xanh để tiêu diệt Zombie trên cùng hàng.
    4. **Điều kiện Thua:** Khi có bất kỳ Zombie nào tiến vào khu vực bên trái bàn cờ (vùng màu đỏ), trò chơi sẽ kết thúc!
    """)