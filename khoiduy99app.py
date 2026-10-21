import streamlit as st
import streamlit.components.v1 as components

# Configure Streamlit Page
st.set_page_config(
    page_title="Plants vs. Zombies - Classic Edition",
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
        color: #76ff03 !important; 
        font-family: 'Trebuchet MS', 'Segoe UI', sans-serif; 
        text-align: center; 
        margin-bottom: 2px; 
        text-shadow: 2px 2px 4px #000; 
    }
    p { 
        text-align: center; 
        color: #a5d6a7; 
        font-family: sans-serif; 
        margin-bottom: 10px; 
    }
</style>
""", unsafe_allow_html=True)

st.title("🌻 PLANTS VS. ZOMBIES 🧟")
st.markdown("Trồng cây bảo vệ ngôi nhà! Nhặt **Mặt Trời ☀️** để lấy năng lượng, dùng **Xẻng 🧹** để nhổ cây khi cần.")

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
            width: 900px;
            height: 580px;
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
        <canvas id="pvzCanvas" width="900" height="580"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('pvzCanvas');
        const ctx = canvas.getContext('2d');

        // Bàn cờ 5 Hàng x 8 Cột chuẩn PvZ
        const ROWS = 5;
        const COLS = 8;
        const CELL_W = 85;
        const CELL_H = 85;
        const OFFSET_X = 150; // Lề trái dành cho Cửa nhà & Máy cắt cỏ
        const OFFSET_Y = 100; // Lề trên dành cho Thanh Seed Bank

        // Trạng thái Game
        let suns = 200;
        let score = 0;
        let gameOver = false;
        let selectedTool = null; // 'sunflower', 'peashooter', 'snowpea', 'wallnut', 'cherry', 'shovel'
        let frameCount = 0;

        let levelZombiesSpawned = 0;
        let levelTotalZombies = 20;
        let levelZombiesKilled = 0;
        let hugeWaveTriggered = false;
        let hugeWaveBannerTimer = 0;

        const PLANT_TYPES = {
            'sunflower': { name: 'Sunflower', cost: 50, icon: '🌻', cdMax: 120 },
            'peashooter': { name: 'Peashooter', cost: 100, icon: '🫛', cdMax: 100 },
            'snowpea': { name: 'Snow Pea', cost: 175, icon: '❄️', cdMax: 150 },
            'wallnut': { name: 'Wall-nut', cost: 50, icon: '🧱', cdMax: 200 },
            'cherry': { name: 'Cherry Bomb', cost: 150, icon: '🍒', cdMax: 300 }
        };

        // Cooldown cho từng loại cây
        let plantCooldowns = {
            'sunflower': 0,
            'peashooter': 0,
            'snowpea': 0,
            'wallnut': 0,
            'cherry': 0
        };

        let grid = Array(ROWS).fill(null).map(() => Array(COLS).fill(null));

        // 5 Máy cắt cỏ (Lawn Mowers)
        let lawnMowers = [];
        for (let r = 0; r < ROWS; r++) {
            lawnMowers.push({ row: r, x: OFFSET_X - 48, y: OFFSET_Y + r * CELL_H + 20, active: false, used: false });
        }

        let plants = [];
        let zombies = [];
        let peas = [];
        let fallingSuns = [];
        let particles = [];
        let explosions = [];

        // Web Audio Synthesizer cho Âm thanh
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playSound(type) {
            try {
                if (audioCtx.state === 'suspended') audioCtx.resume();
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain);
                gain.connect(audioCtx.destination);

                if (type === 'sun') {
                    osc.frequency.setValueAtTime(523.25, audioCtx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(880, audioCtx.currentTime + 0.15);
                    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.15);
                    osc.start(); osc.stop(audioCtx.currentTime + 0.15);
                } else if (type === 'shoot') {
                    osc.frequency.setValueAtTime(300, audioCtx.currentTime);
                    osc.frequency.linearRampToValueAtTime(120, audioCtx.currentTime + 0.08);
                    gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.08);
                    osc.start(); osc.stop(audioCtx.currentTime + 0.08);
                } else if (type === 'boom') {
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(150, audioCtx.currentTime);
                    osc.frequency.linearRampToValueAtTime(30, audioCtx.currentTime + 0.35);
                    gain.gain.setValueAtTime(0.4, audioCtx.currentTime);
                    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.35);
                    osc.start(); osc.stop(audioCtx.currentTime + 0.35);
                } else if (type === 'mower') {
                    osc.type = 'sawtooth';
                    osc.frequency.setValueAtTime(100, audioCtx.currentTime);
                    osc.frequency.linearRampToValueAtTime(220, audioCtx.currentTime + 0.5);
                    gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                    gain.gain.linearRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);
                    osc.start(); osc.stop(audioCtx.currentTime + 0.5);
                }
            } catch(e) {}
        }

        function drawSunflower(x, y, animFrame) {
            ctx.save();
            ctx.translate(x, y);

            const bob = Math.sin(animFrame * 0.1) * 2;

            // Thân
            ctx.beginPath();
            ctx.moveTo(0, 10);
            ctx.quadraticCurveTo(-4, 25, 0, 35);
            ctx.strokeStyle = '#2e7d32';
            ctx.lineWidth = 6;
            ctx.stroke();

            // Lá
            ctx.fillStyle = '#388e3c';
            ctx.beginPath(); ctx.ellipse(-12, 28, 10, 5, -0.4, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.ellipse(12, 28, 10, 5, 0.4, 0, Math.PI * 2); ctx.fill();

            // Cánh hoa
            const petalCount = 10;
            ctx.fillStyle = '#ffeb3b';
            for (let i = 0; i < petalCount; i++) {
                const angle = (i * Math.PI * 2) / petalCount + Math.sin(animFrame * 0.05) * 0.08;
                const px = Math.cos(angle) * 18;
                const py = (bob - 5) + Math.sin(angle) * 18;
                ctx.beginPath();
                ctx.arc(px, py, 9, 0, Math.PI * 2);
                ctx.fill();
            }

            // Mắt xích trung tâm
            ctx.fillStyle = '#795548';
            ctx.beginPath();
            ctx.arc(0, bob - 5, 14, 0, Math.PI * 2);
            ctx.fill();

            // Mắt & Cười
            ctx.fillStyle = '#000';
            ctx.beginPath(); ctx.arc(-4, bob - 8, 2.2, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.arc(4, bob - 8, 2.2, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.arc(0, bob - 4, 4.5, 0, Math.PI); ctx.stroke();

            ctx.restore();
        }

        function drawPeashooter(x, y, animFrame, isIce = false) {
            ctx.save();
            ctx.translate(x, y);

            const recoil = Math.sin(animFrame * 0.15) * 1.5;

            // Thân
            ctx.beginPath();
            ctx.moveTo(0, 10);
            ctx.quadraticCurveTo(5, 25, 0, 35);
            ctx.strokeStyle = isIce ? '#0097a7' : '#2e7d32';
            ctx.lineWidth = 6;
            ctx.stroke();

            // Lá
            ctx.fillStyle = isIce ? '#00acc1' : '#388e3c';
            ctx.beginPath(); ctx.ellipse(-12, 30, 12, 6, -0.2, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.ellipse(12, 30, 12, 6, 0.2, 0, Math.PI * 2); ctx.fill();

            // Đầu Cây
            ctx.fillStyle = isIce ? '#00e5ff' : '#4caf50';
            ctx.beginPath();
            ctx.arc(-2 + recoil, -6, 16, 0, Math.PI * 2);
            ctx.fill();

            // Tinh thể băng phía sau (Snow Pea)
            if (isIce) {
                ctx.fillStyle = '#e0f7fa';
                ctx.beginPath();
                ctx.moveTo(-16, -14); ctx.lineTo(-24, -18); ctx.lineTo(-18, -8); ctx.fill();
                ctx.beginPath();
                ctx.moveTo(-16, 0); ctx.lineTo(-25, 2); ctx.lineTo(-18, 6); ctx.fill();
            }

            // Nòng bắn
            ctx.beginPath();
            ctx.ellipse(12 + recoil, -6, 10, 8, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = isIce ? '#00838f' : '#1b5e20';
            ctx.beginPath();
            ctx.ellipse(16 + recoil, -6, 4, 7, 0, 0, Math.PI * 2);
            ctx.fill();

            // Mắt
            ctx.fillStyle = '#000';
            ctx.beginPath(); ctx.arc(2 + recoil, -10, 2.5, 0, Math.PI * 2); ctx.fill();

            ctx.restore();
        }

        function drawWallnut(x, y, hp, maxHp, animFrame) {
            ctx.save();
            ctx.translate(x, y);

            const bob = Math.sin(animFrame * 0.05) * 1;

            // Thân Wall-nut
            ctx.fillStyle = '#8d6e63';
            ctx.beginPath();
            ctx.ellipse(0, 5 + bob, 18, 24, 0, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = '#5d4037';
            ctx.lineWidth = 3;
            ctx.stroke();

            // Mắt
            ctx.fillStyle = '#000';
            ctx.beginPath(); ctx.arc(-5, -4 + bob, 3, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.arc(5, -4 + bob, 3, 0, Math.PI * 2); ctx.fill();

            // Vết nứt khi mất máu
            if (hp < maxHp * 0.6) {
                ctx.strokeStyle = '#3e2723';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(-6, 2 + bob); ctx.lineTo(-2, 10 + bob); ctx.lineTo(-8, 16 + bob);
                ctx.stroke();
            }
            if (hp < maxHp * 0.3) {
                ctx.beginPath();
                ctx.moveTo(4, -2 + bob); ctx.lineTo(8, 6 + bob); ctx.lineTo(3, 14 + bob);
                ctx.stroke();
            }

            ctx.restore();
        }

        function drawCherryBomb(x, y, animFrame) {
            ctx.save();
            ctx.translate(x, y);

            const pulse = Math.sin(animFrame * 0.3) * 2;

            // Cuống lá
            ctx.strokeStyle = '#388e3c';
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(-8, -2); ctx.quadraticCurveTo(0, -18, 0, -22);
            ctx.moveTo(8, -2); ctx.quadraticCurveTo(0, -18, 0, -22);
            ctx.stroke();

            // Quả 1
            ctx.fillStyle = '#d32f2f';
            ctx.beginPath();
            ctx.arc(-10, 2, 12 + pulse, 0, Math.PI * 2);
            ctx.fill();

            // Quả 2
            ctx.beginPath();
            ctx.arc(10, 2, 12 + pulse, 0, Math.PI * 2);
            ctx.fill();

            // Mắt tức giận
            ctx.fillStyle = '#fff';
            ctx.beginPath(); ctx.arc(-12, -2, 3, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.arc(8, -2, 3, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = '#000';
            ctx.beginPath(); ctx.arc(-11, -2, 1.5, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath(); ctx.arc(9, -2, 1.5, 0, Math.PI * 2); ctx.fill();

            ctx.restore();
        }

        function drawZombie(x, y, hp, maxHp, type, slowTimer, animFrame) {
            ctx.save();
            ctx.translate(x, y);

            const walkWobble = Math.sin(animFrame * 0.1) * 3;

            // Thân Zombie
            ctx.fillStyle = '#4e342e'; // Áo nâu
            ctx.fillRect(-10, -10 + walkWobble, 20, 30);

            // Quần
            ctx.fillStyle = '#1a237e';
            ctx.fillRect(-9, 20 + walkWobble, 8, 18);
            ctx.fillRect(1, 20 + walkWobble, 8, 18);

            // Đầu (Màu da xám/băng)
            ctx.fillStyle = slowTimer > 0 ? '#4dd0e1' : '#81c784';
            ctx.beginPath();
            ctx.arc(0, -22 + walkWobble, 14, 0, Math.PI * 2);
            ctx.fill();

            // Mắt & Răng
            ctx.fillStyle = '#d50000';
            ctx.beginPath(); ctx.arc(-4, -24 + walkWobble, 3, 0, Math.PI * 2); ctx.fill();
            ctx.fillStyle = '#ffffff';
            ctx.beginPath(); ctx.arc(4, -24 + walkWobble, 2, 0, Math.PI * 2); ctx.fill();

            // Tay
            ctx.fillStyle = slowTimer > 0 ? '#4dd0e1' : '#81c784';
            ctx.fillRect(-18, -6 + walkWobble, 14, 6);

            // Nón giao thông (Conehead Zombie)
            if (type === 'conehead') {
                ctx.fillStyle = '#ff6d00';
                ctx.beginPath();
                ctx.moveTo(-12, -32 + walkWobble);
                ctx.lineTo(0, -55 + walkWobble);
                ctx.lineTo(12, -32 + walkWobble);
                ctx.closePath();
                ctx.fill();
                ctx.fillStyle = '#ffffff';
                ctx.fillRect(-10, -38 + walkWobble, 20, 4);
            }

            // Xô sắt (Buckethead Zombie)
            if (type === 'buckethead') {
                ctx.fillStyle = '#b0bec5';
                ctx.fillRect(-12, -48 + walkWobble, 24, 22);
                ctx.fillStyle = '#78909c';
                ctx.fillRect(-14, -28 + walkWobble, 28, 4);
            }

            // Cờ (Flag Zombie)
            if (type === 'flag') {
                ctx.fillStyle = '#d32f2f';
                ctx.fillRect(-22, -60 + walkWobble, 18, 12);
                ctx.strokeStyle = '#5d4037';
                ctx.lineWidth = 2;
                ctx.beginPath();
                ctx.moveTo(-22, -60 + walkWobble); ctx.lineTo(-22, -10 + walkWobble);
                ctx.stroke();
            }

            // Bông tuyết khi bị làm chậm
            if (slowTimer > 0) {
                ctx.font = '16px sans-serif';
                ctx.fillText('❄️', 10, -35 + walkWobble);
            }

            // Thanh máu
            if (hp < maxHp) {
                ctx.fillStyle = '#f44336';
                ctx.fillRect(-15, -55, 30, 4);
                ctx.fillStyle = '#4caf50';
                ctx.fillRect(-15, -55, 30 * Math.max(0, hp / maxHp), 4);
            }

            ctx.restore();
        }

        function drawSun(x, y, animFrame) {
            ctx.save();
            ctx.translate(x, y);
            const rot = animFrame * 0.03;

            ctx.fillStyle = '#ffeb3b';
            ctx.beginPath();
            ctx.arc(0, 0, 15, 0, Math.PI * 2);
            ctx.fill();

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
            // Seed Bank Khung gỗ
            ctx.fillStyle = '#2b170c';
            ctx.fillRect(0, 0, canvas.width, OFFSET_Y);
            ctx.strokeStyle = '#4a2a18';
            ctx.lineWidth = 3;
            ctx.strokeRect(0, 0, canvas.width, OFFSET_Y);

            // Khung Mặt Trời
            ctx.fillStyle = '#140b05';
            ctx.fillRect(15, 15, 95, 70);
            ctx.strokeStyle = '#fbc02d';
            ctx.lineWidth = 2;
            ctx.strokeRect(15, 15, 95, 70);

            drawSun(38, 50, frameCount);

            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 20px sans-serif';
            ctx.fillText(suns, 60, 57);

            // Thẻ Cây
            const cardKeys = ['sunflower', 'peashooter', 'snowpea', 'wallnut', 'cherry'];
            cardKeys.forEach((key, idx) => {
                const p = PLANT_TYPES[key];
                const x = 125 + idx * 95;
                const y = 15;
                const w = 88;
                const h = 70;

                const canAfford = suns >= p.cost && plantCooldowns[key] === 0;
                const isSelected = selectedTool === key;

                ctx.fillStyle = isSelected ? '#388e3c' : (canAfford ? '#3b2518' : '#1e130c');
                ctx.fillRect(x, y, w, h);
                ctx.strokeStyle = isSelected ? '#76ff03' : '#5a3d28';
                ctx.lineWidth = isSelected ? 3 : 1.5;
                ctx.strokeRect(x, y, w, h);

                ctx.font = '26px sans-serif';
                ctx.fillText(p.icon, x + 8, y + 42);
                ctx.font = 'bold 13px sans-serif';
                ctx.fillStyle = canAfford ? '#ffeb3b' : '#777777';
                ctx.fillText(`${p.cost}☀️`, x + 40, y + 40);

                // Hiệu ứng Cooldown
                if (plantCooldowns[key] > 0) {
                    const cdRatio = plantCooldowns[key] / p.cdMax;
                    ctx.fillStyle = 'rgba(0, 0, 0, 0.65)';
                    ctx.fillRect(x, y, w, h * cdRatio);
                }
            });

            // Khung Xẻng (Shovel Tool)
            const shovelX = 610;
            ctx.fillStyle = selectedTool === 'shovel' ? '#c62828' : '#3b281a';
            ctx.fillRect(shovelX, 15, 65, 70);
            ctx.strokeStyle = selectedTool === 'shovel' ? '#ff5252' : '#5a3d28';
            ctx.lineWidth = selectedTool === 'shovel' ? 3 : 1.5;
            ctx.strokeRect(shovelX, 15, 65, 70);
            ctx.font = '32px sans-serif';
            ctx.fillText('🧹', shovelX + 14, 58);

            // Progress Bar (Góc dưới bên phải)
            const barW = 180;
            const barH = 16;
            const barX = canvas.width - barW - 20;
            const barY = canvas.height - 30;

            ctx.fillStyle = '#111';
            ctx.fillRect(barX, barY, barW, barH);
            ctx.strokeStyle = '#558b2f';
            ctx.lineWidth = 2;
            ctx.strokeRect(barX, barY, barW, barH);

            const ratio = Math.min(1, levelZombiesKilled / levelTotalZombies);
            ctx.fillStyle = '#4caf50';
            ctx.fillRect(barX + barW * (1 - ratio), barY, barW * ratio, barH);

            ctx.font = '16px sans-serif';
            ctx.fillText('🧟', barX + barW * (1 - ratio) - 10, barY + 14);
            ctx.fillText('🚩', barX - 5, barY + 14);
        }

        function drawLawn() {
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    const x = OFFSET_X + c * CELL_W;
                    const y = OFFSET_Y + r * CELL_H;

                    ctx.fillStyle = (r + c) % 2 === 0 ? '#43a047' : '#388e3c';
                    ctx.fillRect(x, y, CELL_W, CELL_H);
                    ctx.strokeStyle = 'rgba(0,0,0,0.06)';
                    ctx.strokeRect(x, y, CELL_W, CELL_H);
                }
            }

            // Nhà bên trái (Đường đỏ nguy hiểm)
            ctx.fillStyle = 'rgba(211, 47, 47, 0.2)';
            ctx.fillRect(0, OFFSET_Y, OFFSET_X - 50, ROWS * CELL_H);

            // Máy cắt cỏ (Lawn Mowers)
            lawnMowers.forEach(lm => {
                if (!lm.used) {
                    ctx.font = '32px sans-serif';
                    ctx.fillText('🚜', lm.x, lm.y + 25);
                }
            });
        }

        class Plant {
            constructor(r, c, type) {
                this.r = r;
                this.c = c;
                this.x = OFFSET_X + c * CELL_W + CELL_W / 2;
                this.y = OFFSET_Y + r * CELL_H + CELL_H / 2;
                this.type = type;
                this.hp = type === 'wallnut' ? 600 : 100;
                this.maxHp = this.hp;
                this.timer = 0;
            }

            update() {
                this.timer++;

                // Sunflower sinh Sun
                if (this.type === 'sunflower' && this.timer % 380 === 0) {
                    fallingSuns.push({
                        x: this.x + (Math.random() * 20 - 10),
                        y: this.y - 10,
                        targetY: this.y + 20,
                        timer: 0
                    });
                }

                // Peashooter & Snowpea bắn đạn
                if ((this.type === 'peashooter' || this.type === 'snowpea') && this.timer % 100 === 0) {
                    const hasZombie = zombies.some(z => z.r === this.r && z.x > this.x);
                    if (hasZombie) {
                        peas.push({
                            x: this.x + 20,
                            y: this.y - 10,
                            r: this.r,
                            damage: 20,
                            isIce: (this.type === 'snowpea')
                        });
                        playSound('shoot');
                    }
                }

                // Cherry Bomb nổ diện 3x3
                if (this.type === 'cherry' && this.timer === 45) {
                    playSound('boom');
                    explosions.push({ x: this.x, y: this.y - 10, radius: 130, timer: 20 });
                    zombies.forEach(z => {
                        const dist = Math.hypot(z.x - this.x, (OFFSET_Y + z.r * CELL_H + CELL_H / 2) - this.y);
                        if (dist < 140) z.hp -= 500;
                    });
                    this.hp = 0;
                }
            }

            draw() {
                if (this.type === 'sunflower') drawSunflower(this.x, this.y, frameCount);
                else if (this.type === 'peashooter') drawPeashooter(this.x, this.y, frameCount, false);
                else if (this.type === 'snowpea') drawPeashooter(this.x, this.y, frameCount, true);
                else if (this.type === 'wallnut') drawWallnut(this.x, this.y, this.hp, this.maxHp, frameCount);
                else if (this.type === 'cherry') drawCherryBomb(this.x, this.y, frameCount);
            }
        }

        class Zombie {
            constructor(r, type = 'normal') {
                this.r = r;
                this.x = canvas.width + 20;
                this.y = OFFSET_Y + r * CELL_H + CELL_H / 2;
                this.type = type;
                this.slowTimer = 0;

                if (type === 'normal') this.hp = 100;
                else if (type === 'conehead') this.hp = 280;
                else if (type === 'buckethead') this.hp = 550;
                else if (type === 'flag') this.hp = 120;

                this.maxHp = this.hp;
                this.speed = (type === 'flag' ? 0.45 : 0.32) + Math.random() * 0.05;
            }

            update() {
                let eating = false;
                const cellC = Math.floor((this.x - OFFSET_X) / CELL_W);
                
                if (cellC >= 0 && cellC < COLS) {
                    const plant = grid[this.r][cellC];
                    if (plant && Math.abs(plant.x - this.x) < 25) {
                        eating = true;
                        plant.hp -= 0.7; // Cắn cây
                    }
                }

                let currentSpeed = this.speed;
                if (this.slowTimer > 0) {
                    this.slowTimer--;
                    currentSpeed *= 0.5; // Giảm 50% tốc độ
                }

                if (!eating) this.x -= currentSpeed;

                // Kích hoạt Lawn Mower hoặc thua game
                if (this.x <= OFFSET_X - 10) {
                    const lm = lawnMowers[this.r];
                    if (lm && !lm.used) {
                        lm.active = true;
                    } else if (this.x <= OFFSET_X - 45) {
                        gameOver = true;
                    }
                }
            }

            draw() {
                drawZombie(this.x, this.y, this.hp, this.maxHp, this.type, this.slowTimer, frameCount);
            }
        }

        let zombieTimer = 0;

        function update() {
            if (gameOver) return;

            frameCount++;

            // Cooldowns
            Object.keys(plantCooldowns).forEach(k => {
                if (plantCooldowns[k] > 0) plantCooldowns[k]--;
            });

            // 1. Mặt Trời tự nhiên
            if (Math.random() < 0.004) {
                fallingSuns.push({
                    x: OFFSET_X + Math.random() * (COLS * CELL_W - 40),
                    y: OFFSET_Y - 20,
                    targetY: OFFSET_Y + Math.random() * (ROWS * CELL_H - 40),
                    timer: 0
                });
            }

            fallingSuns.forEach(s => {
                if (s.y < s.targetY) s.y += 1.5;
                s.timer++;
            });
            fallingSuns = fallingSuns.filter(s => s.timer < 500);

            // 2. Spawn Zombies
            zombieTimer++;
            if (zombieTimer > 280 && levelZombiesSpawned < levelTotalZombies) {
                zombieTimer = 0;
                levelZombiesSpawned++;

                const rand = Math.random();
                let zType = 'normal';
                if (rand > 0.7) zType = 'conehead';
                if (rand > 0.9) zType = 'buckethead';

                if (levelZombiesSpawned === 15 && !hugeWaveTriggered) {
                    zType = 'flag';
                    hugeWaveTriggered = true;
                    hugeWaveBannerTimer = 180;
                }

                const randomRow = Math.floor(Math.random() * ROWS);
                zombies.push(new Zombie(randomRow, zType));
            }

            // 3. Update Cây
            plants.forEach(p => p.update());
            for (let r = 0; r < ROWS; r++) {
                for (let c = 0; c < COLS; c++) {
                    if (grid[r][c] && grid[r][c].hp <= 0) grid[r][c] = null;
                }
            }
            plants = plants.filter(p => p.hp > 0);

            // 4. Update Đạn Đậu
            peas.forEach(p => p.x += 6.5);
            peas.forEach(p => {
                zombies.forEach(z => {
                    if (z.r === p.r && Math.abs(z.x - p.x) < 20) {
                        z.hp -= p.damage;
                        if (p.isIce) z.slowTimer = 180;
                        p.hit = true;

                        for (let i = 0; i < 4; i++) {
                            particles.push({
                                x: p.x, y: p.y,
                                vx: (Math.random() - 0.5) * 4,
                                vy: (Math.random() - 0.5) * 4,
                                life: 15,
                                color: p.isIce ? '#00e5ff' : '#76ff03'
                            });
                        }
                    }
                });
            });
            peas = peas.filter(p => !p.hit && p.x < canvas.width);

            // 5. Update Máy Cắt Cỏ
            lawnMowers.forEach(lm => {
                if (lm.active) {
                    if (!lm.soundPlayed) { playSound('mower'); lm.soundPlayed = true; }
                    lm.x += 8.5;
                    zombies.forEach(z => {
                        if (z.r === lm.row && Math.abs(z.x - lm.x) < 30) z.hp = 0;
                    });
                    if (lm.x > canvas.width) {
                        lm.active = false;
                        lm.used = true;
                    }
                }
            });

            // 6. Update Zombies
            zombies.forEach(z => z.update());
            const initialCount = zombies.length;
            zombies = zombies.filter(z => z.hp > 0);
            const killedNow = initialCount - zombies.length;
            score += killedNow;
            levelZombiesKilled += killedNow;

            // 7. Update Particles & Explosions
            particles.forEach(pt => { pt.x += pt.vx; pt.y += pt.vy; pt.life--; });
            particles = particles.filter(pt => pt.life > 0);

            explosions.forEach(e => e.timer--);
            explosions = explosions.filter(e => e.timer > 0);

            if (hugeWaveBannerTimer > 0) hugeWaveBannerTimer--;
        }

        function render() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            drawLawn();
            plants.forEach(p => p.draw());

            // Draw Peas
            peas.forEach(p => {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.2)';
                ctx.beginPath(); ctx.ellipse(p.x, p.y + 16, 6, 2, 0, 0, Math.PI * 2); ctx.fill();

                ctx.fillStyle = p.isIce ? '#00e5ff' : '#76ff03';
                ctx.beginPath(); ctx.arc(p.x, p.y, 7, 0, Math.PI * 2); ctx.fill();
                ctx.strokeStyle = p.isIce ? '#00838f' : '#2e7d32';
                ctx.stroke();
            });

            zombies.forEach(z => z.draw());
            fallingSuns.forEach(s => drawSun(s.x, s.y, frameCount));

            particles.forEach(pt => {
                ctx.fillStyle = pt.color;
                ctx.fillRect(pt.x, pt.y, 3, 3);
            });

            explosions.forEach(e => {
                ctx.fillStyle = 'rgba(255, 87, 34, 0.6)';
                ctx.beginPath();
                ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.font = '48px sans-serif';
                ctx.fillText('💥', e.x - 20, e.y + 15);
            });

            drawUI();

            // Huge Wave Banner
            if (hugeWaveBannerTimer > 0) {
                ctx.fillStyle = 'rgba(180, 0, 0, 0.85)';
                ctx.fillRect(0, canvas.height / 2 - 35, canvas.width, 60);
                ctx.fillStyle = '#ffffff';
                ctx.font = 'bold 26px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('A HUGE WAVE OF ZOMBIES IS APPROACHING!', canvas.width / 2, canvas.height / 2 + 5);
                ctx.textAlign = 'left';
            }

            // Game Over Screen
            if (gameOver) {
                ctx.fillStyle = 'rgba(0, 0, 0, 0.85)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                ctx.fillStyle = '#f44336';
                ctx.font = 'bold 44px sans-serif';
                ctx.textAlign = 'center';
                ctx.fillText('ZOMBIES ATE YOUR BRAINS!', canvas.width / 2, canvas.height / 2 - 20);

                ctx.fillStyle = '#ffffff';
                ctx.font = '20px sans-serif';
                ctx.fillText(`Điểm số của bạn: ${score} Zombie`, canvas.width / 2, canvas.height / 2 + 30);
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

            // 1. Nhặt Mặt Trời
            for (let i = fallingSuns.length - 1; i >= 0; i--) {
                const s = fallingSuns[i];
                if (Math.hypot(s.x - mouseX, s.y - mouseY) < 32) {
                    suns += 25;
                    playSound('sun');
                    fallingSuns.splice(i, 1);
                    return;
                }
            }

            // 2. Chọn Thẻ Cây / Xẻng trên UI
            if (mouseY < OFFSET_Y) {
                const cardKeys = ['sunflower', 'peashooter', 'snowpea', 'wallnut', 'cherry'];
                cardKeys.forEach((key, idx) => {
                    const x = 125 + idx * 95;
                    if (mouseX >= x && mouseX <= x + 88) {
                        if (suns >= PLANT_TYPES[key].cost && plantCooldowns[key] === 0) {
                            selectedTool = (selectedTool === key) ? null : key;
                        }
                    }
                });

                // Chọn Xẻng
                if (mouseX >= 610 && mouseX <= 675) {
                    selectedTool = (selectedTool === 'shovel') ? null : 'shovel';
                }
                return;
            }

            // 3. Trồng Cây hoặc Dùng Xẻng
            if (selectedTool && mouseX >= OFFSET_X && mouseY >= OFFSET_Y) {
                const c = Math.floor((mouseX - OFFSET_X) / CELL_W);
                const r = Math.floor((mouseY - OFFSET_Y) / CELL_H);

                if (r >= 0 && r < ROWS && c >= 0 && c < COLS) {
                    if (selectedTool === 'shovel') {
                        if (grid[r][c]) {
                            grid[r][c].hp = 0;
                            grid[r][c] = null;
                            selectedTool = null;
                        }
                    } else if (!grid[r][c]) {
                        const pInfo = PLANT_TYPES[selectedTool];
                        if (suns >= pInfo.cost && plantCooldowns[selectedTool] === 0) {
                            suns -= pInfo.cost;
                            plantCooldowns[selectedTool] = pInfo.cdMax;
                            const newPlant = new Plant(r, c, selectedTool);
                            grid[r][c] = newPlant;
                            plants.push(newPlant);
                            playSound('sun');
                            selectedTool = null;
                        }
                    }
                }
            }
        });

        // Khởi chạy Vòng lặp Game
        gameLoop();
    </script>
</body>
</html>
"""

components.html(pvz_game_html, height=600, scrolling=False)

with st.expander("📖 Hướng dẫn chi tiết & Quy tắc trò chơi"):
    st.write("""
    * 🌻 **Sunflower (50 Sun):** Sinh ánh nắng định kỳ.
    * 🫛 **Peashooter (100 Sun):** Bắn đạn đậu xanh tiêu diệt Zombie trên cùng hàng.
    * ❄️ **Snow Pea (175 Sun):** Bắn đạn băng làm chậm 50% tốc độ di chuyển của Zombie.
    * 🧱 **Wall-nut (50 Sun):** Lá chắn máu cực trâu (600 HP) giúp chặn đợt tấn công của Zombie.
    * 🍒 **Cherry Bomb (150 Sun):** Nổ diện rộng 3x3 tiêu diệt sạch Zombie khẩn cấp.
    * 🧹 **Xẻng (Shovel):** Chọn xẻng rồi nhấp vào cây để nhổ bỏ khi muốn thay đổi vị trí.
    * 🚜 **Máy cắt cỏ (Lawn Mower):** Vũ khí phòng thủ dòng cuối ở bên trái bãi cỏ, tự động lao ra cán sạch Zombie nếu chúng tràn tới!
    """)
