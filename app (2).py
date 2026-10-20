import base64
import json
import random
from datetime import date
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Brain Cubes 3D", page_icon="🧠", layout="wide")

BOARD_FILE = Path(__file__).parent / "leaderboard.json"

# ---------------------------------------------------------------------------
# CHỦ ĐỀ GIAO DIỆN
# ---------------------------------------------------------------------------
THEMES = {
    "Ninja Lá": {
        "bg": "radial-gradient(circle at 50% 30%,#1f3a2a,#07110b)",
        "hue": 0.25, "span": 0.3, "sat": 0.6, "light": 0.5, "star": "#9be7a8",
    },
    "Neon": {
        "bg": "radial-gradient(circle at 50% 30%,#2a1b4e,#0a0614)",
        "hue": 0.0, "span": 1.0, "sat": 0.85, "light": 0.55, "star": "#ff7bf0",
    },
    "Hoa Anh Đào": {
        "bg": "radial-gradient(circle at 50% 30%,#4e1b3a,#14060f)",
        "hue": 0.9, "span": 0.15, "sat": 0.65, "light": 0.65, "star": "#ffc2e0",
    },
    "Đại Dương": {
        "bg": "radial-gradient(circle at 50% 30%,#1b2a4e,#0a0e1a)",
        "hue": 0.5, "span": 0.2, "sat": 0.7, "light": 0.5, "star": "#a8d8ff",
    },
}

# ---------------------------------------------------------------------------
# KHUNG HTML CHUNG CỦA CÁC GAME 3D
# ---------------------------------------------------------------------------
PAGE_HTML = """
<div id="wrap" style="position:relative;font-family:sans-serif;color:#fff;">
  <div id="c" style="width:100%;height:560px;border-radius:12px;overflow:hidden;background:#0a0e1a;"></div>
  <div id="hud" style="position:absolute;top:12px;left:16px;font-size:16px;line-height:1.6;
       text-shadow:0 1px 4px #000;pointer-events:none;">__HUD__</div>
  <div id="msg" style="position:absolute;bottom:16px;width:100%;text-align:center;
       font-size:18px;text-shadow:0 1px 4px #000;pointer-events:none;">__MSG__</div>
  <div id="board" style="position:absolute;bottom:56px;left:16px;font-size:13px;line-height:1.5;
       background:rgba(0,0,0,.4);padding:8px 12px;border-radius:8px;pointer-events:none;"></div>
  <button id="start" style="position:absolute;top:12px;right:16px;padding:8px 18px;
       font-size:16px;border:none;border-radius:8px;background:#4f8cff;color:#fff;cursor:pointer;">
    Bắt đầu
  </button>
  <button id="music" style="position:absolute;top:56px;right:16px;padding:8px 18px;
       font-size:16px;border:none;border-radius:8px;background:#2b3a67;color:#fff;cursor:pointer;">
    🔇 Nhạc: Tắt
  </button>
  <input id="pname" placeholder="Tên của bạn" maxlength="12"
       style="position:absolute;top:100px;right:16px;width:130px;padding:6px 8px;
       border-radius:8px;border:none;">
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script>
__JS__
</script>
"""

# ---------------------------------------------------------------------------
# JS DÙNG CHUNG: cảnh 3D, sao nền, hạt nổ, âm thanh, bảng xếp hạng cục bộ
# ---------------------------------------------------------------------------
COMMON_JS = """
const THEME = __THEME__;
const AUDIO_SRC = "__AUDIO__";
const STORE_KEY = "__KEY__";
const $ = id => document.getElementById(id);
const sleep = ms => new Promise(r => setTimeout(r, ms));
function say(t) { $('msg').textContent = t; }

const container = $('c');
const W = container.clientWidth, H = 560;
container.style.background = THEME.bg;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, W / H, 0.1, 100);
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

function placeCamera(n) {
  camera.position.set(0, n * 1.6, n * 2.1);
  camera.lookAt(0, 0, 0);
}

let floor = null;
function addFloor(r) {
  floor = new THREE.Mesh(
    new THREE.CircleGeometry(r, 48),
    new THREE.MeshBasicMaterial({ color: 0x101626 })
  );
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.7;
  group.add(floor);
}

// ---- Bầu trời sao ----
const starPos = [];
for (let i = 0; i !== 300; i++) {
  starPos.push((Math.random() - 0.5) * 60, (Math.random() - 0.5) * 40, -10 - Math.random() * 20);
}
const starGeo = new THREE.BufferGeometry();
starGeo.setAttribute('position', new THREE.Float32BufferAttribute(starPos, 3));
const stars = new THREE.Points(starGeo, new THREE.PointsMaterial({ color: THEME.star, size: 0.15 }));
scene.add(stars);

// ---- Hạt nổ khi trả lời đúng ----
const sparks = [];
function burst(pos, color) {
  for (let i = 0; i !== 14; i++) {
    const m = new THREE.Mesh(
      new THREE.SphereGeometry(0.07, 6, 6),
      new THREE.MeshBasicMaterial({ color: new THREE.Color().copy(color), transparent: true })
    );
    const wp = pos.clone();
    group.localToWorld(wp);
    m.position.copy(wp);
    m.userData = {
      v: new THREE.Vector3((Math.random() - 0.5) * 0.12, Math.random() * 0.12, (Math.random() - 0.5) * 0.12),
      life: 1
    };
    scene.add(m);
    sparks.push(m);
  }
}
function stepSparks() {
  for (let i = sparks.length - 1; i >= 0; i--) {
    const s = sparks[i];
    s.position.add(s.userData.v);
    s.userData.v.y -= 0.004;
    s.userData.life -= 0.025;
    s.material.opacity = Math.max(0, s.userData.life);
    if (!(s.userData.life > 0)) {
      scene.remove(s);
      s.geometry.dispose();
      s.material.dispose();
      sparks.splice(i, 1);
    }
  }
}

// ---- Âm thanh ----
const SCALE = [220, 246.94, 261.63, 329.63, 349.23, 440, 493.88, 523.25];
let actx = null, bgm = null, timer = null, musicOn = false;
function ensureCtx() {
  try {
    actx = actx || new (window.AudioContext || window.webkitAudioContext)();
    if (actx.state === 'suspended') actx.resume();
  } catch (e) {}
}
function pluck(freq, t, vol) {
  const o = actx.createOscillator(), g = actx.createGain();
  o.type = 'triangle'; o.frequency.value = freq;
  g.gain.setValueAtTime(vol, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + 0.9);
  o.connect(g); g.connect(actx.destination);
  o.start(t); o.stop(t + 1);
}
function drum(t, freq, vol) {
  const o = actx.createOscillator(), g = actx.createGain();
  o.type = 'sine';
  o.frequency.setValueAtTime(freq, t);
  o.frequency.exponentialRampToValueAtTime(40, t + 0.3);
  g.gain.setValueAtTime(vol, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + 0.35);
  o.connect(g); g.connect(actx.destination);
  o.start(t); o.stop(t + 0.4);
}
function note(i) {
  ensureCtx();
  if (actx) pluck(SCALE[i % SCALE.length] * 2, actx.currentTime, 0.2);
}
function chime() {
  ensureCtx();
  if (!actx) return;
  const t = actx.currentTime;
  pluck(660, t, 0.18);
  pluck(880, t + 0.1, 0.18);
}
function buzz() {
  ensureCtx();
  if (!actx) return;
  const t = actx.currentTime;
  const o = actx.createOscillator(), g = actx.createGain();
  o.type = 'sawtooth';
  o.frequency.setValueAtTime(140, t);
  o.frequency.exponentialRampToValueAtTime(70, t + 0.3);
  g.gain.setValueAtTime(0.15, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + 0.3);
  o.connect(g); g.connect(actx.destination);
  o.start(t); o.stop(t + 0.35);
}
function startSynth() {
  ensureCtx();
  if (!actx || timer) return;
  let step = 0, idx = 3;
  const stepMs = 60000 / 96 / 2;
  timer = setInterval(() => {
    const t = actx.currentTime;
    if (step % 8 === 0) drum(t, 90, 0.45);
    if (step % 8 === 4) drum(t, 70, 0.3);
    if (Math.random() > 0.35) {
      const move = [-2, -1, 0, 1, 2][Math.floor(Math.random() * 5)];
      idx = Math.max(0, Math.min(SCALE.length - 1, idx + move));
      pluck(SCALE[idx], t, 0.12);
    }
    step++;
  }, stepMs);
}
function toggleMusic() {
  musicOn = !musicOn;
  if (musicOn) {
    if (AUDIO_SRC) {
      bgm = bgm || new Audio(AUDIO_SRC);
      bgm.loop = true; bgm.volume = 0.5;
      bgm.play().catch(() => {});
    } else {
      startSynth();
    }
  } else {
    if (bgm) bgm.pause();
    if (timer) { clearInterval(timer); timer = null; }
  }
  $('music').textContent = musicOn ? '🔊 Nhạc: Bật' : '🔇 Nhạc: Tắt';
}
$('music').addEventListener('click', toggleMusic);

// ---- Bảng xếp hạng trên máy này (localStorage) ----
const nameEl = $('pname');
try { nameEl.value = localStorage.getItem('bc_name') || ''; } catch (e) {}
nameEl.addEventListener('change', () => {
  try { localStorage.setItem('bc_name', nameEl.value); } catch (e) {}
});
function playerName() {
  return (nameEl.value || 'Ninja').trim().slice(0, 12) || 'Ninja';
}
function loadBoard() {
  try { return JSON.parse(localStorage.getItem(STORE_KEY) || '[]'); } catch (e) { return []; }
}
function bestScore() {
  const b = loadBoard();
  return b.length === 0 ? 0 : b[0].s;
}
function renderBoard() {
  const b = loadBoard(), el = $('board');
  el.textContent = '';
  const t = document.createElement('div');
  t.style.fontWeight = 'bold';
  t.textContent = '🏆 Top 5 (máy này)';
  el.appendChild(t);
  if (b.length === 0) {
    const e = document.createElement('div');
    e.textContent = 'Chưa có điểm';
    el.appendChild(e);
  }
  b.forEach((r, i) => {
    const d = document.createElement('div');
    d.textContent = (i + 1) + '. ' + r.n + ' – ' + r.s;
    el.appendChild(d);
  });
}
function saveScore(name, sc) {
  const b = loadBoard();
  b.push({ n: name, s: sc });
  b.sort((x, y) => y.s - x.s);
  try { localStorage.setItem(STORE_KEY, JSON.stringify(b.slice(0, 5))); } catch (e) {}
  renderBoard();
}
renderBoard();

// ---- Điều khiển: kéo để xoay, bấm để chọn ----
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();
let down = null, rotY = 0.4, rotX = 0, clickHandler = null, running = false;
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
  if (down && !(down.moved > 5) && clickHandler) clickHandler(e);
  down = null;
});
function pick(e, objs) {
  const r = el.getBoundingClientRect();
  mouse.x = ((e.clientX - r.left) / r.width) * 2 - 1;
  mouse.y = -((e.clientY - r.top) / r.height) * 2 + 1;
  raycaster.setFromCamera(mouse, camera);
  const hit = raycaster.intersectObjects(objs)[0];
  return hit ? hit.object : null;
}

// ---- Vòng lặp vẽ ----
let clock = 0, shake = 0;
function animateCommon() {
  requestAnimationFrame(animateCommon);
  clock += 0.016;
  if (!down && !running) rotY += 0.003;
  group.rotation.y += (rotY - group.rotation.y) * 0.15;
  group.rotation.x += (rotX - group.rotation.x) * 0.15;
  group.position.x = Math.sin(clock * 60) * 0.12 * shake;
  shake = shake * 0.9;
  stars.rotation.z += 0.0004;
  stepSparks();
  if (typeof onFrame === 'function') onFrame();
  renderer.render(scene, camera);
}
"""

# ---------------------------------------------------------------------------
# GAME 1: GHI NHỚ CHUỖI KHỐI
# ---------------------------------------------------------------------------
MEMORY_JS = """
const GRID = __GRID__, SPEED = __SPEED__;
placeCamera(GRID);

const cubes = [];
const gap = 1.35;
const offset = (GRID - 1) * gap / 2;
for (let i = 0; i !== GRID * GRID; i++) {
  const x = i % GRID, z = Math.floor(i / GRID);
  const hue = (THEME.hue + (i / (GRID * GRID)) * THEME.span) % 1;
  const mat = new THREE.MeshStandardMaterial({
    color: new THREE.Color().setHSL(hue, THEME.sat, THEME.light),
    emissive: 0x000000, metalness: 0.2, roughness: 0.4
  });
  const cube = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), mat);
  cube.position.set(x * gap - offset, 0, z * gap - offset);
  cube.userData = { i: i, flash: 0 };
  group.add(cube);
  cubes.push(cube);
}
addFloor(GRID * 1.5);

let seq = [], pos = 0, level = 1, score = 0, lives = 3, accept = false;
function hud() {
  $('lv').textContent = level; $('sc').textContent = score;
  $('li').textContent = lives; $('bs').textContent = bestScore();
}
function flash(c) {
  c.userData.flash = 1;
  note(c.userData.i);
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
  ensureCtx();
  seq = []; level = 1; score = 0; lives = 3; running = true;
  $('start').textContent = 'Chơi lại';
  await nextRound();
}
function gameOver() {
  running = false; accept = false;
  saveScore(playerName(), score);
  hud();
  say('Hết mạng! Điểm của bạn: ' + score + '. Bấm "Chơi lại".');
}

clickHandler = function (e) {
  if (!accept) return;
  const o = pick(e, cubes);
  if (!o) return;
  flash(o);
  if (o.userData.i === seq[pos]) {
    pos++; score += 10;
    burst(o.position, o.material.color);
    hud();
    if (pos === seq.length) {
      accept = false; level++; score += 20;
      chime();
      say('Chính xác! Lên level ' + level);
      setTimeout(nextRound, 900);
    }
  } else {
    lives--; accept = false; shake = 1; buzz();
    hud();
    if (lives === 0) { gameOver(); return; }
    say('Sai rồi! Xem lại chuỗi...');
    setTimeout(playSeq, 1000);
  }
};
$('start').addEventListener('click', startGame);

function onFrame() {
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
}
hud();
animateCommon();
"""

# ---------------------------------------------------------------------------
# GAME 2: TÌM KHỐI KHÁC BIỆT (chạy đua với thời gian)
# ---------------------------------------------------------------------------
ODD_JS = """
const TIME0 = __TIME__;
let level = 1, score = 0, timeLeft = TIME0, oddIdx = 0, accept = false, timerId = null;
let cubes = [];

function hud() {
  $('lv').textContent = level; $('sc').textContent = score;
  $('tm').textContent = Math.ceil(timeLeft); $('bs').textContent = bestScore();
}
function clearCubes() {
  for (const c of cubes) {
    group.remove(c);
    c.geometry.dispose();
    c.material.dispose();
  }
  cubes = [];
}
function buildLevel() {
  clearCubes();
  const n = Math.min(6, 2 + Math.ceil(level / 2));
  placeCamera(n);
  if (!floor) addFloor(5);
  floor.scale.setScalar(n * 1.5 / 5);
  const hue = Math.random();
  const diff = Math.max(0.035, 0.24 - level * 0.016);
  const sign = Math.random() > 0.5 ? 1 : -1;
  oddIdx = Math.floor(Math.random() * n * n);
  const gap = 1.35, offset = (n - 1) * gap / 2;
  for (let i = 0; i !== n * n; i++) {
    const light = i === oddIdx ? 0.5 + sign * diff : 0.5;
    const mat = new THREE.MeshStandardMaterial({
      color: new THREE.Color().setHSL(hue, 0.7, light), metalness: 0.2, roughness: 0.4
    });
    const cube = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), mat);
    cube.position.set((i % n) * gap - offset, 0, Math.floor(i / n) * gap - offset);
    cube.userData = { i: i };
    group.add(cube);
    cubes.push(cube);
  }
}
function endGame() {
  if (timerId) { clearInterval(timerId); timerId = null; }
  running = false; accept = false;
  saveScore(playerName(), score);
  hud();
  say('Hết giờ! Điểm: ' + score + '. Bấm "Chơi lại".');
}
function tick() {
  timeLeft = Math.max(0, timeLeft - 0.1);
  hud();
  if (!(timeLeft > 0)) endGame();
}
function startGame() {
  ensureCtx();
  level = 1; score = 0; timeLeft = TIME0; running = true; accept = true;
  $('start').textContent = 'Chơi lại';
  if (timerId) clearInterval(timerId);
  timerId = setInterval(tick, 100);
  buildLevel();
  hud();
  say('Tìm khối có màu khác biệt và bấm vào nó!');
}

clickHandler = function (e) {
  if (!accept) return;
  const o = pick(e, cubes);
  if (!o) return;
  if (o.userData.i === oddIdx) {
    score += 10 + level; timeLeft += 1.5; level++;
    burst(o.position, o.material.color);
    chime();
    hud();
    buildLevel();
  } else {
    timeLeft = Math.max(0, timeLeft - 4); shake = 1; buzz();
    hud();
    if (!(timeLeft > 0)) endGame();
  }
};
$('start').addEventListener('click', startGame);

function onFrame() {
  for (const c of cubes) {
    c.position.y = Math.sin(clock * 2 + c.userData.i) * 0.06;
  }
}
buildLevel();
hud();
animateCommon();
"""

MEMORY_HUD = (
    'Level: <b id="lv">1</b> &nbsp; Điểm: <b id="sc">0</b> &nbsp; '
    'Mạng: <b id="li">3</b> &nbsp; Kỷ lục: <b id="bs">0</b>'
)
ODD_HUD = (
    'Level: <b id="lv">1</b> &nbsp; Điểm: <b id="sc">0</b> &nbsp; '
    'Thời gian: <b id="tm">45</b>s &nbsp; Kỷ lục: <b id="bs">0</b>'
)


def build_game(game_js, hud, msg, key, theme, audio_src, **params):
    html = PAGE_HTML.replace("__HUD__", hud).replace("__MSG__", msg)
    html = html.replace("__JS__", COMMON_JS + game_js)
    html = html.replace("__THEME__", json.dumps(theme)).replace("__KEY__", key)
    for name, value in params.items():
        html = html.replace("__" + name.upper() + "__", str(value))
    return html.replace("__AUDIO__", audio_src)


def get_audio_src(audio_file):
    if audio_file is None:
        return ""
    data = audio_file.getvalue()
    if len(data) > 5 * 1024 * 1024:
        st.sidebar.warning("File quá lớn (tối đa 5MB), đang dùng nhạc mặc định.")
        return ""
    ext = audio_file.name.rsplit(".", 1)[-1].lower()
    mime = {"mp3": "audio/mpeg", "ogg": "audio/ogg", "wav": "audio/wav"}[ext]
    return f"data:{mime};base64," + base64.b64encode(data).decode()


# ---------------------------------------------------------------------------
# CÂU ĐỐ LOGIC
# ---------------------------------------------------------------------------
ROUND = 10


def make_options(ans):
    opts = {ans}
    while len(opts) != 4:
        cand = ans + random.choice([-1, 1]) * random.randint(1, 9)
        if cand > 0:
            opts.add(cand)
    return sorted(opts)


def q_sequence():
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
    return {
        "cat": "Dãy số",
        "prompt": "### " + ", ".join(map(str, s)) + ", **?**",
        "ans": ans,
        "opts": make_options(ans),
        "hint": hint,
    }


def q_odd_number():
    k = random.randint(2, 9)
    nums = [k * m for m in random.sample(range(1, 13), 3)]
    odd = k * random.randint(1, 12) + random.randint(1, k - 1)
    opts = nums + [odd]
    random.shuffle(opts)
    return {
        "cat": "Số khác loại",
        "prompt": "### " + ", ".join(map(str, opts))
        + "\n\nSố nào **không** cùng quy luật với ba số còn lại?",
        "ans": odd,
        "opts": opts,
        "hint": f"Ba số kia đều là bội của {k}",
    }


def q_missing_op():
    op = random.choice(["+", "-", "×"])
    if op == "+":
        a, b = random.randint(2, 20), random.randint(2, 12)
        c = a + b
    elif op == "-":
        b = random.randint(2, 12)
        a = b + random.randint(1, 15)
        c = a - b
    else:
        a, b = random.randint(2, 9), random.randint(2, 9)
        c = a * b
    return {
        "cat": "Phép tính thiếu",
        "prompt": f"### {a} {op} **?** = {c}",
        "ans": b,
        "opts": make_options(b),
        "hint": f"{a} {op} {b} = {c}",
    }


def q_matrix():
    op = random.choice(["+", "×"])
    rows = []
    for _ in range(3):
        if op == "+":
            x, y = random.randint(1, 9), random.randint(1, 9)
            rows.append([x, y, x + y])
        else:
            x, y = random.randint(1, 5), random.randint(1, 5)
            rows.append([x, y, x * y])
    ans = rows[2][2]
    lines = ["  ".join(f"{v:>2}" for v in r) for r in rows[:2]]
    lines.append(f"{rows[2][0]:>2}  {rows[2][1]:>2}   ?")
    return {
        "cat": "Ma trận số",
        "prompt": "```\n" + "\n".join(lines) + "\n```",
        "ans": ans,
        "opts": make_options(ans),
        "hint": "Cột 3 = cột 1 " + op + " cột 2",
    }


def q_letters():
    step = random.randint(1, 3)
    start = random.randint(0, 25 - step * 5)
    letters = [chr(65 + start + step * i) for i in range(5)]
    ans = chr(65 + start + step * 5)
    opts = {ans}
    while len(opts) != 4:
        opts.add(chr(65 + random.randint(0, 25)))
    return {
        "cat": "Chuỗi chữ cái",
        "prompt": "### " + ", ".join(letters) + ", **?**",
        "ans": ans,
        "opts": sorted(opts),
        "hint": f"Mỗi chữ cái cách nhau {step} vị trí trong bảng chữ cái",
    }


CATS = {
    "Dãy số": q_sequence,
    "Số khác loại": q_odd_number,
    "Phép tính thiếu": q_missing_op,
    "Ma trận số": q_matrix,
    "Chuỗi chữ cái": q_letters,
}


def new_question(cat):
    if cat != "Tất cả":
        return CATS[cat]()
    return random.choice(list(CATS.values()))()


def reset_round(cat):
    s = st.session_state
    s.cat = cat
    s.q = new_question(cat)
    s.idx = 0
    s.correct = 0
    s.feedback = ""
    s.finished = False
    s.saved = False


# ---- Bảng xếp hạng câu đố (lưu trên máy chủ, dùng chung mọi người chơi) ----
def load_board():
    try:
        return json.loads(BOARD_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []


def add_score(name, score, cat):
    board = load_board()
    board.append(
        {"Tên": name[:16], "Điểm": score, "Loại": cat, "Ngày": date.today().isoformat()}
    )
    board.sort(key=lambda r: r["Điểm"], reverse=True)
    try:
        BOARD_FILE.write_text(
            json.dumps(board[:50], ensure_ascii=False), encoding="utf-8"
        )
    except Exception:
        st.warning("Không ghi được file xếp hạng trên máy chủ.")


def render_quiz():
    st.subheader("🧩 Câu đố logic")
    cat = st.selectbox("Loại câu đố", ["Tất cả"] + list(CATS.keys()))
    if "q" not in st.session_state or st.session_state.get("cat") != cat:
        reset_round(cat)
    s = st.session_state

    if s.finished:
        st.success(f"Hoàn thành vòng chơi! Điểm: {s.correct}/{ROUND}")
        name = st.text_input("Tên của bạn", value="Ninja", max_chars=16)
        c1, c2 = st.columns(2)
        if c1.button("💾 Lưu điểm", disabled=s.saved):
            add_score(name.strip() or "Ẩn danh", s.correct, cat)
            s.saved = True
            st.rerun()
        if c2.button("🔁 Vòng mới"):
            reset_round(cat)
            st.rerun()
        if s.saved:
            st.info("Đã lưu vào bảng xếp hạng! Xem ở tab 🏆 Xếp hạng.")
        return

    st.progress(s.idx / ROUND, text=f"Câu {s.idx + 1}/{ROUND}  •  Đúng: {s.correct}")
    if s.feedback:
        st.info(s.feedback)
    q = s.q
    st.caption(q["cat"])
    st.markdown(q["prompt"])
    choice = st.radio(
        "Chọn đáp án:", q["opts"], horizontal=True, key=f"choice_{s.idx}"
    )
    if st.button("Trả lời"):
        if choice == q["ans"]:
            s.correct += 1
            s.feedback = "✅ Chính xác! " + q["hint"]
        else:
            s.feedback = f"❌ Sai. Đáp án là {q['ans']} ({q['hint']})"
        s.idx += 1
        if s.idx == ROUND:
            s.finished = True
        else:
            s.q = new_question(cat)
        st.rerun()


def render_board():
    st.subheader("🏆 Bảng xếp hạng câu đố logic")
    board = load_board()
    if not board:
        st.info("Chưa có ai ghi điểm. Hãy chơi một vòng câu đố và lưu điểm!")
    else:
        st.dataframe(board[:10], hide_index=True)
    st.caption(
        "Điểm của hai game 3D được lưu riêng trên từng thiết bị "
        "(Top 5 hiển thị ngay trong game). Bảng này dùng chung cho mọi người "
        "chơi câu đố; trên Streamlit Cloud dữ liệu có thể bị xoá khi app khởi động lại."
    )


# ---------------------------------------------------------------------------
# GIAO DIỆN CHÍNH
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Cài đặt")
    theme_name = st.selectbox("Chủ đề giao diện", list(THEMES.keys()))
    audio_file = st.file_uploader(
        "🎵 Nhạc nền của bạn (mp3/ogg/wav, tối đa 5MB). Bỏ trống để dùng nhạc mặc định.",
        type=["mp3", "ogg", "wav"],
    )
theme = THEMES[theme_name]
audio_src = get_audio_src(audio_file)

st.title("🧠 Brain Cubes 3D")
tab1, tab2, tab3, tab4 = st.tabs(
    ["🧊 Ghi nhớ 3D", "🔍 Tìm khối khác 3D", "🧩 Câu đố logic", "🏆 Xếp hạng"]
)

with tab1:
    st.subheader("🧊 Ghi nhớ chuỗi khối")
    c1, c2 = st.columns(2)
    with c1:
        grid = st.select_slider("Kích thước lưới", options=[2, 3, 4], value=3)
    with c2:
        speed = st.select_slider(
            "Tốc độ chuỗi (ms)", options=[800, 600, 450, 300], value=600
        )
    components.html(
        build_game(
            MEMORY_JS,
            MEMORY_HUD,
            'Bấm "Bắt đầu" rồi ghi nhớ thứ tự các khối sáng lên',
            "bc_board_memory",
            theme,
            audio_src,
            grid=grid,
            speed=speed,
        ),
        height=600,
    )
    st.caption(
        "Ghi nhớ thứ tự khối sáng, rồi bấm lại đúng thứ tự. Kéo chuột để xoay bàn chơi 3D, "
        "bấm nhẹ để chọn khối. Bấm nút 'Nhạc' trong game để bật/tắt nhạc nền."
    )

with tab2:
    st.subheader("🔍 Tìm khối có màu khác biệt")
    time0 = st.select_slider("Thời gian ban đầu (giây)", options=[30, 45, 60], value=45)
    components.html(
        build_game(
            ODD_JS,
            ODD_HUD.replace(">45<", ">" + str(time0) + "<"),
            'Bấm "Bắt đầu", tìm khối có màu hơi khác rồi bấm vào nó',
            "bc_board_odd",
            theme,
            audio_src,
            time=time0,
        ),
        height=600,
    )
    st.caption(
        "Đúng: +điểm và +1.5 giây. Sai: -4 giây. Càng lên level, lưới càng lớn và "
        "màu càng giống nhau. Kéo chuột để xoay bàn chơi."
    )

with tab3:
    render_quiz()

with tab4:
    render_board()
