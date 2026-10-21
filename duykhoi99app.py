import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Plants vs Zombies: Classic Single Player",
    page_icon="🌻",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0c180c; color: #ffffff; }
    header, footer { visibility: hidden; }
    h1 { color: #76ff03 !important; font-family: 'Trebuchet MS', sans-serif; text-align: center; margin-bottom: 2px; text-shadow: 2px 2px #000; }
    p { text-align: center; color: #c8e6c9; font-family: sans-serif; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🌻 PLANTS VS. ZOMBIES: CLASSIC DAY LEVEL 🧟")
st.markdown("Bản tái hiện chuẩn xác giao diện Day Level gốc: Thanh Seed Bank gỗ, 5 xe cắt cỏ, đạn đậu có bóng râm và thanh tiến trình góc dưới bên phải!")

# Mã HTML & Canvas Engine 2D
pvz_classic_html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body { background: #060d06; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; }
        
        #game-container {
            position: relative;
            width: 960px;
            height: 580px;
            border: 4px solid #3d2514;
            border-radius: 8px;
            box-shadow: 0 0 35px rgba(0,0,0,0.9);
            background: #111;
        }
        
        canvas { display: block; cursor: pointer; }
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="pvzCanvas" width="960" height="580"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('pvzCanvas');
        const ctx = canvas.getContext('2d');

        const ROWS = 5;
        const COLS = 9;
        const CELL_W = 82;
        const CELL_H = 84;
        const OFFSET_X = 140; // Lề trái cho 5 xe cắt cỏ
        const OFFSET_Y = 95;  // Lề trên cho Seed Bank

        let suns = 350; // Khởi đầu 350 Sun như trong hình
        let gameState = 'PLAYING';
        let selectedTool = null;

        let totalZombiesInLevel = 15;
        let spawnedZombiesCount = 0;
        let killedZombiesCount = 0;

        // Danh sách thẻ cây chuẩn như hình ảnh
        const SEED_CARDS = [
            { id: 'peashooter', name: 'Peashooter', cost: 100, icon: '🫛', cooldown: 0, maxCooldown: 100 },
            { id: 'sunflower',  name: 'Sunflower',  cost: 50,  icon: '🌻', cooldown: 0, maxCooldown: 100 },
            { id: 'cherry',     name: 'Cherry Bomb',cost: 150, icon: '🍒', cooldown: 180, maxCooldown: 300 }, // Đang cooldown như ảnh
            { id: 'repeater',   name: 'Repeater',   cost: 200, icon: '🫛🫛', cooldown: 0, maxCooldown: 150 }
        ];

        let grid = Array(ROWS).fill(null).map(() => Array(COLS).fill(null));
        
        // 5 Máy cắt cỏ bên trái bãi cỏ
        let lawnMowers = [];
        for (let r = 0; r < ROWS; r++) {
            lawnMowers.push({ row: r, x: OFFSET_X - 48, y: OFFSET_Y + r * CELL_H + 22, active: false, used: false });
        }

        let plants = [];
        let zombies = [];
        let peas = [];
        let fallingSuns = [];
        let explosions = [];

        // Trồng sẵn một số cây mặc định cho giống hình ảnh gốc
        function setupInitialBoard() {
            const initialPlants = [
                {r:0, c:0, type:'sunflower'}, {r:0, c:1, type:'peashooter'},
                {r:1, c:0, type:'sunflower'}, {r:1, c:1, type:'peashooter'},
                {r:2, c:0, type:'peashooter'}, {r:2, c:1, type:'sunflower'}, {r:2, c:2, type:'sunflower'},
                {r:3, c:0, type:'sunflower'}, {r:3, c:1, type:'peashooter'}, {r:3, c:2, type:'peashooter'},
                {r:4, c:0, type:'peashooter'}, {r:4, c:1, type:'sunflower'}, {r:4, c:2, type:'peashooter'}
            ];

            initialPlants.forEach(p => {
                const plant = new Plant(p.r, p.c, p.type);
                grid[p.r][p.c] = plant;
                plants.push(plant);
            });
        }

        // --- DRAW TOP SEED BANK UI ---
        function drawUI() {
            // Thanh gỗ khung chính
            ctx.fillStyle = '#2b170c';
            ctx.fillRect(0, 0, canvas.width - 100, OFFSET_Y);
            ctx.strokeStyle = '#4a2a18';
            ctx.lineWidth = 3;
            ctx.strokeRect(0, 0, canvas.width - 100, OFFSET_Y);

            // Khung Mặt Trời bên trái
            ctx.fillStyle = '#140b05';
            ctx.fillRect(12, 12, 90, 68);
            ctx.strokeStyle = '#d4af37';
            ctx.lineWidth = 2;
            ctx.strokeRect(12, 12, 90, 68);

            ctx.font = '24px sans-serif';
            ctx.fillText('☀️', 18, 54);
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 20px sans-serif';
            ctx.fillText(suns, 50, 52);

            // Các thẻ cây
            SEED_CARDS.forEach((card, idx) => {
                const x = 112 + idx * 82;
                const y = 10;
                const w = 76;
                const h = 72;

                const canAfford = suns >= card.cost && card.cooldown === 0;
                ctx.fillStyle = selectedTool === card.id ? '#43a047' : (canAfford ? '#3b2518' : '#1e130c');
                ctx.fillRect(x, y, w, h);
                ctx.strokeStyle = selectedTool === card.id ? '#76ff03' : '#5a3d28';
                ctx.lineWidth = selectedTool === card.id ? 3 : 1.5;
                ctx.strokeRect(x, y, w, h);

                ctx.font = '26px sans-serif';
                ctx.fillText(card.icon, x + 6, y + 45);
                ctx.font = 'bold 13px sans-serif';
                ctx.fillStyle = canAfford ? '#ffffff' : '#777777';
                ctx.fillText(card.cost, x + 38, y + 42);

                // Lớp Cooldown phủ mờ như thẻ Cherry Bomb trong hình
                if (card.cooldown > 0) {
                    const cdRatio = card.cooldown / card.maxCooldown;
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.65)';
                    ctx.fillRect(x, y, w, h * cdRatio);
                }
            });

            // Khung Xẻng bên phải góc trên
            const shovelX = canvas.width - 85;
            ctx.fillStyle = '#2b170c';
            ctx.fillRect(shovelX, 10, 70, 72);
            ctx.strokeStyle = selectedTool === 'shovel' ? '#ff3232' : '#5a3d28';
            ctx.lineWidth = selectedTool === 'shovel' ? 3 : 2;
            ctx.strokeRect(shovelX, 10, 70, 72);
            ctx.font = '32px sans-serif';
            ctx.fillText('🧹', shovelX + 16, 56);

            // --- BOTTOM-RIGHT PROGRESS BAR (Thanh Tiến Trình Zombie) ---
            const progW = 220;
            const progH = 16;
            const progX = canvas.width - progW - 20;
            const progY = canvas.height - 32;

            // Khung thanh tiến trình
            ctx.fillStyle = '#1c281c';
            ctx.fillRect(progX, progY, progW, progH);
            ctx.strokeStyle = '#558b2f';
            ctx.lineWidth = 2;
            ctx.strokeRect(progX, progY, progW, progH);

            // Phần trăm tiến độ
            const ratio = Math.min(1, killedZombiesCount / totalZombiesInLevel);
            ctx.fillStyle = '#4caf50';
            ctx.fillRect(progX + progW * (1 - ratio), progY, progW * ratio, progH);

            // Đầu Zombie di chuyển từ phải qua trái trên thanh tiến trình
            const headX = progX + progW * (1 - ratio) - 10;
            ctx.font = '18px sans-serif';
            ctx.fillText('🧟', headX, progY + 15);
            ctx.fillText('🚩', progX - 5, progY + 14);
        }

        // --- DRAW LAWN GRID ---
        function drawLawn() {
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    const x = OFFSET_X + c * CELL_W;
                    const y = OFFSET_Y + r * CELL_H;
                    ctx.fillStyle = (r + c) % 2 === 0 ? '#3d9432' : '#46a33a';
                    ctx.fillRect(x, y, CELL_W, CELL_H);
                    ctx.strokeStyle = 'rgba(0,0,0,0.05)';
                    ctx.strokeRect(x, y, CELL_W, CELL_H);
                }
            }

            // Vẽ 5 Máy cắt cỏ
            lawnMowers.forEach(lm => {
                if (!lm.used) {
                    ctx.font = '32px sans-serif';
                    ctx.fillText('🚜', lm.x, lm.y + 25);
                }
            });
        }

        // --- CLASSES ---
        class Plant {
            constructor(r, c, type) {
                this.r = r;
                this.c = c;
                this.x = OFFSET_X + c * CELL_W + 15;
                this.y = OFFSET_Y + r * CELL_H + 60;
                this.type = type;
                this.hp = 100;
                this.timer = Math.floor(Math.random() * 50);
            }

            update() {
                this.timer++;
                if (this.type === 'sunflower' && this.timer % 340 === 0) {
                    fallingSuns.push({ x: this.x, y: this.y - 30, targetY: this.y + 10, timer: 0 });
                }

                if ((this.type === 'peashooter' || this.type === 'repeater') && this.timer % 90 === 0) {
                    const hasZombie = zombies.some(z => z.r === this.r && z.x > this.x);
                    if (hasZombie) {
                        peas.push({ x: this.x + 28, y: this.y - 20, r: this.r, damage: 20 });
                        if (this.type === 'repeater') {
                            setTimeout(() => {
                                peas.push({ x: this.x + 28, y: this.y - 20, r: this.r, damage: 20 });
                            }, 150);
                        }
                    }
                }
            }

            draw() {
                ctx.font = '42px sans-serif';
                let icon = '🌻';
                if (this.type === 'peashooter') icon = '🫛';
                if (this.type === 'repeater') icon = '🫛';
                ctx.fillText(icon, this.x - 5, this.y);
            }
        }

        class Zombie {
            constructor(r) {
                this.r = r;
                this.x = canvas.width + 10;
                this.y = OFFSET_Y + r * CELL_H + 62;
                this.hp = 100;
                this.maxHp = 100;
                this.speed = 0.32;
                this.dying = false;
                this.dyingTimer = 0;
            }

            update() {
                if (this.dying) {
                    this.dyingTimer++;
                    return;
                }

                let eating = false;
                const cellC = Math.floor((this.x - OFFSET_X) / CELL_W);
                if (cellC >= 0 && cellC < COLS) {
                    const plant = grid[this.r][cellC];
                    if (plant && Math.abs(plant.x - this.x) < 25) {
                        eating = true;
                        plant.hp -= 0.8;
                    }
                }

                if (!eating) this.x -= this.speed;

                if (this.x < OFFSET_X - 10) {
                    const lm = lawnMowers[this.r];
                    if (lm && !lm.used) {
                        lm.active = true;
                    } else if (this.x < OFFSET_X - 45) {
                        gameState = 'GAME_OVER';
                    }
                }
            }

            draw() {
                ctx.font = '44px sans-serif';
                if (this.dying) {
                    // Hiệu ứng Zombie ngã gục như trong ảnh
                    ctx.fillText('💀', this.x, this.y);
                } else {
                    ctx.fillText('🧟', this.x, this.y);

                    if (this.hp < this.maxHp) {
                        ctx.fillStyle = '#f44336';
                        ctx.fillRect(this.x + 5, this.y - 52, 32, 4);
                        ctx.fillStyle = '#4caf50';
                        ctx.fillRect(this.x + 5, this.y - 52, 32 * Math.max(0, this.hp / this.maxHp), 4);
                    }
                }
            }
        }

        let zombieSpawnTimer = 0;

        function update() {
            if (gameState !== 'PLAYING') return;

            // Giảm cooldown thẻ cây
            SEED_CARDS.forEach(c => {
                if (c.cooldown > 0) c.cooldown--;
            });

            // Mặt trời rơi tự nhiên
            if (Math.random() < 0.005) {
                fallingSuns.push({
                    x: OFFSET_X + Math.random() * (COLS * CELL_W - 40),
                    y: OFFSET_Y - 20,
                    targetY: OFFSET_Y + Math.floor(Math.random() * ROWS) * CELL_H + 40,
                    timer: 0
                });
            }

            fallingSuns.forEach(s => {
                if (s.y < s.targetY) s.y += 1.4;
                s.timer++;
            });
            fallingSuns = fallingSuns.filter(s => s.timer < 500);

            // Spawn Zombie
            zombieSpawnTimer++;
            if (zombieSpawnTimer > 260 && spawnedZombiesCount < totalZombiesInLevel) {
                zombieSpawnTimer = 0;
                const randomRow = Math.floor(Math.random() * ROWS);
                zombies.push(new Zombie(randomRow));
                spawnedZombiesCount++;
            }

            plants.forEach(p => p.update());
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    if (grid[r][c] && grid[r][c].hp <= 0) grid[r][c] = null;
                }
            }
            plants = plants.filter(p => p.hp > 0);

            // Cập nhật vị trí Đạn & Bóng râm
            peas.forEach(p => p.x += 6.5);
            peas.forEach(p => {
                zombies.forEach(z => {
                    if (!z.dying && z.r === p.r && Math.abs(z.x - p.x) < 22) {
                        z.hp -= p.damage;
                        if (z.hp <= 0) {
                            z.dying = true; // Kích hoạt animation gục ngã
                        }
                        p.hit = true;
                    }
                });
            });
            peas = peas.filter(p => !p.hit && p.x < canvas.width);

            // Xe cắt cỏ
            lawnMowers.forEach(lm => {
                if (lm.active) {
                    lm.x += 8.5;
                    zombies.forEach(z => {
                        if (z.r === lm.row && Math.abs(z.x - lm.x) < 35) z.hp = 0;
                    });
                    if (lm.x > canvas.width) {
                        lm.active = false;
                        lm.used = true;
                    }
                }
            });

            zombies.forEach(z => z.update());
            
            // Lọc các Zombie chết hoàn toàn
            const activeZombies = zombies.filter(z => !z.dying || z.dyingTimer < 40);
            killedZombiesCount += (zombies.length - activeZombies.length);
            zombies = activeZombies;
        }

        function render() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            drawLawn();
            plants.forEach(p => p.draw());

            // Vẽ Đạn Đậu Xanh & Bóng râm đạn bên dưới (Giống ảnh gốc)
            peas.forEach(p => {
                // Bóng râm đạn
                ctx.fillStyle = 'rgba(0,0,0,0.25)';
                ctx.beginPath();
                ctx.ellipse(p.x, p.y + 18, 7, 3, 0, 0, Math.PI * 2);
                ctx.fill();

                // Viên đạn xanh rực
                ctx.beginPath();
                ctx.arc(p.x, p.y, 7, 0, Math.PI * 2);
                ctx.fillStyle = '#76ff03';
                ctx.fill();
                ctx.strokeStyle = '#2e7d32';
                ctx.stroke();
            });

            zombies.forEach(z => z.draw());

            fallingSuns.forEach(s => {
                ctx.font = '32px sans-serif';
                ctx.fillText('☀️', s.x, s.y);
            });

            drawUI();

            if (gameState === 'GAME_OVER') {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.88)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                ctx.fillStyle = '#f44336';
                ctx.font = 'bold 46px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('THE ZOMBIES ATE YOUR BRAINS!', canvas.width / 2, canvas.height / 2);
                ctx.font = '20px sans-serif';
                ctx.fillStyle = '#ffffff';
                ctx.fillText('Nhấp chuột vào màn hình để chơi lại', canvas.width / 2, canvas.height / 2 + 50);
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

            if (gameState === 'GAME_OVER') {
                location.reload();
                return;
            }

            // Nhặt Sun
            for (let i = fallingSuns.length - 1; i >= 0; i--) {
                const s = fallingSuns[i];
                if (Math.hypot(s.x + 15 - mouseX, s.y - 15 - mouseY) < 32) {
                    suns += 25;
                    fallingSuns.splice(i, 1);
                    return;
                }
            }

            // Tương tác Seed Bank
            if (mouseY < OFFSET_Y) {
                SEED_CARDS.forEach((card, idx) => {
                    const x = 112 + idx * 82;
                    if (mouseX >= x && mouseX <= x + 76) {
                        if (suns >= card.cost && card.cooldown === 0) {
                            selectedTool = (selectedTool === card.id) ? null : card.id;
                        }
                    }
                });

                const shovelX = canvas.width - 85;
                if (mouseX >= shovelX && mouseX <= shovelX + 70) {
                    selectedTool = (selectedTool === 'shovel') ? null : 'shovel';
                }
                return;
            }

            // Trồng cây
            if (selectedTool && mouseX >= OFFSET_X && mouseY >= OFFSET_Y) {
                const c = Math.floor((mouseX - OFFSET_X) / CELL_W);
                const r = Math.floor((mouseY - OFFSET_Y) / CELL_H);

                if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
                    if (selectedTool === 'shovel') {
                        if (grid[r][c]) {
                            grid[r][c] = null;
                            selectedTool = null;
                        }
                    } else if (!grid[r][c]) {
                        const card = SEED_CARDS.find(k => k.id === selectedTool);
                        if (card && suns >= card.cost) {
                            suns -= card.cost;
                            card.cooldown = card.maxCooldown;
                            const plant = new Plant(r, c, selectedTool);
                            grid[r][c] = plant;
                            plants.push(plant);
                            selectedTool = null;
                        }
                    }
                }
            }
        });

        setupInitialBoard();
        gameLoop();
    </script>
</body>
</html>
"""

# Khởi chạy ứng dụng Web trên Streamlit
components.html(pvz_classic_html, height=600, scrolling=False)
