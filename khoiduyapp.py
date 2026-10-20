import streamlit as st
import streamlit.components.v1 as components

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="Anime Battle 3.0 - Bleach vs Naruto Style",
    page_icon="⚔️",
    layout="wide"
)

# Custom CSS cho giao diện Streamlit hiện đại
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0d0e15, #1a1c29, #26122b);
            color: #ffffff;
        }
        .main-title {
            text-align: center;
            font-size: 2.5rem;
            font-weight: 900;
            background: -webkit-linear-gradient(45deg, #ff416c, #8a2be2, #00f2fe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        .sub-desc {
            text-align: center;
            color: #a0aec0;
            font-size: 1rem;
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-title">⚔️ ANIME BATTLE 3.0 ⚔️</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-desc">Game đối kháng 2D phong cách Bleach vs Naruto — Chế độ 2 Người chơi (P1 vs P2)</p>', unsafe_allow_html=True)

# Giao diện Sidebar hướng dẫn điều khiển
with st.sidebar:
    st.markdown("### 🎮 Bảng Điều Khiển Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🔴 PLAYER 1 (Soul Reaper)**")
        st.markdown("""
        * **A / D**: Di chuyển Trái / Phải
        * **W**: Nhảy lên
        * **J**: Tấn công thường (Combo)
        * **K**: Tuyệt kỹ Ultimate (Tốn 30 MP)
        * **L**: Tăng tốc / Lướt né
        """)
    
    with col2:
        st.markdown("**🔵 PLAYER 2 (Ninja Shinobi)**")
        st.markdown("""
        * **← / →**: Di chuyển Trái / Phải
        * **↑**: Nhảy lên
        * **Numpad 1**: Tấn công thường
        * **Numpad 2**: Tuyệt kỹ Rasengan (Tốn 30 MP)
        * **Numpad 3**: Tăng tốc / Lướt né
        """)
    
    st.markdown("---")
    st.info("💡 **Mẹo:** Đánh trúng đối thủ sẽ hồi năng lượng MP. Khi đủ MP hãy tung Tuyệt kỹ K hoặc Numpad 2 để gây sát thương cực lớn!")

# Mã Game HTML5 Canvas + JavaScript Physics Engine
game_html = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>Anime Fighting Game</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: #05050a;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-family: 'Segoe UI', Roboto, sans-serif;
            overflow: hidden;
        }
        #game-container {
            position: relative;
            width: 1024px;
            height: 576px;
            box-shadow: 0 0 30px rgba(138, 43, 226, 0.4);
            border: 3px solid #334155;
            border-radius: 10px;
            overflow: hidden;
            background: #0f172a;
        }
        canvas { display: block; width: 100%; height: 100%; }
        
        /* Giao diện HUD (Thanh máu & MP) */
        #hud {
            position: absolute;
            top: 15px;
            left: 20px;
            right: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            pointer-events: none;
            z-index: 10;
        }
        .player-hud { width: 42%; }
        .player-name {
            font-weight: 900;
            font-size: 16px;
            color: #fff;
            text-transform: uppercase;
            text-shadow: 0 2px 4px rgba(0,0,0,0.8);
            margin-bottom: 4px;
        }
        .bar-container {
            background: rgba(15, 23, 42, 0.8);
            border: 2px solid #475569;
            border-radius: 6px;
            padding: 3px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.6);
        }
        .hp-bar-bg { height: 22px; background: #334155; border-radius: 4px; overflow: hidden; position: relative; }
        .hp-bar-fill { height: 100%; transition: width 0.1s ease-out; }
        #p1-hp { background: linear-gradient(90deg, #ef4444, #f97316); width: 100%; }
        #p2-hp { background: linear-gradient(90deg, #3b82f6, #06b6d4); width: 100%; float: right; }
        
        .mp-bar-bg { height: 10px; background: #1e293b; border-radius: 3px; margin-top: 4px; overflow: hidden; }
        .mp-bar-fill { height: 100%; transition: width 0.15s ease-out; }
        #p1-mp { background: linear-gradient(90deg, #eab308, #facc15); width: 0%; }
        #p2-mp { background: linear-gradient(90deg, #a855f7, #c084fc); width: 0%; float: right; }

        #vs-badge {
            font-size: 28px;
            font-weight: 900;
            font-style: italic;
            color: #f43f5e;
            text-shadow: 0 0 10px rgba(244, 63, 94, 0.8);
        }

        #game-over {
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(15, 23, 42, 0.85);
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 20;
            backdrop-filter: blur(5px);
        }
        #game-over h1 { font-size: 50px; color: #fbbf24; margin-bottom: 10px; text-shadow: 0 0 20px rgba(251, 191, 36, 0.6); }
        #game-over p { font-size: 20px; color: #fff; margin-bottom: 20px; }
        #restart-btn {
            padding: 12px 30px; font-size: 18px; font-weight: bold;
            color: #fff; background: #8b5cf6; border: none; border-radius: 8px;
            cursor: pointer; box-shadow: 0 4px 14px rgba(139, 92, 246, 0.5);
            transition: all 0.2s;
        }
        #restart-btn:hover { background: #7c3aed; transform: scale(1.05); }
    </style>
</head>
<body>
    <div id="game-container">
        <div id="hud">
            <!-- Player 1 HUD -->
            <div class="player-hud">
                <div class="player-name">P1: Ichigo (Soul Reaper)</div>
                <div class="bar-container">
                    <div class="hp-bar-bg"><div id="p1-hp" class="hp-bar-fill"></div></div>
                    <div class="mp-bar-bg"><div id="p1-mp" class="mp-bar-fill"></div></div>
                </div>
            </div>

            <div id="vs-badge">VS</div>

            <!-- Player 2 HUD -->
            <div class="player-hud" style="text-align: right;">
                <div class="player-name">P2: Naruto (Shinobi)</div>
                <div class="bar-container">
                    <div class="hp-bar-bg"><div id="p2-hp" class="hp-bar-fill"></div></div>
                    <div class="mp-bar-bg"><div id="p2-mp" class="mp-bar-fill"></div></div>
                </div>
            </div>
        </div>

        <!-- Màn hình kết thúc game -->
        <div id="game-over">
            <h1 id="winner-text">P1 WINNER!</h1>
            <p>Trận đấu kết thúc!</p>
            <button id="restart-btn" onclick="restartGame()">Chơi Lại (Restart)</button>
        </div>

        <canvas id="gameCanvas" width="1024" height="576"></canvas>
    </div>

    <script>
        const canvas = document.getElementById('gameCanvas');
        const ctx = canvas.getContext('2d');

        const GRAVITY = 0.7;
        const GROUND_Y = 480;

        // Quản lý phím bấm
        const keys = {
            a: false, d: false, w: false, j: false, k: false, l: false,
            ArrowLeft: false, ArrowRight: false, ArrowUp: false,
            Numpad1: false, Numpad2: false, Numpad3: false,
            1: false, 2: false, 3: false // Hỗ trợ hàng phím số nếu không có Numpad
        };

        window.addEventListener('keydown', (e) => {
            if (e.code === 'KeyA') keys.a = true;
            if (e.code === 'KeyD') keys.d = true;
            if (e.code === 'KeyW') keys.w = true;
            if (e.code === 'KeyJ') keys.j = true;
            if (e.code === 'KeyK') keys.k = true;
            if (e.code === 'KeyL') keys.l = true;

            if (e.code === 'ArrowLeft') keys.ArrowLeft = true;
            if (e.code === 'ArrowRight') keys.ArrowRight = true;
            if (e.code === 'ArrowUp') keys.ArrowUp = true;
            if (e.code === 'Numpad1' || e.code === 'Digit1') keys.Numpad1 = true;
            if (e.code === 'Numpad2' || e.code === 'Digit2') keys.Numpad2 = true;
            if (e.code === 'Numpad3' || e.code === 'Digit3') keys.Numpad3 = true;
        });

        window.addEventListener('keyup', (e) => {
            if (e.code === 'KeyA') keys.a = false;
            if (e.code === 'KeyD') keys.d = false;
            if (e.code === 'KeyW') keys.w = false;
            if (e.code === 'KeyJ') keys.j = false;
            if (e.code === 'KeyK') keys.k = false;
            if (e.code === 'KeyL') keys.l = false;

            if (e.code === 'ArrowLeft') keys.ArrowLeft = false;
            if (e.code === 'ArrowRight') keys.ArrowRight = false;
            if (e.code === 'ArrowUp') keys.ArrowUp = false;
            if (e.code === 'Numpad1' || e.code === 'Digit1') keys.Numpad1 = false;
            if (e.code === 'Numpad2' || e.code === 'Digit2') keys.Numpad2 = false;
            if (e.code === 'Numpad3' || e.code === 'Digit3') keys.Numpad3 = false;
        });

        // Lớp đối tượng Hiệu ứng đòn đánh & Skill Projectile
        class Particle {
            constructor(x, y, vx, vy, color, radius, life) {
                this.x = x; this.y = y; this.vx = vx; this.vy = vy;
                this.color = color; this.radius = radius; this.life = life; this.maxLife = life;
            }
            update() {
                this.x += this.vx; this.y += this.vy; this.life--;
            }
            draw() {
                ctx.save();
                ctx.globalAlpha = this.life / this.maxLife;
                ctx.fillStyle = this.color;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
        }

        class SkillEffect {
            constructor(x, y, facing, type, owner) {
                this.x = x; this.y = y;
                this.facing = facing; // 1: Right, -1: Left
                this.type = type; // 'Getsuga' hoặc 'Rasengan'
                this.owner = owner;
                this.width = type === 'Getsuga' ? 80 : 50;
                this.height = type === 'Getsuga' ? 40 : 50;
                this.vx = facing * (type === 'Getsuga' ? 14 : 10);
                this.active = true;
                this.damage = type === 'Getsuga' ? 25 : 30;
            }
            update() {
                this.x += this.vx;
                if (this.x < -100 || this.x > canvas.width + 100) this.active = false;
            }
            draw() {
                ctx.save();
                if (this.type === 'Getsuga') {
                    ctx.fillStyle = '#ef4444';
                    ctx.shadowColor = '#f97316';
                    ctx.shadowBlur = 15;
                    ctx.beginPath();
                    ctx.ellipse(this.x, this.y, this.width, this.height / 2, 0, 0, Math.PI * 2);
                    ctx.fill();
                } else if (this.type === 'Rasengan') {
                    ctx.fillStyle = '#38bdf8';
                    ctx.shadowColor = '#0284c7';
                    ctx.shadowBlur = 20;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, this.width / 2, 0, Math.PI * 2);
                    ctx.fill();
                }
                ctx.restore();
            }
        }

        let particles = [];
        let skillEffects = [];

        // Class Nhân vật (Fighter)
        class Fighter {
            constructor({ x, y, color, facing, name, isP1 }) {
                this.x = x;
                this.y = y;
                this.width = 50;
                this.height = 110;
                this.vx = 0;
                this.vy = 0;
                this.color = color;
                this.facing = facing; // 1: Phải, -1: Trái
                this.name = name;
                this.isP1 = isP1;

                this.hp = 100;
                this.mp = 0;
                this.isGrounded = false;
                this.isAttacking = false;
                this.isSpecialAttacking = false;
                this.attackCooldown = 0;
                this.isHit = 0; // Thời gian dính đòn (Hitstun)

                // Hitbox đòn đánh thường
                this.attackBox = {
                    x: 0, y: 0, width: 80, height: 50
                };
            }

            update(target) {
                // Giảm hiệu ứng dính đòn
                if (this.isHit > 0) this.isHit--;

                // Trọng lực
                this.vy += GRAVITY;
                this.x += this.vx;
                this.y += this.vy;

                // Va chạm mặt đất
                if (this.y + this.height >= GROUND_Y) {
                    this.y = GROUND_Y - this.height;
                    this.vy = 0;
                    this.isGrounded = true;
                } else {
                    this.isGrounded = false;
                }

                // Giới hạn khung hình
                if (this.x < 0) this.x = 0;
                if (this.x + this.width > canvas.width) this.x = canvas.width - this.width;

                // Tự động quay mặt về đối thủ khi không đánh
                if (!this.isAttacking && this.isHit === 0) {
                    this.facing = this.x < target.x ? 1 : -1;
                }

                // Cập nhật vị trí Hitbox đánh thường
                this.attackBox.x = this.facing === 1 ? this.x + this.width : this.x - this.attackBox.width;
                this.attackBox.y = this.y + 20;

                if (this.attackCooldown > 0) this.attackCooldown--;

                // Giảm ma sát di chuyển
                this.vx *= 0.8;
            }

            draw() {
                ctx.save();
                // Hiệu ứng giật đỏ khi bị đánh
                if (this.isHit > 0) {
                    ctx.fillStyle = '#ff2222';
                } else {
                    ctx.fillStyle = this.color;
                }

                // Thân nhân vật
                ctx.fillRect(this.x, this.y, this.width, this.height);

                // Đầu
                ctx.fillStyle = '#fde047'; // Tóc
                ctx.fillRect(this.x + (this.facing === 1 ? 20 : 0), this.y - 15, 30, 20);

                // Mắt / Hướng nhìn
                ctx.fillStyle = '#000';
                ctx.fillRect(this.facing === 1 ? this.x + 35 : this.x + 5, this.y + 15, 8, 8);

                // Vũ khí / Hiệu ứng đánh
                if (this.isAttacking) {
                    ctx.fillStyle = this.isP1 ? '#ef4444' : '#38bdf8';
                    ctx.fillRect(this.attackBox.x, this.attackBox.y, this.attackBox.width, this.attackBox.height);
                }

                ctx.restore();
            }

            attack(target) {
                if (this.attackCooldown === 0 && this.isHit === 0) {
                    this.isAttacking = true;
                    this.attackCooldown = 20;

                    // Tạo hạt hiệu ứng vệt chém
                    for (let i = 0; i < 8; i++) {
                        particles.push(new Particle(
                            this.attackBox.x + Math.random() * this.attackBox.width,
                            this.attackBox.y + Math.random() * this.attackBox.height,
                            this.facing * (Math.random() * 4 + 2),
                            (Math.random() - 0.5) * 4,
                            this.isP1 ? '#f97316' : '#06b6d4',
                            Math.random() * 4 + 2, 15
                        ));
                    }

                    // Kiểm tra trúng đối thủ
                    if (
                        this.attackBox.x < target.x + target.width &&
                        this.attackBox.x + this.attackBox.width > target.x &&
                        this.attackBox.y < target.y + target.height &&
                        this.attackBox.y + this.attackBox.height > target.y
                    ) {
                        target.takeDamage(10, this.facing * 8);
                        this.gainMp(15);
                    }

                    setTimeout(() => { this.isAttacking = false; }, 150);
                }
            }

            specialAttack() {
                if (this.mp >= 30 && this.attackCooldown === 0 && this.isHit === 0) {
                    this.mp -= 30;
                    this.attackCooldown = 40;
                    updateHud();

                    // Tải chiêu tuyệt kỹ
                    const skillType = this.isP1 ? 'Getsuga' : 'Rasengan';
                    skillEffects.push(new SkillEffect(
                        this.x + (this.facing === 1 ? this.width + 20 : -20),
                        this.y + 40,
                        this.facing,
                        skillType,
                        this
                    ));
                }
            }

            dash() {
                if (this.attackCooldown === 0 && this.isHit === 0) {
                    this.vx = this.facing * 22;
                    this.attackCooldown = 15;
                    // Tạo bóng mờ
                    for (let i = 0; i < 5; i++) {
                        particles.push(new Particle(
                            this.x + Math.random() * this.width,
                            this.y + Math.random() * this.height,
                            0, 0, '#ffffff', 4, 10
                        ));
                    }
                }
            }

            takeDamage(amount, knockbackX) {
                this.hp -= amount;
                if (this.hp < 0) this.hp = 0;
                this.vx = knockbackX;
                this.vy = -4;
                this.isHit = 12; // Choáng 12 frames
                updateHud();

                // Tạo hiệu ứng máu/tóe lửa
                for (let i = 0; i < 12; i++) {
                    particles.push(new Particle(
                        this.x + this.width / 2, this.y + this.height / 2,
                        (Math.random() - 0.5) * 10, (Math.random() - 0.5) * 10,
                        '#dc2626', Math.random() * 5 + 2, 20
                    ));
                }
            }

            gainMp(amount) {
                this.mp += amount;
                if (this.mp > 100) this.mp = 100;
                updateHud();
            }
        }

        // Khởi tạo 2 Nhân vật
        const p1 = new Fighter({ x: 150, y: 300, color: '#1e293b', facing: 1, name: 'Ichigo', isP1: true });
        const p2 = new Fighter({ x: 800, y: 300, color: '#ea580c', facing: -1, name: 'Naruto', isP1: false });

        function updateHud() {
            document.getElementById('p1-hp').style.width = p1.hp + '%';
            document.getElementById('p2-hp').style.width = p2.hp + '%';
            document.getElementById('p1-mp').style.width = p1.mp + '%';
            document.getElementById('p2-mp').style.width = p2.mp + '%';
        }

        let isGameOver = false;

        function checkWinCondition() {
            if (p1.hp <= 0 || p2.hp <= 0) {
                isGameOver = true;
                const winnerText = document.getElementById('winner-text');
                const gameOverScreen = document.getElementById('game-over');

                if (p1.hp <= 0 && p2.hp <= 0) {
                    winnerText.innerText = "HÒA NHAU (DRAW)!";
                } else if (p1.hp <= 0) {
                    winnerText.innerText = "PLAYER 2 (NARUTO) WINNER!";
                } else {
                    winnerText.innerText = "PLAYER 1 (ICHIGO) WINNER!";
                }
                gameOverScreen.style.display = 'flex';
            }
        }

        function restartGame() {
            p1.hp = 100; p1.mp = 0; p1.x = 150; p1.y = 300; p1.vx = 0; p1.vy = 0;
            p2.hp = 100; p2.mp = 0; p2.x = 800; p2.y = 300; p2.vx = 0; p2.vy = 0;
            particles = [];
            skillEffects = [];
            isGameOver = false;
            updateHud();
            document.getElementById('game-over').style.display = 'none';
        }

        // Vòng lặp Game (Game Loop)
        function gameLoop() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            // Vẽ Sân đấu (Stage Background)
            ctx.fillStyle = '#1e293b';
            ctx.fillRect(0, GROUND_Y, canvas.width, canvas.height - GROUND_Y);
            ctx.fillStyle = '#475569';
            ctx.fillRect(0, GROUND_Y, canvas.width, 8);

            if (!isGameOver) {
                // Xử lý di chuyển P1
                if (keys.a && p1.isHit === 0) p1.vx = -6;
                if (keys.d && p1.isHit === 0) p1.vx = 6;
                if (keys.w && p1.isGrounded && p1.isHit === 0) p1.vy = -16;
                if (keys.j) p1.attack(p2);
                if (keys.k) p1.specialAttack();
                if (keys.l) p1.dash();

                // Xử lý di chuyển P2
                if (keys.ArrowLeft && p2.isHit === 0) p2.vx = -6;
                if (keys.ArrowRight && p2.isHit === 0) p2.vx = 6;
                if (keys.ArrowUp && p2.isGrounded && p2.isHit === 0) p2.vy = -16;
                if (keys.Numpad1) p2.attack(p1);
                if (keys.Numpad2) p2.specialAttack();
                if (keys.Numpad3) p2.dash();
            }

            // Cập nhật nhân vật
            p1.update(p2);
            p2.update(p1);

            // Cập nhật tuyệt kỹ (Projectiles)
            for (let i = skillEffects.length - 1; i >= 0; i--) {
                const skill = skillEffects[i];
                skill.update();
                skill.draw();

                // Bắt va chạm Tuyệt kỹ với đối thủ
                const target = skill.owner === p1 ? p2 : p1;
                if (
                    skill.x - skill.width / 2 < target.x + target.width &&
                    skill.x + skill.width / 2 > target.x &&
                    skill.y - skill.height / 2 < target.y + target.height &&
                    skill.y + skill.height / 2 > target.y
                ) {
                    target.takeDamage(skill.damage, skill.facing * 12);
                    skill.owner.gainMp(10);
                    skill.active = false;
                }

                if (!skill.active) skillEffects.splice(i, 1);
            }

            // Cập nhật hạt hiệu ứng Particle
            for (let i = particles.length - 1; i >= 0; i--) {
                particles[i].update();
                particles[i].draw();
                if (particles[i].life <= 0) particles.splice(i, 1);
            }

            // Vẽ Nhân vật
            p1.draw();
            p2.draw();

            checkWinCondition();
            requestAnimationFrame(gameLoop);
        }

        // Bắt đầu Game
        updateHud();
        gameLoop();
    </script>
</body>
</html>
"""

# Hiển thị game tương tác trong Streamlit
components.html(game_html, height=620, scrolling=False)
