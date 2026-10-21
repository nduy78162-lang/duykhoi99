import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Plants vs Zombies: Adventure Mode",
    page_icon="🌻",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0f1c0f; color: #ffffff; }
    header, footer { visibility: hidden; }
    h1 { color: #76ff03 !important; font-family: 'Trebuchet MS', sans-serif; text-align: center; margin-bottom: 2px; text-shadow: 2px 2px #000; }
    p { text-align: center; color: #a5d6a7; font-family: sans-serif; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🌻 PLANTS VS. ZOMBIES: ADVENTURE MODE 🧟")
st.markdown("Vượt qua từng Level từ 1-1 để mở rộng bãi cỏ, nhận cây mới và tiêu diệt đợt sóng Zombie khổng lồ!")

# Engine Game HTML5 / JS Canvas
pvz_adventure_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body { background: #081008; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; overflow: hidden; }
        
        #game-container {
            position: relative;
            width: 900px;
            height: 560px;
            border: 4px solid #3d2514;
            border-radius: 10px;
            box-shadow: 0 0 35px rgba(0,0,0,0.9);
            background: #111;
        }
        
        canvas { display: block; cursor: pointer; }
    </style>
</head>
<body>

    <div id="game-container">
        <canvas id="pvzCanvas" width="900" height="560"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('pvzCanvas');
        const ctx = canvas.getContext('2d');

        const ROWS = 5;
        const COLS = 9;
        const CELL_W = 80;
        const CELL_H = 82;
        const OFFSET_X = 140;
        const OFFSET_Y = 85;

        // --- HỆ THỐNG MÀN CHƠI (ADVENTURE LEVELS) ---
        const LEVELS_DATA = [
            {
                id: "1-1",
                name: "LEVEL 1-1",
                activeRows: [2], // Chỉ 1 làn ở giữa
                unlockedPlants: ['peashooter'],
                zombieQueue: ['normal', 'normal', 'normal', 'flag', 'normal'],
                reward: 'sunflower',
                rewardName: 'Sunflower',
                rewardIcon: '🌻',
                rewardDesc: 'Tạo thêm 25 Mặt Trời định kỳ!'
            },
            {
                id: "1-2",
                name: "LEVEL 1-2",
                activeRows: [1, 2, 3], // 3 làn cỏ
                unlockedPlants: ['peashooter', 'sunflower'],
                zombieQueue: ['normal', 'normal', 'conehead', 'normal', 'flag', 'normal', 'conehead'],
                reward: 'cherry',
                rewardName: 'Cherry Bomb',
                rewardIcon: '🍒',
                rewardDesc: 'Nổ tung tất cả Zombie trong diện tích 3x3!'
            },
            {
                id: "1-3",
                name: "LEVEL 1-3",
                activeRows: [0, 1, 2, 3, 4], // Full 5 làn cỏ
                unlockedPlants: ['peashooter', 'sunflower', 'cherry', 'wallnut'],
                zombieQueue: ['normal', 'conehead', 'normal', 'buckethead', 'flag', 'conehead', 'buckethead', 'normal'],
                reward: 'completed',
                rewardName: 'Trophy',
                rewardIcon: '🏆',
                rewardDesc: 'Chúc mừng bạn đã chinh phục toàn bộ Adventure Mode!'
            }
        ];

        let currentLevelIndex = 0;
        let currentLevel = LEVELS_DATA[currentLevelIndex];

        // Trạng thái Game
        let suns = 150;
        let gameState = 'PLAYING'; // 'PLAYING', 'LEVEL_WON', 'GAME_OVER'
        let selectedTool = null; // 'peashooter', 'sunflower', 'cherry', 'wallnut', 'shovel'
        
        let spawnedZombiesCount = 0;
        let totalZombiesInLevel = 0;
        let killedZombiesInLevel = 0;
        let hugeWaveTriggered = false;
        let hugeWaveBannerTimer = 0;

        let grid = Array(ROWS).fill(null).map(() => Array(COLS).fill(null));
        let lawnMowers = [];
        let plants = [];
        let zombies = [];
        let peas = [];
        let fallingSuns = [];
        let explosions = [];

        // Âm thanh giả lập qua Web Audio Synthesizer
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playAudio(type) {
            try {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain);
                gain.connect(audioCtx.destination);

                if (type === 'sun') {
                    osc.frequency.setValueAtTime(523, audioCtx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.15);
                    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
                    osc.start(); osc.stop(audioCtx.currentTime + 0.15);
                } else if (type === 'shoot') {
                    osc.frequency.setValueAtTime(320, audioCtx.currentTime);
                    osc.frequency.linearRampToValueAtTime(140, audioCtx.currentTime + 0.08);
                    gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
                    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);
                    osc.start(); osc.stop(audioCtx.currentTime + 0.08);
                } else if (type === 'boom') {
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(140, audioCtx.currentTime);
                    osc.frequency.linearRampToValueAtTime(25, audioCtx.currentTime + 0.4);
                    gain.gain.setValueAtTime(0.4, audioCtx.currentTime);
                    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);
                    osc.start(); osc.stop(audioCtx.currentTime + 0.4);
                } else if (type === 'hugewave') {
                    osc.type = 'square';
                    osc.frequency.setValueAtTime(180, audioCtx.currentTime);
                    osc.frequency.linearRampToValueAtTime(90, audioCtx.currentTime + 0.6);
                    gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
                    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.6);
                    osc.start(); osc.stop(audioCtx.currentTime + 0.6);
                }
            } catch(e) {}
        }

        function initLevel(levelIdx) {
            currentLevelIndex = levelIdx;
            currentLevel = LEVELS_DATA[currentLevelIndex];
            
            suns = 150;
            gameState = 'PLAYING';
            selectedTool = null;
            spawnedZombiesCount = 0;
            killedZombiesInLevel = 0;
            totalZombiesInLevel = currentLevel.zombieQueue.length;
            hugeWaveTriggered = false;
            hugeWaveBannerTimer = 0;

            grid = Array(ROWS).fill(null).map(() => Array(COLS).fill(null));
            plants = [];
            zombies = [];
            peas = [];
            fallingSuns = [];
            explosions = [];

            // Máy cắt cỏ chỉ đặt ở các hàng cỏ hoạt động
            lawnMowers = [];
            for (let r = 0; r < ROWS; r++) {
                if (currentLevel.activeRows.includes(r)) {
                    lawnMowers.push({ row: r, x: OFFSET_X - 45, y: OFFSET_Y + r * CELL_H + 20, active: false, used: false });
                }
            }
        }

        // --- CÁC THẺ CÂY CÓ THỂ MỞ KHÓA ---
        const ALL_PLANTS = {
            'peashooter': { id: 'peashooter', name: 'Peashooter', cost: 100, icon: '🫛' },
            'sunflower':  { id: 'sunflower',  name: 'Sunflower',  cost: 50,  icon: '🌻' },
            'wallnut':    { id: 'wallnut',    name: 'Wall-nut',   cost: 50,  icon: '🧱' },
            'cherry':     { id: 'cherry',     name: 'Cherry Bomb',cost: 150, icon: '🍒' }
        };

        // --- RENDER GIAO DIỆN CHÍNH ---
        function drawUI() {
            // Thanh hạt giống (Seed Bank)
            ctx.fillStyle = '#2b1810';
            ctx.fillRect(0, 0, canvas.width, OFFSET_Y);
            ctx.strokeStyle = '#5a3d28';
            ctx.lineWidth = 3;
            ctx.strokeRect(0, 0, canvas.width, OFFSET_Y);

            // Ô Mặt Trời
            ctx.fillStyle = '#170c06';
            ctx.fillRect(12, 12, 95, 60);
            ctx.strokeRect(12, 12, 95, 60);
            ctx.font = '24px sans-serif';
            ctx.fillText('☀️', 18, 49);
            ctx.fillStyle = '#ffeb3b';
            ctx.font = 'bold 19px sans-serif';
            ctx.fillText(suns, 54, 48);

            // Thẻ cây đã mở khóa
            let cardIndex = 0;
            currentLevel.unlockedPlants.forEach(pId => {
                const card = ALL_PLANTS[pId];
                const x = 120 + cardIndex * 95;
                const y = 10;
                const w = 88;
                const h = 64;

                const canAfford = suns >= card.cost;
                ctx.fillStyle = selectedTool === card.id ? '#388e3c' : (canAfford ? '#3b281a' : '#21150e');
                ctx.fillRect(x, y, w, h);
                ctx.strokeStyle = selectedTool === card.id ? '#76ff03' : '#5a3d28';
                ctx.lineWidth = selectedTool === card.id ? 3 : 1.5;
                ctx.strokeRect(x, y, w, h);

                ctx.font = '24px sans-serif';
                ctx.fillText(card.icon, x + 6, y + 42);
                ctx.font = 'bold 13px sans-serif';
                ctx.fillStyle = canAfford ? '#ffeb3b' : '#777777';
                ctx.fillText(card.cost + '☀️', x + 40, y + 40);

                cardIndex++;
            });

            // Ô Xẻng Nhổ Cây (Shovel) - Mở khóa từ Level 1-3
            if (currentLevel.unlockedPlants.includes('wallnut')) {
                const shovelX = 120 + cardIndex * 95 + 10;
                ctx.fillStyle = selectedTool === 'shovel' ? '#c62828' : '#3b281a';
                ctx.fillRect(shovelX, 10, 60, 64);
                ctx.strokeStyle = selectedTool === 'shovel' ? '#ff5252' : '#5a3d28';
                ctx.strokeRect(shovelX, 10, 60, 64);
                ctx.font = '30px sans-serif';
                ctx.fillText('🧹', shovelX + 12, 52);
            }

            // Thanh Tiến Trình Level (Level Progress Bar)
            const barW = 180;
            const barH = 18;
            const barX = canvas.width - barW - 25;
            const barY = 22;

            ctx.fillStyle = '#111';
            ctx.fillRect(barX, barY, barW, barH);
            ctx.strokeStyle = '#888';
            ctx.strokeRect(barX, barY, barW, barH);

            const progressRatio = Math.min(1, killedZombiesInLevel / totalZombiesInLevel);
            ctx.fillStyle = '#4caf50';
            ctx.fillRect(barX, barY, barW * progressRatio, barH);

            // Lá cờ báo Đợt sóng lớn
            ctx.font = '16px sans-serif';
            ctx.fillText('🚩', barX + barW * 0.75 - 8, barY + 15);

            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 14px sans-serif';
            ctx.fillText(currentLevel.name, barX + 35, barY + 36);
        }

        function drawLawn() {
            // Vẽ bãi cỏ hoặc đất dựa vào activeRows của màn hiện tại
            for (let r = 0; r < ROWS; r++) {
                const isActive = currentLevel.activeRows.includes(r);
                for (let c = 0; c < COLS; c++) {
                    const x = OFFSET_X + c * CELL_W;
                    const y = OFFSET_Y + r * CELL_H;

                    if (isActive) {
                        ctx.fillStyle = (r + c) % 2 === 0 ? '#43a047' : '#388e3c';
                    } else {
                        ctx.fillStyle = '#2d1f15'; // Đất trọc màu nâu xám cho hàng chưa mở
                    }
                    ctx.fillRect(x, y, CELL_W, CELL_H);
                    ctx.strokeStyle = 'rgba(0,0,0,0.08)';
                    ctx.strokeRect(x, y, CELL_W, CELL_H);
                }
            }

            // Máy cắt cỏ
            lawnMowers.forEach(lm => {
                if (!lm.used) {
                    ctx.font = '32px sans-serif';
                    ctx.fillText('🚜', lm.x, lm.y + 25);
                }
            });
        }

        // --- CÁC LỚP ĐỐI TƯỢNG (PLANTS, ZOMBIES) ---
        class Plant {
            constructor(r, c, type) {
                this.r = r;
                this.c = c;
                this.x = OFFSET_X + c * CELL_W + 15;
                this.y = OFFSET_Y + r * CELL_H + 58;
                this.type = type;
                this.hp = type === 'wallnut' ? 600 : 100;
                this.maxHp = this.hp;
                this.timer = 0;
            }

            update() {
                this.timer++;
                if (this.type === 'sunflower' && this.timer % 380 === 0) {
                    fallingSuns.push({ x: this.x, y: this.y - 30, targetY: this.y + 10, timer: 0 });
                }
                if (this.type === 'peashooter' && this.timer % 100 === 0) {
                    const hasZombie = zombies.some(z => z.r === this.r && z.x > this.x);
                    if (hasZombie) {
                        peas.push({ x: this.x + 28, y: this.y - 18, r: this.r, damage: 20 });
                        playAudio('shoot');
                    }
                }
                if (this.type === 'cherry' && this.timer === 50) {
                    playAudio('boom');
                    explosions.push({ x: this.x, y: this.y - 20, radius: 130, timer: 20 });
                    zombies.forEach(z => {
                        const dist = Math.hypot(z.x - this.x, (OFFSET_Y + z.r * CELL_H + 40) - this.y);
                        if (dist < 150) z.hp -= 500;
                    });
                    this.hp = 0;
                }
            }

            draw() {
                ctx.font = '40px sans-serif';
                let icon = ALL_PLANTS[this.type] ? ALL_PLANTS[this.type].icon : '🌻';
                ctx.fillText(icon, this.x - 5, this.y);

                if (this.type === 'wallnut' && this.hp < this.maxHp) {
                    ctx.fillStyle = '#f44336';
                    ctx.fillRect(this.x - 5, this.y - 52, 40, 5);
                    ctx.fillStyle = '#4caf50';
                    ctx.fillRect(this.x - 5, this.y - 52, 40 * (this.hp / this.maxHp), 5);
                }
            }
        }

        class Zombie {
            constructor(r, type = 'normal') {
                this.r = r;
                this.x = canvas.width + 10;
                this.y = OFFSET_Y + r * CELL_H + 60;
                this.type = type;
                this.speed = type === 'flag' ? 0.45 : 0.3;
                
                if (type === 'normal') this.hp = 100;
                else if (type === 'conehead') this.hp = 280;
                else if (type === 'buckethead') this.hp = 550;
                else if (type === 'flag') this.hp = 120;

                this.maxHp = this.hp;
            }

            update() {
                let eating = false;
                const cellC = Math.floor((this.x - OFFSET_X) / CELL_W);
                if (cellC >= 0 && cellC < COLS) {
                    const plant = grid[this.r][cellC];
                    if (plant && Math.abs(plant.x - this.x) < 25) {
                        eating = true;
                        plant.hp -= 0.7;
                    }
                }

                if (!eating) this.x -= this.speed;

                // Kiểm tra Máy Cắt Cỏ & Game Over
                if (this.x < OFFSET_X - 10) {
                    const lm = lawnMowers.find(m => m.row === this.r);
                    if (lm && !lm.used) {
                        lm.active = true;
                    } else if (this.x < OFFSET_X - 45) {
                        gameState = 'GAME_OVER';
                    }
                }
            }

            draw() {
                ctx.font = '42px sans-serif';
                let icon = '🧟';
                if (this.type === 'conehead') icon = '🗼🧟';
                else if (this.type === 'buckethead') icon = '🪣🧟';
                else if (this.type === 'flag') icon = '🚩🧟';

                ctx.fillText(icon, this.x, this.y);

                if (this.hp < this.maxHp) {
                    ctx.fillStyle = '#f44336';
                    ctx.fillRect(this.x + 5, this.y - 52, 32, 4);
                    ctx.fillStyle = '#4caf50';
                    ctx.fillRect(this.x + 5, this.y - 52, 32 * Math.max(0, this.hp / this.maxHp), 4);
                }
            }
        }

        let zombieTimer = 0;

        function update() {
            if (gameState !== 'PLAYING') return;

            // 1. Mặt trời tự nhiên rơi
            if (Math.random() < 0.004) {
                const randomRow = currentLevel.activeRows[Math.floor(Math.random() * currentLevel.activeRows.length)];
                fallingSuns.push({
                    x: OFFSET_X + Math.random() * (COLS * CELL_W - 40),
                    y: OFFSET_Y - 20,
                    targetY: OFFSET_Y + randomRow * CELL_H + 40,
                    timer: 0
                });
            }

            fallingSuns.forEach(s => {
                if (s.y < s.targetY) s.y += 1.4;
                s.timer++;
            });
            fallingSuns = fallingSuns.filter(s => s.timer < 500);

            // 2. Spawn Zombie theo đợt sóng của màn
            zombieTimer++;
            if (zombieTimer > 280 && spawnedZombiesCount < totalZombiesInLevel) {
                zombieTimer = 0;
                const zType = currentLevel.zombieQueue[spawnedZombiesCount];
                const activeR = currentLevel.activeRows;
                const randomRow = activeR[Math.floor(Math.random() * activeR.length)];

                // Kiểm tra kích hoạt Huge Wave
                if (zType === 'flag' && !hugeWaveTriggered) {
                    hugeWaveTriggered = true;
                    hugeWaveBannerTimer = 180;
                    playAudio('hugewave');
                }

                zombies.push(new Zombie(randomRow, zType));
                spawnedZombiesCount++;
            }

            // Update Cây & Xóa cây chết
            plants.forEach(p => p.update());
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    if (grid[r][c] && grid[r][c].hp <= 0) grid[r][c] = null;
                }
            }
            plants = plants.filter(p => p.hp > 0);

            // Update Đậu (Peas)
            peas.forEach(p => p.x += 6.5);
            peas.forEach(p => {
                zombies.forEach(z => {
                    if (z.r === p.r && Math.abs(z.x - p.x) < 22) {
                        z.hp -= p.damage;
                        p.hit = true;
                    }
                });
            });
            peas = peas.filter(p => !p.hit && p.x < canvas.width);

            // Update Máy Cắt Cỏ
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

            // Update Zombies
            zombies.forEach(z => z.update());
            const prevZCount = zombies.length;
            zombies = zombies.filter(z => z.hp > 0);
            killedZombiesInLevel += (prevZCount - zombies.length);

            // Kiểm tra Hoàn Thành Màn Chơi (Level Clear)
            if (spawnedZombiesCount >= totalZombiesInLevel && zombies.length === 0) {
                gameState = 'LEVEL_WON';
            }

            // Update Hiệu ứng nổ
            explosions.forEach(e => e.timer--);
            explosions = explosions.filter(e => e.timer > 0);

            if (hugeWaveBannerTimer > 0) hugeWaveBannerTimer--;
        }

        function render() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            drawLawn();
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

            zombies.forEach(z => z.draw());

            fallingSuns.forEach(s => {
                ctx.font = '32px sans-serif';
                ctx.fillText('☀️', s.x, s.y);
            });

            explosions.forEach(e => {
                ctx.fillStyle = 'rgba(255, 87, 34, 0.6)';
                ctx.beginPath();
                ctx.arc(e.x + 15, e.y + 15, e.radius, 0, Math.PI * 2);
                ctx.fill();
            });

            drawUI();

            // Banner thông báo Huge Wave
            if (hugeWaveBannerTimer > 0) {
                ctx.fillStyle = 'rgba(180, 0, 0, 0.85)';
                ctx.fillRect(0, canvas.height / 2 - 40, canvas.width, 70);
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 28px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('A HUGE WAVE OF ZOMBIES IS APPROACHING!', canvas.width / 2, canvas.height / 2 + 5);
                ctx.textAlign = 'left';
            }

            // Màn Hình Thắng Level & Nhận Cây Mới (Get New Plant Screen)
            if (gameState === 'LEVEL_WON') {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#ffeb3b';
                ctx.font = 'bold 36px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('LEVEL COMPLETED!', canvas.width / 2, 120);

                // Khung nhận phần thưởng
                ctx.fillStyle = '#2b1810';
                ctx.fillRect(canvas.width / 2 - 160, 160, 320, 220);
                ctx.strokeStyle = '#76ff03';
                ctx.lineWidth = 3;
                ctx.strokeRect(canvas.width / 2 - 160, 160, 320, 220);

                ctx.font = '70px sans-serif';
                ctx.fillText(currentLevel.rewardIcon, canvas.width / 2, 250);

                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 22px sans-serif';
                ctx.fillText(`YOU FOUND A NEW PLANT!`, canvas.width / 2, 300);
                ctx.font = '16px sans-serif';
                ctx.fillStyle = '#a5d6a7';
                ctx.fillText(currentLevel.rewardDesc, canvas.width / 2, 335);

                // Nút Tiếp Tục Màn Sau
                ctx.fillStyle = '#388e3c';
                ctx.fillRect(canvas.width / 2 - 100, 420, 200, 50);
                ctx.strokeStyle = '#ffffff';
                ctx.lineWidth = 2;
                ctx.strokeRect(canvas.width / 2 - 100, 420, 200, 50);

                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 20px sans-serif';
                ctx.fillText(currentLevelIndex < LEVELS_DATA.length - 1 ? 'NEXT LEVEL ➔' : 'REPLAY ADVENTURE', canvas.width / 2, 452);
                ctx.textAlign = 'left';
            }

            // Game Over
            if (gameState === 'GAME_OVER') {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.88)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#f44336';
                ctx.font = 'bold 46px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('THE ZOMBIES ATE YOUR BRAINS!', canvas.width / 2, canvas.height / 2 - 20);

                ctx.fillStyle = '#ffffff';
                ctx.font = '20px sans-serif';
                ctx.fillText('Nhấp chuột vào màn hình để thử lại màn này', canvas.width / 2, canvas.height / 2 + 40);
                ctx.textAlign = 'left';
            }
        }

        function gameLoop() {
            update();
            render();
            requestAnimationFrame(gameLoop);
        }

        // --- TƯƠNG TÁC CHUỘT (CLICK LOGIC) ---
        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;

            if (gameState === 'GAME_OVER') {
                initLevel(currentLevelIndex);
                return;
            }

            if (gameState === 'LEVEL_WON') {
                // Nhấp nút Next Level
                if (mouseX >= canvas.width / 2 - 100 && mouseX <= canvas.width / 2 + 100 &&
                    mouseY >= 420 && mouseY <= 470) {
                    const nextIdx = (currentLevelIndex + 1) % LEVELS_DATA.length;
                    initLevel(nextIdx);
                }
                return;
            }

            // 1. Nhặt Mặt Trời
            for (let i = fallingSuns.length - 1; i >= 0; i--) {
                const s = fallingSuns[i];
                if (Math.hypot(s.x + 15 - mouseX, s.y - 15 - mouseY) < 32) {
                    suns += 25;
                    playAudio('sun');
                    fallingSuns.splice(i, 1);
                    return;
                }
            }

            // 2. Chọn Thẻ Cây / Xẻng từ Thanh UI
            if (mouseY < OFFSET_Y) {
                let cardIndex = 0;
                currentLevel.unlockedPlants.forEach(pId => {
                    const x = 120 + cardIndex * 95;
                    if (mouseX >= x && mouseX <= x + 88) {
                        if (suns >= ALL_PLANTS[pId].cost) {
                            selectedTool = (selectedTool === pId) ? null : pId;
                        }
                    }
                    cardIndex++;
                });

                // Chọn Xẻng
                if (currentLevel.unlockedPlants.includes('wallnut')) {
                    const shovelX = 120 + cardIndex * 95 + 10;
                    if (mouseX >= shovelX && mouseX <= shovelX + 60) {
                        selectedTool = (selectedTool === 'shovel') ? null : 'shovel';
                    }
                }
                return;
            }

            // 3. Trồng Cây hoặc Dùng Xẻng trên bãi cỏ
            if (selectedTool && mouseX >= OFFSET_X && mouseY >= OFFSET_Y) {
                const c = Math.floor((mouseX - OFFSET_X) / CELL_W);
                const r = Math.floor((mouseY - OFFSET_Y) / CELL_H);

                if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
                    // Kiểm tra xem hàng này có đang hoạt động ở Level hiện tại không
                    if (currentLevel.activeRows.includes(r)) {
                        if (selectedTool === 'shovel') {
                            // Dùng Xẻng nhổ cây
                            if (grid[r][c]) {
                                grid[r][c].hp = 0;
                                grid[r][c] = null;
                                selectedTool = null;
                            }
                        } else {
                            // Trồng cây
                            if (!grid[r][c]) {
                                const card = ALL_PLANTS[selectedTool];
                                if (suns >= card.cost) {
                                    suns -= card.cost;
                                    const plant = new Plant(r, c, selectedTool);
                                    grid[r][c] = plant;
                                    plants.push(plant);
                                    playAudio('sun');
                                    selectedTool = null;
                                }
                            }
                        }
                    }
                }
            }
        });

        // Khởi động màn chơi 1-1
        initLevel(0);
        gameLoop();
    </script>
</body>
</html>
"""

components.html(pvz_adventure_html, height=580, scrolling=False)

with st.expander("🎮 Hướng Dẫn Tiến Trình Adventure Mode"):
    st.write("""
    * **Màn 1-1:** Bãi cỏ chỉ mở **1 làn ở giữa**. Bạn bắt đầu với cây bắn đậu **Peashooter**. Tiêu diệt hết Zombie để hoàn thành màn và mở khóa **Sunflower**.
    * **Màn 1-2:** Bãi cỏ mở rộng ra **3 làn**. Trồng thêm Sunflower để có nhiều Mặt trời hơn. Tiêu diệt đợt Zombie để nhận **Cherry Bomb**.
    * **Màn 1-3:** Bãi cỏ mở rộng đủ **5 làn chuẩn PvZ**. Mở khóa **Wall-nut** và **Xẻng nhổ cây (Shovel 🧹)** để đối đầu với các đợt **Buckethead Zombie** đội xô sắt trâu bò!
    """)
