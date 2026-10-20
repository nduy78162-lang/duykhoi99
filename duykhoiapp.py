import random

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Brain Cubes 3D", page_icon="🧠", layout="wide")

# ---------------------------------------------------------------------------
# GAME 3D (Three.js nhúng qua components.html)
# ---------------------------------------------------------------------------
GAME_HTML = """
<div id="wrap" style="position:relative;font-family:sans-serif;color:#fff;">
  <div id="c" style="width:100%;height:560px;border-radius:12px;overflow:hidden;
       background:radial-gradient(circle at 50% 30%,#1b2a4e,#0a0e1a);"></div>
  <div id="hud" style="position:absolute;top:12px;left:16px;font-size:16px;line-height:1.6;
       text-shadow:0 1px 4px #000;pointer-events:none;">
    Level: <b id="lv">1</b> &nbsp; Điểm: <b id="sc">0</b> &nbsp;
    Mạng: <b id="li">3</b> &nbsp; Kỷ lục: <b id="bs">0</b>
  </div>
  <div id="msg" style="position:absolute;bottom:16px;width:100%;text-align:center;
       font-size:18px;text-shadow:0 1px 4px #000;pointer-events:none;">
    Bấm "Bắt đầu" rồi ghi nhớ thứ tự các khối sáng lên
  </div>
  <button id="start" style="position:absolute;top:12px;right:16px;padding:8px 18px;
       font-size:16px;border:none;border-radius:8px;background:#4f8cff;color:#fff;cursor:pointer;">
    Bắt đầu
  </button>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
const GRID = __GRID__;
const SPEED = __SPEED__;   // ms mỗi lần sáng

const container = document.getElementById('c');
const W = container.clientWidth, H = 560;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, W / H, 0.1, 100);
camera.position.set(0, GRID * 1.6, GRID * 2.1);
camera.lookAt(0, 0, 0);

const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setSize(W, H);
renderer.setPixelRatio(window.devicePixelRatio);
container.appendChild(renderer.domElement);

scene.add(new THREE.AmbientLight(0xffffff, 0.55));
const dl = new THREE.DirectionalLight(0xffffff, 0.9);
dl.position.set(5, 10, 7);
scene.add(dl);

const group = new THREE.Group();
scene.add(group);

const cubes = [];
const gap = 1.35;
const offset = (GRID - 1) * gap / 2;
for (let i = 0; i !== GRID * GRID; i++) {
  const x = i % GRID, z = Math.floor(i / GRID);
  const color = new THREE.Color().setHSL(i / (GRID * GRID), 0.65, 0.5);
  const mat = new THREE.MeshStandardMaterial({
    color: color, emissive: 0x000000, metalness: 0.2, roughness: 0.4
  });
  const cube = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), mat);
  cube.position.set(x * gap - offset, 0, z * gap - offset);
  cube.userData = { i: i, flash: 0 };
  group.add(cube);
  cubes.push(cube);
}

// Sàn
const floor = new THREE.Mesh(
  new THREE.CircleGeometry(GRID * 1.5, 48),
  new THREE.MeshBasicMaterial({ color: 0x141c33 })
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -0.7;
group.add(floor);

// ---- Trạng thái game ----
let seq = [], pos = 0, level = 1, score = 0, lives = 3;
let accept = false, running = false;
let best = 0;
try { best = parseInt(localStorage.getItem('bc_best') || '0'); } catch (e) {}
const $ = id => document.getElementById(id);
function hud() {
  $('lv').textContent = level; $('sc').textContent = score;
  $('li').textContent = lives; $('bs').textContent = best;
}
function say(t) { $('msg').textContent = t; }
const sleep = ms => new Promise(r => setTimeout(r, ms));

function flash(c) {
  c.userData.flash = 1;
}

async function playSeq() {
  accept = false;
  say('Xem kỹ thứ tự...');
  await sleep(700);
  for (const idx of seq) {
    flash(cubes[idx]);
    await sleep(SPEED);
    await sleep(150);
  }
  pos = 0;
  accept = true;
  say('Đến lượt bạn! Bấm các khối theo đúng thứ tự');
}

async function nextRound() {
  seq.push(Math.floor(Math.random() * cubes.length));
  hud();
  await playSeq();
}

async function startGame() {
  seq = []; level = 1; score = 0; lives = 3; running = true;
  $('start').textContent = 'Chơi lại';
  await nextRound();
}

function gameOver() {
  running = false; accept = false;
  if (score > best) {
    best = score;
    try { localStorage.setItem('bc_best', String(best)); } catch (e) {}
  }
  hud();
  say('Hết mạng! Điểm của bạn: ' + score + '. Bấm "Chơi lại".');
}

// ---- Điều khiển: kéo để xoay, bấm để chọn ----
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let down = null, rotY = 0.4, rotX = 0;
group.rotation.y = rotY;

const el = renderer.domElement;
el.addEventListener('pointerdown', e => { down = { x: e.clientX, y: e.clientY, moved: 0 }; });
el.addEventListener('pointermove', e => {
  if (!down) return;
  const dx = e.clientX - down.x, dy = e.clientY - down.y;
  down.moved += Math.abs(dx) + Math.abs(dy);
  rotY += dx * 0.008;
  rotX = Math.max(-0.5, Math.min(0.6, rotX + dy * 0.004));
  down.x = e.clientX; down.y = e.clientY;
});
el.addEventListener('pointerup', e => {
  if (down && !(down.moved > 5)) onClick(e);
  down = null;
});

function onClick(e) {
  if (!accept) return;
  const r = el.getBoundingClientRect();
  mouse.x = ((e.clientX - r.left) / r.width) * 2 - 1;
  mouse.y = -((e.clientY - r.top) / r.height) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const hit = raycaster.intersectObjects(cubes)[0];
  if (!hit) return;
  const idx = hit.object.userData.i;
  flash(hit.object);
  if (idx === seq[pos]) {
    pos++; score += 10;
    hud();
    if (pos === seq.length) {
      accept = false; level++; score += 20;
      say('Chính xác! Lên level ' + level);
      setTimeout(nextRound, 900);
    }
  } else {
    lives--; accept = false;
    hud();
    if (lives === 0) { gameOver(); return; }
    say('Sai rồi! Xem lại chuỗi...');
    setTimeout(playSeq, 1000);
  }
}

$('start').addEventListener('click', startGame);

// ---- Vòng lặp vẽ ----
function animate() {
  requestAnimationFrame(animate);
  if (!down && !running) rotY += 0.003;
  group.rotation.y += (rotY - group.rotation.y) * 0.15;
  group.rotation.x += (rotX - group.rotation.x) * 0.15;
  for (const c of cubes) {
    const f = c.userData.flash;
    if (f > 0) {
      c.userData.flash = Math.max(0, f - 0.03);
      c.material.emissive.setHex(0xffffff);
      c.material.emissiveIntensity = f;
      c.scale.setScalar(1 + 0.4 * f);
      c.position.y = 0.5 * f;
    } else {
      c.material.emissive.setHex(0x000000);
      c.scale.setScalar(1);
      c.position.y = 0;
    }
  }
  renderer.render(scene, camera);
}
hud();
animate();
</script>
"""


def render_game():
    st.subheader("🧊 Brain Cubes 3D – Thử thách trí nhớ")
    col1, col2 = st.columns(2)
    with col1:
        grid = st.select_slider("Kích thước lưới", options=[2, 3, 4], value=3)
    with col2:
        speed = st.select_slider(
            "Tốc độ chuỗi (ms)", options=[800, 600, 450, 300], value=600
        )
    html = GAME_HTML.replace("__GRID__", str(grid)).replace("__SPEED__", str(speed))
    components.html(html, height=600)
    st.caption(
        "Cách chơi: ghi nhớ thứ tự khối sáng, rồi bấm lại đúng thứ tự. "
        "Kéo chuột để xoay bàn chơi 3D, bấm nhẹ để chọn khối."
    )


# ---------------------------------------------------------------------------
# CÂU ĐỐ LOGIC (Python thuần)
# ---------------------------------------------------------------------------
def make_question():
    kind = random.choice(["cong", "nhan", "binh_phuong", "fibo", "xen_ke"])
    if kind == "cong":
        a, d = random.randint(1, 20), random.randint(2, 9)
        s = [a + d * i for i in range(5)]
        ans = a + d * 5
        hint = f"Cấp số cộng, công sai {d}"
    elif kind == "nhan":
        a, r = random.randint(1, 4), random.choice([2, 3])
        s = [a * r**i for i in range(5)]
        ans = a * r**5
        hint = f"Cấp số nhân, công bội {r}"
    elif kind == "binh_phuong":
        k = random.randint(1, 5)
        s = [(k + i) ** 2 for i in range(5)]
        ans = (k + 5) ** 2
        hint = "Dãy số chính phương"
    elif kind == "fibo":
        a, b = random.randint(1, 5), random.randint(1, 5)
        s = [a, b]
        while len(s) != 6:
            s.append(s[-1] + s[-2])
        ans = s.pop()
        hint = "Mỗi số bằng tổng hai số liền trước"
    else:
        a, b = random.randint(1, 10), random.randint(1, 10)
        s = [a, b, a + 3, b + 5, a + 6]
        ans = b + 10
        hint = "Hai dãy xen kẽ: +3 và +5"
    options = {ans}
    while len(options) != 4:
        options.add(ans + random.choice([-1, 1]) * random.randint(1, 9))
    options = sorted(options)
    return {"seq": s, "ans": ans, "opts": options, "hint": hint}


def render_quiz():
    st.subheader("🧩 Câu đố tìm quy luật")
    if "q" not in st.session_state:
        st.session_state.q = make_question()
        st.session_state.correct = 0
        st.session_state.total = 0
        st.session_state.feedback = ""
    q = st.session_state.q
    st.markdown("### " + ", ".join(map(str, q["seq"])) + ", **?**")
    choice = st.radio("Số tiếp theo là:", q["opts"], horizontal=True, key="choice")
    c1, c2 = st.columns([1, 5])
    if c1.button("Trả lời"):
        st.session_state.total += 1
        if choice == q["ans"]:
            st.session_state.correct += 1
            st.session_state.feedback = "✅ Chính xác! " + q["hint"]
        else:
            st.session_state.feedback = (
                f"❌ Sai. Đáp án là {q['ans']} ({q['hint']})"
            )
        st.session_state.q = make_question()
        st.rerun()
    if st.session_state.feedback:
        st.info(st.session_state.feedback)
    st.metric(
        "Điểm", f"{st.session_state.correct}/{st.session_state.total}"
    )


# ---------------------------------------------------------------------------
st.title("🧠 Brain Cubes 3D")
tab1, tab2 = st.tabs(["Game 3D", "Câu đố logic"])
with tab1:
    render_game()
with tab2:
    render_quiz()
