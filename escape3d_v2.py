"""
⏳ ESCAPE TIME 3D — BẢN 2: GIẢI ĐỐ BẰNG HÀNH ĐỘNG (kiểu Minecraft, chạy trên Streamlit)
=======================================================================================
Cài đặt:  pip install "streamlit>=1.30"
Chạy:     streamlit run escape3d_v2.py

Game dùng three.js (tải từ cdnjs) nhúng vào Streamlit, nên máy cần có mạng.

3 căn phòng, 3 kiểu đố hành động (không nhập mã):
  1. Đẩy thùng  : đẩy 2 thùng gỗ lên 2 ô xanh trên sàn (bố cục luôn giải được, có kiểm tra bằng thuật toán)
  2. Trí nhớ đèn: xem dãy đèn màu sáng trên tường rồi bước lên các ô màu theo đúng thứ tự
  3. Cầu ô nền  : ghi nhớ đường đi an toàn, bước sai sẽ bị đưa về đầu và bị phạt giờ

Điều khiển
  Điện thoại : cần trái = đi · kéo ngón tay lên màn hình = nhìn · ⬆ nhảy · ✋ tương tác
               ↺ xếp lại thùng · 💡 gợi ý · 📋 nhiệm vụ · 👁 đổi góc nhìn
  Máy tính   : W A S D = đi · Space = nhảy · kéo chuột trái = nhìn · E = tương tác
               R = xếp lại thùng · H = gợi ý · I = nhiệm vụ · V = đổi góc nhìn · Esc = đóng bảng
"""

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Escape Time 3D - Bản 2",
    page_icon="⏳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
header[data-testid="stHeader"], footer, #MainMenu {display:none !important}
.block-container {padding:0 !important; max-width:100% !important}
iframe {height: calc(100vh - 6px) !important; min-height: 460px; border:0}
</style>
""",
    unsafe_allow_html=True,
)

HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<style>
html,body{margin:0;height:100%;overflow:hidden;background:#1b2330;
  font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  -webkit-user-select:none;user-select:none;touch-action:none;-webkit-touch-callout:none}
canvas{display:block;touch-action:none}
.ui{position:absolute;color:#fff;text-shadow:0 1px 3px #000}
#timer{top:8px;left:50%;transform:translateX(-50%);font-size:26px;font-weight:800;
  letter-spacing:2px;padding:2px 16px;border-radius:12px;background:rgba(0,0,0,.45);
  font-variant-numeric:tabular-nums;text-shadow:none;white-space:nowrap}
#timer.ok{color:#5be38a}#timer.warn{color:#ffd24a}
#timer.danger{color:#ff5a4a;animation:pulse 1s infinite}
@keyframes pulse{50%{opacity:.55}}
#toast{top:56px;left:50%;transform:translateX(-50%);width:max-content;max-width:80%;
  text-align:center;font-size:14px;background:rgba(0,0,0,.62);padding:8px 12px;
  border-radius:10px;display:none;line-height:1.35}
#prompt{right:16px;bottom:190px;font-size:13px;background:rgba(0,0,0,.55);padding:4px 10px;
  border-radius:10px;display:none;max-width:46%;text-align:right}
#compass{left:8px;top:62px;font-size:13px;background:rgba(0,0,0,.45);padding:3px 9px;border-radius:10px}
.btn{position:absolute;border-radius:50%;background:rgba(0,0,0,.45);
  border:2px solid rgba(255,255,255,.75);color:#fff;display:flex;align-items:center;
  justify-content:center;font-size:22px;touch-action:none;text-shadow:none}
.btn:active,.btn.on{background:rgba(255,255,255,.35)}
.btn small{font-size:11px;margin-left:2px;font-weight:700}
#joy{left:18px;bottom:24px;width:124px;height:124px;border-radius:50%;
  background:rgba(255,255,255,.16);border:2px solid rgba(255,255,255,.5);touch-action:none}
#knob{position:absolute;left:36px;top:36px;width:52px;height:52px;border-radius:50%;
  background:rgba(255,255,255,.55);pointer-events:none}
#bJump{right:20px;bottom:26px;width:62px;height:62px;font-size:24px}
#bAct{right:20px;bottom:100px;width:76px;height:76px;font-size:30px;opacity:.55}
#bAct.near{opacity:1;background:rgba(255,200,0,.55);border-color:#ffd24a;
  box-shadow:0 0 14px #ffd24a;animation:glow 1s infinite}
@keyframes glow{50%{box-shadow:0 0 4px #ffd24a}}
#bReset{left:34px;bottom:160px;width:48px;height:48px;font-size:24px;display:none}
#bInv{top:8px;left:8px;width:46px;height:46px}
#bHint{top:8px;right:8px;width:50px;height:46px;border-radius:23px}
#bView{top:62px;right:8px;width:46px;height:46px}
#overlay,#panel{position:absolute;inset:0;display:none;align-items:center;justify-content:center;
  background:rgba(8,12,20,.72);z-index:10;padding:12px;box-sizing:border-box}
.card{background:#1f2937;color:#fff;border:2px solid #4b5b73;border-radius:14px;
  padding:16px 18px;width:100%;max-width:430px;max-height:92%;overflow:auto;
  box-sizing:border-box;font-size:15px;line-height:1.45;touch-action:pan-y;text-shadow:none}
.card h2{margin:0 0 8px;font-size:20px}
.card p{margin:6px 0}
.cap{opacity:.7;font-size:13px}
.pb{display:block;width:100%;margin-top:10px;padding:11px;font-size:16px;font-weight:700;
  border:0;border-radius:10px;background:#f5b72d;color:#222}
.pb.alt{background:#3a4a63;color:#fff}
.hint{color:#ffd24a}
.chk{margin:6px 0}
#pClose{float:right;background:none;border:0;color:#fff;font-size:22px;margin:-6px -6px 0 0}
</style>
</head>
<body>
<div id="timer" class="ui ok">--:--</div>
<div id="toast" class="ui"></div>
<div id="prompt" class="ui"></div>
<div id="compass" class="ui">🧭 Đông</div>
<div id="joy" class="ui"><div id="knob"></div></div>
<div id="bJump" class="btn">⬆</div>
<div id="bAct" class="btn">✋</div>
<div id="bReset" class="btn">↺</div>
<div id="bInv" class="btn">📋</div>
<div id="bHint" class="btn">💡<small id="hn">0</small></div>
<div id="bView" class="btn">👁</div>

<div id="panel"><div class="card"><button id="pClose">✕</button><h2 id="pTitle"></h2><div id="pBody"></div></div></div>
<div id="overlay"><div class="card" id="ovBody"></div></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
  onerror="document.body.insertAdjacentHTML('beforeend','<div style=&quot;position:absolute;top:40%;width:100%;text-align:center;color:#fff&quot;>❌ Không tải được three.js. Hãy kiểm tra mạng rồi tải lại trang.</div>')"></script>
<script>
(function(){
if(typeof THREE==='undefined')return;
const $=id=>document.getElementById(id);
const fmt=s=>{s=Math.max(0,Math.floor(s));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');};
function rnd(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;
  let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;
  return((t^t>>>14)>>>0)/4294967296;};}
const R=rnd((Math.random()*1e9)|0);
const rint=n=>Math.floor(R()*n);

/* độ khó: [giây, gợi ý, hệ số điểm, mô tả, độ dài dãy đèn, số nước tối thiểu của đố thùng, bước lạc tối đa của đường đi] */
const DIFF={'Dễ':[900,4,1,'15 phút · 4 gợi ý',3,10,1],'Thường':[600,3,1.5,'10 phút · 3 gợi ý',4,14,2],'Khó':[420,2,2,'7 phút · 2 gợi ý',5,20,3]};
const HINT_PEN=30,WRONG_PEN=8,FALL_PEN=10;
const LAMP=['🔴 Đỏ','🟢 Lục','🟡 Vàng','🔵 Xanh dương'];
const DIRN=['Đông ➡️','Tây ⬅️','Nam ⬇️','Bắc ⬆️'];

/* ============================ THẾ GIỚI ============================ */
const W=48,H=10,D=13,CS=16,NCX=W/CS,NCZ=1;
const world=new Uint8Array(W*H*D);
const I=(x,y,z)=>x+W*(z+D*y);
const inb=(x,y,z)=>x>=0&&x<W&&z>=0&&z<D&&y>=0&&y<H;
const get=(x,y,z)=>inb(x,y,z)?world[I(x,y,z)]:0;
const set=(x,y,z,v)=>{if(inb(x,y,z))world[I(x,y,z)]=v;};
function box(x0,y0,z0,x1,y1,z1,id){for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++)for(let x=x0;x<=x1;x++)set(x,y,z,id);}
/* id: 1 ván, 2 tường, 3 trần, 4 đèn trần, 8 gạch trắng, 14 cửa, 20 cỏ, 21 đất, 22 thân cây, 23 lá,
   24 thùng, 25 ô đích tắt, 26 ô đích sáng, 27 thùng sáng(gợi ý), 28 ô nền, 29 ô nền vàng, 30 ô nền xanh, 31 ô nền đỏ,
   32-35 đèn tắt, 36-39 đèn sáng, 40-43 ô bấm màu, 44 bảng điều khiển, 45 cần gạt, 46 biển */
box(0,0,0,W-1,0,D-1,21);
const FLOOR=[1,8,1];
for(let r=0;r<3;r++){
  const x0=r*12;
  box(x0,1,0,x0+12,1,12,FLOOR[r]);
  box(x0,2,0,x0+12,6,12,2);
  box(x0+1,2,1,x0+11,6,11,0);
  box(x0,7,0,x0+12,7,12,3);
  for(const rx of [3,6,9])for(const rz of [3,6,9])set(x0+rx,7,rz,4);
}
box(25,1,11,35,6,11,2);               // phòng 3 chỉ cao tới z=10
const DOORS=[{x:12,z:6},{x:24,z:6},{x:36,z:6}];
for(const d of DOORS){set(d.x,2,d.z,14);set(d.x,3,d.z,14);}
box(37,1,0,W-1,1,D-1,20);
set(5,3,0,46);set(6,3,0,46);          // biển phòng 1
set(12,3,3,44);set(12,2,3,44);       // bảng điều khiển phòng 2
set(26,3,0,45);set(26,2,0,45);       // cần gạt phòng 3
for(let i=0;i<4;i++)box(13+3*i,3,0,14+3*i,4,0,32+i);          // 4 đèn tường
for(let i=0;i<4;i++)box(13+3*i,1,8,14+3*i,1,9,40+i);          // 4 ô bấm
box(25,1,1,26,1,10,1);box(35,1,1,35,1,10,1);                  // bục đầu và cuối
box(27,1,1,34,1,10,28);                                      // 8x10 ô nền (4 cột × 5 hàng, mỗi ô 2x2)
function tree(x,z){
  const h=1,th=4+rint(2);
  for(let i=1;i<=th;i++)set(x,h+i,z,22);
  for(let dy=th-1;dy<=th+1;dy++){
    const r=dy>=th+1?1:2;
    for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dz++){
      if(Math.abs(dx)===r&&Math.abs(dz)===r&&dy<th+1&&R()<.5)continue;
      if(!get(x+dx,h+dy,z+dz))set(x+dx,h+dy,z+dz,23);
    }
  }
}
tree(41,3);tree(44,9);tree(40,10);tree(45,2);

/* ============================ TEXTURE ============================ */
const TS=16,COLS=8,ROWS=6;
const atlas=document.createElement('canvas');
atlas.width=TS*COLS;atlas.height=TS*ROWS;
const ac=atlas.getContext('2d');
const cl=v=>Math.max(0,Math.min(255,v|0));
function fillTile(t,c,v,fn){
  for(let y=0;y<TS;y++)for(let x=0;x<TS;x++){
    let q=c;if(fn){const r=fn(x,y);if(r)q=r;}
    const k=1+(Math.random()-.5)*v;
    ac.fillStyle='rgb('+cl(q[0]*k)+','+cl(q[1]*k)+','+cl(q[2]*k)+')';
    ac.fillRect((t%COLS)*TS+x,((t/COLS)|0)*TS+y,1,1);
  }
}
const edge=(x,y,n)=>x<n||y<n||x>15-n||y>15-n;
const GRASS=[96,160,56],DIRT=[134,96,67];
fillTile(0,[162,130,78],.12,(x,y)=>(y%4===3)?[118,90,50]:null);
fillTile(1,[122,122,128],.15,(x,y)=>(y%8===7||(x+(((y>>3)&1)*8))%16===0)?[78,78,84]:null);
fillTile(2,[62,46,36],.15,(x,y)=>(y%4===3)?[44,32,24]:null);
fillTile(3,[255,220,120],.12,(x,y)=>((x+y)%5===0)?[255,245,185]:null);
fillTile(7,[226,231,236],.06,(x,y)=>(x%8===0||y%8===0)?[190,196,202]:null);
fillTile(13,[150,150,156],.08,(x,y)=>{
  if(x===3&&(y===8||y===9))return[240,200,60];
  return(x%4===1||y%8===0)?[98,98,104]:null;});
fillTile(19,GRASS,.25);
fillTile(20,DIRT,.25,(x,y)=>y<4?GRASS:(y===4&&x%3===0?GRASS:null));
fillTile(21,DIRT,.3);
fillTile(22,[102,81,51],.2,(x,y)=>x%4===0?[78,60,36]:null);
fillTile(23,[48,120,40],.45,(x,y)=>((x*5+y*3)%7===0)?[28,88,26]:null);
const xmark=(x,y)=>(Math.abs(x-y)<2||Math.abs(x+y-15)<2);
fillTile(24,[176,130,60],.12,(x,y)=>edge(x,y,2)?[110,74,30]:(xmark(x,y)?[130,90,40]:null));
fillTile(25,[50,98,52],.08,(x,y)=>edge(x,y,2)?[24,60,28]:((x>5&&x<10&&y>5&&y<10)?[70,130,72]:null));
fillTile(26,[120,255,130],.06,(x,y)=>edge(x,y,2)?[60,190,70]:null);
fillTile(27,[255,215,90],.08,(x,y)=>edge(x,y,2)?[200,120,20]:(xmark(x,y)?[230,160,30]:null));
fillTile(28,[150,150,158],.08,(x,y)=>edge(x,y,1)?[100,100,108]:null);
fillTile(29,[255,215,80],.06,(x,y)=>edge(x,y,1)?[205,150,20]:null);
fillTile(30,[90,200,110],.06,(x,y)=>edge(x,y,1)?[40,130,60]:null);
fillTile(31,[225,70,60],.06,(x,y)=>edge(x,y,1)?[140,30,30]:null);
const DIM=[[100,32,32],[32,90,44],[110,98,32],[32,54,112]];
const BRI=[[255,70,70],[80,255,110],[255,235,70],[90,150,255]];
const PAD=[[205,60,60],[60,185,80],[225,200,50],[60,110,220]];
for(let i=0;i<4;i++){
  fillTile(32+i,DIM[i],.1,(x,y)=>edge(x,y,2)?[20,20,24]:null);
  fillTile(36+i,BRI[i],.05,(x,y)=>edge(x,y,2)?[255,255,255]:(Math.hypot(x-7.5,y-7.5)<4?[255,255,255]:null));
  fillTile(40+i,PAD[i],.1,(x,y)=>edge(x,y,1)?[30,30,30]:(Math.hypot(x-7.5,y-7.5)<4.5?[255,255,255]:null));
}
fillTile(44,[40,50,70],.08,(x,y)=>edge(x,y,2)?[110,120,140]:((y%3===0&&x>3&&x<12)?[90,240,130]:null));
fillTile(45,[90,90,100],.1,(x,y)=>(x>=7&&x<=8&&y>=2&&y<=11)?[250,200,50]:((Math.hypot(x-7.5,y-11.5)<2.5)?[220,50,50]:null));
fillTile(46,[140,100,55],.1,(x,y)=>edge(x,y,1)?[90,60,30]:(((y===4||y===7||y===10)&&x>2&&x<13)?[245,240,225]:null));
const atlasTex=new THREE.CanvasTexture(atlas);
atlasTex.magFilter=atlasTex.minFilter=THREE.NearestFilter;atlasTex.generateMipmaps=false;
const BT={1:[0,0,0],2:[1,1,1],3:[2,2,2],4:[3,3,3],8:[7,7,7],14:[13,13,13],20:[19,20,21],21:[21,21,21],22:[22,22,22],23:[23,23,23]};
for(let id=24;id<=46;id++)BT[id]=[id,id,id];
const BRIGHT=new Set([4,26,27,29,30,31,36,37,38,39,44]);

/* ============================ LƯỚI KHỐI ============================ */
const FACES=[
 {dir:[-1,0,0],s:.8,c:[{p:[0,1,0],u:[0,1]},{p:[0,0,0],u:[0,0]},{p:[0,1,1],u:[1,1]},{p:[0,0,1],u:[1,0]}]},
 {dir:[1,0,0],s:.8,c:[{p:[1,1,1],u:[0,1]},{p:[1,0,1],u:[0,0]},{p:[1,1,0],u:[1,1]},{p:[1,0,0],u:[1,0]}]},
 {dir:[0,-1,0],s:.5,c:[{p:[1,0,1],u:[1,0]},{p:[0,0,1],u:[0,0]},{p:[1,0,0],u:[1,1]},{p:[0,0,0],u:[0,1]}]},
 {dir:[0,1,0],s:1,c:[{p:[0,1,1],u:[1,1]},{p:[1,1,1],u:[0,1]},{p:[0,1,0],u:[1,0]},{p:[1,1,0],u:[0,0]}]},
 {dir:[0,0,-1],s:.68,c:[{p:[1,0,0],u:[0,0]},{p:[0,0,0],u:[1,0]},{p:[1,1,0],u:[0,1]},{p:[0,1,0],u:[1,1]}]},
 {dir:[0,0,1],s:.68,c:[{p:[0,0,1],u:[0,0]},{p:[1,0,1],u:[1,0]},{p:[0,1,1],u:[0,1]},{p:[1,1,1],u:[1,1]}]}
];
const worldMat=new THREE.MeshBasicMaterial({map:atlasTex,vertexColors:true,side:THREE.DoubleSide});
const scene=new THREE.Scene();
scene.background=new THREE.Color(0x87ceeb);
scene.fog=new THREE.Fog(0x87ceeb,34,90);
const chunks={};
function buildChunk(cx,cz){
  const pos=[],uv=[],col=[],ind=[];const e=0.002;
  for(let y=0;y<H;y++)for(let z=cz*CS;z<Math.min(D,(cz+1)*CS);z++)for(let x=cx*CS;x<(cx+1)*CS;x++){
    const b=get(x,y,z);if(!b)continue;
    for(const f of FACES){
      const nx=x+f.dir[0],ny=y+f.dir[1],nz=z+f.dir[2];
      if(ny<0||get(nx,ny,nz))continue;
      const t=BT[b][f.dir[1]>0?0:f.dir[1]<0?2:1];
      const tc=t%COLS,tr=(t/COLS)|0;
      const u0=tc/COLS+e,u1=(tc+1)/COLS-e,v0=1-(tr+1)/ROWS+e,v1=1-tr/ROWS-e;
      const n=pos.length/3,sh=BRIGHT.has(b)?1:f.s;
      for(const c of f.c){
        pos.push(x+c.p[0],y+c.p[1],z+c.p[2]);
        uv.push(c.u[0]?u1:u0,c.u[1]?v1:v0);
        col.push(sh,sh,sh);
      }
      ind.push(n,n+1,n+2,n+2,n+1,n+3);
    }
  }
  const key=cx+','+cz;
  if(chunks[key]){scene.remove(chunks[key]);chunks[key].geometry.dispose();delete chunks[key];}
  if(!ind.length)return;
  const g=new THREE.BufferGeometry();
  g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(pos),3));
  g.setAttribute('uv',new THREE.BufferAttribute(new Float32Array(uv),2));
  g.setAttribute('color',new THREE.BufferAttribute(new Float32Array(col),3));
  g.setIndex(ind);g.computeBoundingSphere();
  const m=new THREE.Mesh(g,worldMat);chunks[key]=m;scene.add(m);
}
function rebuildAll(){for(let cx=0;cx<NCX;cx++)for(let cz=0;cz<NCZ;cz++)buildChunk(cx,cz);}
rebuildAll();

/* ============================ ĐỒ HỌA ============================ */
const renderer=new THREE.WebGLRenderer({antialias:false});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.5));
document.body.insertBefore(renderer.domElement,document.body.firstChild);
const camera=new THREE.PerspectiveCamera(75,1,0.1,140);
scene.add(new THREE.AmbientLight(0xffffff,0.8));
const sun=new THREE.DirectionalLight(0xffffff,0.55);sun.position.set(3,10,5);scene.add(sun);
function resize(){
  const w=window.innerWidth,h=window.innerHeight;if(!w||!h)return;
  renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();
}
window.addEventListener('resize',resize);resize();

/* ============================ NHÂN VẬT ============================ */
const U=1.8/32;
const mat=c=>new THREE.MeshLambertMaterial({color:c});
const SKIN=0xe0ac85,SHIRT=0x1aa3a3,PANTS=0x3a3d9e,HAIR=0x4a2f1b;
const fc=document.createElement('canvas');fc.width=fc.height=8;
const f2=fc.getContext('2d');
f2.fillStyle='#e0ac85';f2.fillRect(0,0,8,8);
f2.fillStyle='#4a2f1b';f2.fillRect(0,0,8,2);f2.fillRect(0,2,1,2);f2.fillRect(7,2,1,2);
f2.fillStyle='#ffffff';f2.fillRect(1,4,2,1);f2.fillRect(5,4,2,1);
f2.fillStyle='#3b4fc4';f2.fillRect(2,4,1,1);f2.fillRect(5,4,1,1);
f2.fillStyle='#8a4b38';f2.fillRect(3,6,2,1);
const faceTex=new THREE.CanvasTexture(fc);
faceTex.magFilter=faceTex.minFilter=THREE.NearestFilter;faceTex.generateMipmaps=false;
const model=new THREE.Group();
function part(w,h,d,m,y){const g=new THREE.BoxGeometry(w*U,h*U,d*U);g.translate(0,y*U,0);return new THREE.Mesh(g,m);}
model.add(part(8,12,4,mat(SHIRT),18));
const head=new THREE.Group();head.position.y=24*U;
head.add(part(8,8,8,[mat(SKIN),mat(SKIN),mat(HAIR),mat(SKIN),new THREE.MeshLambertMaterial({map:faceTex}),mat(HAIR)],4));
model.add(head);
function limb(x,y,topCol,botCol,topH){
  const g=new THREE.Group();g.position.set(x*U,y*U,0);
  g.add(part(4,topH,4,mat(topCol),-topH/2));
  g.add(part(4,12-topH,4,mat(botCol),-topH-(12-topH)/2));
  model.add(g);return g;
}
const armR=limb(-6,24,SHIRT,SKIN,4),armL=limb(6,24,SHIRT,SKIN,4);
const legR=limb(-2,12,PANTS,PANTS,12),legL=limb(2,12,PANTS,PANTS,12);
scene.add(model);

/* ============================ ÂM THANH ============================ */
let actx=null;
function beep(f,dur,type){
  try{
    if(!actx)actx=new (window.AudioContext||window.webkitAudioContext)();
    const o=actx.createOscillator(),g=actx.createGain();
    o.type=type||'square';o.frequency.value=f;
    g.gain.value=0.06;g.gain.exponentialRampToValueAtTime(0.0001,actx.currentTime+(dur||0.25));
    o.connect(g);g.connect(actx.destination);o.start();o.stop(actx.currentTime+(dur||0.25));
  }catch(e){}
}
const NOTE=[262,330,392,523];

/* ============================ TRẠNG THÁI CHUNG ============================ */
const S={started:false,ended:false,diff:'Thường',duration:600,startT:0,penalty:0,hints:3,used:0,
  flags:{},done:{},mult:1,endT:0};
function timeLeft(){const ref=S.ended?S.endT:performance.now();return S.duration-(ref-S.startT)/1000-S.penalty;}
let toastTimer=null;
function toast(html,ms){
  const t=$('toast');t.innerHTML=html;t.style.display='block';
  clearTimeout(toastTimer);toastTimer=setTimeout(()=>{t.style.display='none';},ms||4500);
}
function openDoor(i){const d=DOORS[i];set(d.x,2,d.z,0);set(d.x,3,d.z,0);rebuildAll();}

/* ============================ ĐỐ 1: ĐẨY THÙNG ============================ */
// lưới ô: x 1..11, z 1..11 (121 ô); thùng chỉ nằm ở x 1..10
const GN=11,NC=121;
const CXs=[],CZs=[];for(let i=0;i<NC;i++){CXs.push(i%GN+1);CZs.push(Math.floor(i/GN)+1);}
const DX=[1,-1,0,0],DZ=[0,0,1,-1];
const ci=(x,z)=>(x-1)+GN*(z-1);
function nbr(c,k){const x=CXs[c]+DX[k],z=CZs[c]+DZ[k];if(x<1||x>11||z<1||z>11)return -1;return ci(x,z);}
const par=new Int32Array(NC*NC*NC),mvk=new Int8Array(NC*NC*NC),qu=new Int32Array(NC*NC*NC);
function solveSok(p,a,b,pl0,pl1,obs){
  if(a>b){const t=a;a=b;b=t;}
  par.fill(-1);
  const start=(p*NC+a)*NC+b;par[start]=-2;
  let qh=0,qt=0;qu[qt++]=start;
  while(qh<qt){
    const s=qu[qh++];
    const b2=s%NC,r1=(s-b2)/NC,a2=r1%NC,p2=(r1-a2)/NC;
    if(a2===pl0&&b2===pl1){
      const moves=[];let k=s;
      while(par[k]!==-2){moves.push(mvk[k]);k=par[k];}
      return moves.reverse();
    }
    for(let k=0;k<4;k++){
      const n=nbr(p2,k);if(n<0||obs[n])continue;
      let na=a2,nb2=b2;
      if(n===a2||n===b2){
        const t=nbr(n,k);
        if(t<0||CXs[t]>10||obs[t]||t===a2||t===b2)continue;
        if(n===a2)na=t;else nb2=t;
      }
      let x=na,y=nb2;if(x>y){const t=x;x=y;y=t;}
      const key=(n*NC+x)*NC+y;
      if(par[key]!==-1)continue;
      par[key]=s;mvk[key]=k;qu[qt++]=key;
    }
  }
  return null;
}
const SOK={plates:[],init:[],obs:[],spawn:ci(1,6)};
const isCrate=v=>v===24||v===27;
let hiCell=-1,hiT=0;
function crateCells(){
  const out=[];
  for(let z=1;z<=11;z++)for(let x=1;x<=10;x++)if(isCrate(get(x,2,z)))out.push(ci(x,z));
  return out;
}
function putCrate(c,id){const x=CXs[c],z=CZs[c];set(x,2,z,id);set(x,3,z,id);}
function clearCell(c){const x=CXs[c],z=CZs[c];set(x,2,z,0);set(x,3,z,0);}
function paintCrates(){
  for(const c of crateCells())putCrate(c,(c===hiCell&&hiT>0)?27:24);
  let all=true;
  for(const p of SOK.plates){
    const on=isCrate(get(CXs[p],2,CZs[p]));
    set(CXs[p],1,CZs[p],on?26:25);if(!on)all=false;
  }
  return all;
}
function genSok(minLen){
  const inner=(c,x0,x1,z0,z1)=>CXs[c]>=x0&&CXs[c]<=x1&&CZs[c]>=z0&&CZs[c]<=z1;
  let best=null;
  for(let attempt=0;attempt<25;attempt++){
    const obs=new Uint8Array(NC);
    const taken=new Set([SOK.spawn]);
    const draw=(x0,x1,z0,z1)=>{for(let t=0;t<200;t++){const c=ci(x0+rint(x1-x0+1),z0+rint(z1-z0+1));if(!taken.has(c)){taken.add(c);return c;}}return -1;};
    const obsList=[];for(let i=0;i<3;i++){const c=draw(3,8,3,9);obs[c]=1;obsList.push(c);}
    const pl=[draw(2,9,2,10),draw(2,9,2,10)].sort((a,b)=>a-b);
    let cr=[pl[0],pl[1]];
    let q=draw(2,9,2,10);taken.delete(q);
    for(let i=0;i<80;i++){
      const k=rint(4),n=nbr(q,k);
      if(n<0||obs[n]||CXs[n]>10)continue;
      const back=nbr(q,k^1);
      if(back>=0&&(back===cr[0]||back===cr[1])&&R()<.85){
        if(back===cr[0])cr[0]=q;else cr[1]=q;
        q=n;
      }else if(n!==cr[0]&&n!==cr[1])q=n;
    }
    cr.sort((a,b)=>a-b);
    if(cr[0]===pl[0]||cr[0]===pl[1]||cr[1]===pl[0]||cr[1]===pl[1])continue;
    if(!inner(cr[0],2,9,2,10)||!inner(cr[1],2,9,2,10))continue;
    const sol=solveSok(SOK.spawn,cr[0],cr[1],pl[0],pl[1],obs);
    if(!sol)continue;
    const cand={plates:pl,init:cr,obs:obsList,len:sol.length};
    if(sol.length>=minLen){best=cand;break;}
    if(!best||cand.len>best.len)best=cand;
  }
  if(!best)best={plates:[ci(6,4),ci(6,8)],init:[ci(4,4),ci(4,8)],obs:[],len:0};
  return best;
}
function applySok(cfg){
  for(let z=1;z<=11;z++)for(let x=1;x<=11;x++){set(x,2,z,0);set(x,3,z,0);set(x,1,z,1);}
  SOK.plates=cfg.plates.slice();SOK.init=cfg.init.slice();SOK.obs=cfg.obs.slice();
  for(const o of SOK.obs){set(CXs[o],2,CZs[o],2);set(CXs[o],3,CZs[o],2);}
  for(const c of SOK.init)putCrate(c,24);
  hiCell=-1;hiT=0;paintCrates();rebuildAll();
}
function resetSok(){
  if(S.flags.r1)return;
  for(const c of crateCells())clearCell(c);
  for(const c of SOK.init)putCrate(c,24);
  hiCell=-1;hiT=0;paintCrates();rebuildAll();
  toast('↺ Các thùng đã được xếp lại như ban đầu.',3000);
}
function solve1(){
  S.flags.r1=true;S.done.sign1=true;openDoor(0);beep(660,.3,'triangle');
  toast('🔔 Cả hai thùng đã vào đúng vị trí! <b>Cửa gỗ phía đông đã mở.</b>',6000);
}
function moveCrate(cx,cz,tx,tz){
  set(cx,2,cz,0);set(cx,3,cz,0);set(tx,2,tz,24);set(tx,3,tz,24);
  hiCell=-1;hiT=0;
  const all=paintCrates();rebuildAll();
  if(all&&!S.flags.r1)solve1();
}
let pushCD=0;
function tryPush(axis,d,newpos){
  const sgn=d>0?1:-1;
  const ca=Math.floor(newpos+sgn*0.3);
  const co=Math.floor(axis==='x'?Pl.z:Pl.x);
  const cx=axis==='x'?ca:co,cz=axis==='x'?co:ca;
  if(Pl.y>2.6||!isCrate(get(cx,2,cz)))return false;
  if(pushCD>0)return true;
  const tx=cx+(axis==='x'?sgn:0),tz=cz+(axis==='z'?sgn:0);
  if(tx<1||tx>10||tz<1||tz>11||get(tx,2,tz)||get(tx,3,tz))return true;
  moveCrate(cx,cz,tx,tz);pushCD=0.2;
  return true;
}
function sokHint(){
  const cr=crateCells();
  if(cr.length!==2)return 'Hãy bấm ↺ (hoặc phím R) để xếp lại thùng.';
  const pc=ci(Math.max(1,Math.min(11,Math.floor(Pl.x))),Math.max(1,Math.min(11,Math.floor(Pl.z))));
  const obs=new Uint8Array(NC);for(const o of SOK.obs)obs[o]=1;
  const pl=SOK.plates.slice().sort((a,b)=>a-b);
  const sol=solveSok(pc,cr[0],cr[1],pl[0],pl[1],obs);
  if(!sol)return 'Có vẻ một thùng đã bị kẹt (ví dụ sát tường hoặc góc). Hãy bấm <b>↺</b> (phím R) để xếp lại thùng.';
  let p=pc,a=cr[0],b=cr[1];
  for(const k of sol){
    const n=nbr(p,k);
    if(n===a||n===b){
      hiCell=n;hiT=7;paintCrates();rebuildAll();
      return 'Hãy đẩy <b>thùng đang sáng vàng</b> sang hướng <b>'+DIRN[k]+'</b>. (Cửa gỗ ở phía Đông.)';
    }
    p=n;
  }
  return 'Đẩy thùng lên ô xanh trên sàn.';
}

/* ============================ ĐỐ 2: TRÍ NHỚ ĐÈN ============================ */
const SIM={len:4,seq:[],prog:0,play:null,lit:-1,flashT:0,curPad:-1,played:false,hintN:0};
function genSim(n){
  SIM.len=n;SIM.seq=[];
  while(SIM.seq.length<n){const v=rint(4);if(SIM.seq.length&&SIM.seq[SIM.seq.length-1]===v)continue;SIM.seq.push(v);}
  SIM.prog=0;SIM.play=null;SIM.lit=-1;SIM.flashT=0;SIM.played=false;SIM.hintN=0;
}
function setLamp(i){
  for(let k=0;k<4;k++)box(13+3*k,3,0,14+3*k,4,0,(k===i?36:32)+k);
  rebuildAll();
}
function playSeq(){
  if(S.flags.r2||SIM.play)return;
  SIM.play={t:0};SIM.prog=0;SIM.played=true;S.done.console=true;
}
function updateSim(dt){
  if(SIM.play){
    SIM.play.t+=dt;
    const t=SIM.play.t-0.6,idx=Math.floor(t/0.9),within=t-idx*0.9;
    const lit=(t>=0&&idx<SIM.len&&within<0.55)?SIM.seq[idx]:-1;
    if(lit!==SIM.lit){SIM.lit=lit;setLamp(lit);if(lit>=0)beep(NOTE[lit],.4,'triangle');}
    if(idx>=SIM.len){SIM.play=null;SIM.lit=-1;setLamp(-1);toast('Đến lượt bạn! Bước lên các <b>ô màu trên sàn</b> theo đúng thứ tự đèn.',5000);}
    return;
  }
  if(SIM.flashT>0){SIM.flashT-=dt;if(SIM.flashT<=0){SIM.lit=-1;setLamp(-1);}}
}
function padAt(){
  if(Pl.y>2.4)return -1;
  for(let i=0;i<4;i++){const x0=13+3*i;if(Pl.x>=x0&&Pl.x<x0+2&&Pl.z>=8&&Pl.z<10)return i;}
  return -1;
}
function pressPad(i){
  if(S.flags.r2||SIM.play)return;
  if(!SIM.played){toast('Hãy quan sát dãy đèn trên tường trước. Dùng <b>bảng điều khiển</b> cạnh cửa để phát dãy đèn.',5000);return;}
  SIM.lit=i;SIM.flashT=0.35;setLamp(i);beep(NOTE[i],.3,'triangle');
  if(i===SIM.seq[SIM.prog]){
    SIM.prog++;
    if(SIM.prog>=SIM.len){
      S.flags.r2=true;S.done.console=true;openDoor(1);
      setTimeout(()=>{beep(523,.2,'triangle');},200);setTimeout(()=>{beep(784,.4,'triangle');},420);
      toast('🎶 Đúng hết rồi! <b>Cửa ở phía đông đã mở.</b>',6000);
    }
  }else{
    SIM.prog=0;S.penalty+=WRONG_PEN;beep(110,.5,'sawtooth');
    toast('❌ Sai thứ tự! Bị phạt <b>'+WRONG_PEN+' giây</b>. Bạn có thể dùng bảng điều khiển để xem lại dãy đèn.',5000);
  }
}

/* ============================ ĐỐ 3: CẦU Ô NỀN ============================ */
const TR=5,TC=4;
const PATH={cells:[],on:null,st:null,revT:0,badT:0,badCell:null,sig:'',last:'',wander:2,hintN:0};
function genPath(wander){
  PATH.wander=wander;
  for(let tries=0;tries<50;tries++){
    let r=rint(TR);const cells=[],seen=new Set();
    for(let c=0;c<TC;c++){
      cells.push([c,r]);seen.add(c+','+r);
      const steps=rint(wander+1);
      for(let s=0;s<steps;s++){
        let nr=r+(R()<.5?-1:1);
        if(nr<0||nr>=TR)nr=r+(nr<0?1:-1);
        if(nr<0||nr>=TR||seen.has(c+','+nr))break;
        r=nr;cells.push([c,r]);seen.add(c+','+r);
      }
    }
    if(cells.length>=6||tries===49){PATH.cells=cells;break;}
  }
  PATH.on=[];PATH.st=[];
  for(let r=0;r<TR;r++){PATH.on.push([0,0,0,0]);PATH.st.push([0,0,0,0]);}
  for(const [c,r] of PATH.cells)PATH.on[r][c]=1;
  PATH.revT=0;PATH.badT=0;PATH.badCell=null;PATH.sig='';PATH.last='';PATH.hintN=0;
  paintTiles(true);
}
function paintTiles(force){
  let sig='';
  const ids=[];
  for(let r=0;r<TR;r++){ids.push([]);for(let c=0;c<TC;c++){
    let id=28;
    if(PATH.st[r][c]===1)id=30;
    else if(PATH.revT>0&&PATH.on[r][c])id=29;
    if(PATH.badT>0&&PATH.badCell&&PATH.badCell[0]===c&&PATH.badCell[1]===r)id=31;
    ids[r].push(id);sig+=id;
  }}
  if(!force&&sig===PATH.sig)return;
  PATH.sig=sig;
  for(let r=0;r<TR;r++)for(let c=0;c<TC;c++)box(27+2*c,1,1+2*r,28+2*c,1,2+2*r,ids[r][c]);
  rebuildAll();
}
function tileAt(){
  if(Pl.y>2.4||Pl.x<27||Pl.x>=35||Pl.z<1||Pl.z>=11)return null;
  return [Math.floor((Pl.x-27)/2),Math.floor((Pl.z-1)/2)];
}
function pullLever(){
  if(S.flags.r3)return;
  PATH.revT=3.5;S.done.lever=true;beep(392,.3,'triangle');paintTiles();
  toast('✨ Các ô an toàn đang sáng <b>vàng</b> trong vài giây. Hãy ghi nhớ đường đi!',4000);
}
function updatePath(dt,active){
  if(PATH.revT>0){PATH.revT-=dt;if(PATH.revT<=0)PATH.revT=0;}
  if(PATH.badT>0){PATH.badT-=dt;if(PATH.badT<=0){PATH.badT=0;PATH.badCell=null;}}
  paintTiles();
  if(!active||S.flags.r3)return;
  const t=tileAt(),key=t?t[0]+','+t[1]:'';
  if(key!==PATH.last){
    PATH.last=key;
    if(t){
      if(PATH.on[t[1]][t[0]]){PATH.st[t[1]][t[0]]=1;beep(440+t[0]*80,.12,'triangle');paintTiles();}
      else{
        PATH.badCell=t;PATH.badT=1.2;S.penalty+=FALL_PEN;beep(110,.5,'sawtooth');
        Pl.x=25.6;Pl.z=6.5;Pl.y=2.0001;vy=0;PATH.last='';
        paintTiles();
        toast('❌ Ô đó không an toàn! Bạn bị đưa về đầu cầu và bị phạt <b>'+FALL_PEN+' giây</b>.',5000);
      }
    }
  }
  if(Pl.x>=35&&Pl.x<36&&Pl.y<2.4){
    S.flags.r3=true;S.done.lever=true;openDoor(2);
    setTimeout(()=>{beep(523,.2,'triangle');},150);setTimeout(()=>{beep(784,.2,'triangle');},350);setTimeout(()=>{beep(1046,.4,'triangle');},550);
    toast('🌞 Qua cầu an toàn! <b>Cửa thoát hiểm đã mở.</b> Hãy bước ra ngoài!',7000);
  }
}

/* ============================ GỢI Ý, NHIỆM VỤ ============================ */
function currentHint(){
  const f=S.flags;
  if(!f.r1)return sokHint();
  if(!f.r2){
    if(!SIM.played)return 'Dùng <b>bảng điều khiển</b> trên tường cạnh cửa để phát dãy đèn, rồi nhớ thứ tự.';
    SIM.hintN++;
    if(SIM.hintN<2)return 'Xem lại dãy đèn bằng bảng điều khiển. Mỗi đèn trên tường khớp với <b>ô màu cùng màu</b> trên sàn.';
    return 'Thứ tự đèn: <b>'+SIM.seq.map(i=>LAMP[i]).join(' → ')+'</b>';
  }
  if(!f.r3){
    PATH.hintN++;
    if(PATH.hintN<2)return 'Gạt <b>cần gạt</b> ở bức tường phía bắc để hiện đường đi. Chỉ các ô vàng là an toàn.';
    PATH.revT=6;paintTiles();
    return 'Mình sẽ làm sáng đường đi trong <b>6 giây</b>. Hãy nhìn kỹ!';
  }
  return 'Cửa thoát hiểm đã mở. Hãy đi ra ngoài trời!';
}
function useHint(){
  if(!S.started||S.ended)return;
  if(S.hints<=0){toast('Bạn đã hết lượt gợi ý.',2500);return;}
  S.hints--;S.used++;S.penalty+=HINT_PEN;$('hn').textContent=S.hints;
  toast('💡 <span class="hint"><b>Gợi ý:</b></span> '+currentHint(),9000);
}

/* ============================ BẢNG THÔNG TIN ============================ */
let panelOpen=false;
const keys={};const joy={x:0,y:0};
function openPanel(title,html){
  $('pTitle').textContent=title;$('pBody').innerHTML=html;$('panel').style.display='flex';
  panelOpen=true;joy.x=joy.y=0;for(const k in keys)keys[k]=false;
}
function closePanel(){$('panel').style.display='none';panelOpen=false;}
$('pClose').addEventListener('click',closePanel);
const q=sel=>$('pBody').querySelector(sel);
function onBtn(id,fn){const e=q('#'+id);if(e)e.addEventListener('click',fn);}
const okBtn='<button id="ok" class="pb alt">Đóng</button>';
function oSign1(){
  S.done.sign1=true;
  openPanel('🪧 Phòng 1: Đẩy thùng',
    '<p>Hai <b>thùng gỗ</b> đang nằm trên sàn. Hãy đẩy chúng lên hai <b>ô xanh</b> trên sàn để mở cửa.</p>'+
    '<p class="hint">• Đi thẳng vào thùng để đẩy nó.<br>• Chỉ đẩy được, <b>không kéo lại được</b>.<br>• Đừng đẩy thùng vào góc hoặc sát tường!</p>'+
    '<p class="cap">Lỡ kẹt? Bấm nút ↺ (hoặc phím R) để xếp lại thùng, không bị phạt.</p>'+
    (S.flags.r1?'':'<button id="rs" class="pb">↺ Xếp lại thùng</button>')+okBtn);
  onBtn('rs',()=>{resetSok();closePanel();});onBtn('ok',closePanel);
}
function oConsole(){
  if(S.flags.r2){openPanel('🖥️ Bảng điều khiển','<p>Bạn đã giải xong câu đố đèn. Cửa phía đông đã mở.</p>'+okBtn);onBtn('ok',closePanel);return;}
  openPanel('🖥️ Bảng điều khiển',
    '<p>Bốn đèn màu trên tường sẽ sáng theo một thứ tự (<b>'+SIM.len+' lần</b>). Hãy nhớ rồi bước lên <b>các ô màu trên sàn</b> theo đúng thứ tự đó.</p>'+
    '<p class="cap">Bấm sai bị phạt '+WRONG_PEN+' giây.</p>'+
    '<button id="pl" class="pb">▶️ Phát dãy đèn</button>'+okBtn);
  onBtn('pl',()=>{closePanel();playSeq();});onBtn('ok',closePanel);
}
function oLever(){
  if(S.flags.r3){openPanel('🕹️ Cần gạt','<p>Bạn đã qua cầu an toàn.</p>'+okBtn);onBtn('ok',closePanel);return;}
  openPanel('🕹️ Cần gạt',
    '<p>Sàn phía trước gồm nhiều ô nền giống hệt nhau. Chỉ một vài ô là an toàn.</p>'+
    '<p class="hint">Gạt cần để các ô an toàn sáng <b>vàng</b> trong vài giây.</p>'+
    '<p class="cap">Bước sai: bị đưa về đầu cầu và phạt '+FALL_PEN+' giây. Ô đúng đã bước sẽ chuyển sang màu xanh.</p>'+
    '<button id="pull" class="pb">🕹️ Gạt cần</button>'+okBtn);
  onBtn('pull',()=>{closePanel();pullLever();});onBtn('ok',closePanel);
}
function oQuests(){
  const f=S.flags,c=v=>v?'✅':'⬜';
  openPanel('📋 Nhiệm vụ',
    '<p class="chk">'+c(f.r1)+' <b>Phòng 1:</b> đẩy 2 thùng lên 2 ô xanh</p>'+
    '<p class="chk">'+c(f.r2)+' <b>Phòng 2:</b> bước lên ô màu theo thứ tự đèn</p>'+
    '<p class="chk">'+c(f.r3)+' <b>Phòng 3:</b> đi theo đường an toàn trên cầu ô nền</p>'+
    '<p class="chk">'+c(S.ended)+' <b>Thoát ra ngoài trời ☀️</b></p>'+
    '<p class="cap">Lại gần vật có dấu <b style="color:#ffd400">◆</b> vàng rồi bấm ✋ (phím E).</p>'+okBtn);
  onBtn('ok',closePanel);
}
const OBJS=[
 {id:'sign1',label:'Biển hướng dẫn',x:5.5,z:1.9,fn:oSign1},
 {id:'console',label:'Bảng điều khiển',x:13.3,z:3.5,fn:oConsole},
 {id:'lever',label:'Cần gạt',x:26.5,z:1.9,fn:oLever}
];
const markGeo=new THREE.OctahedronGeometry(0.2);
const markMat=new THREE.MeshBasicMaterial({color:0xffd400});
OBJS.forEach(o=>{o.mark=new THREE.Mesh(markGeo,markMat);o.mark.position.set(o.x,5.2,o.z);scene.add(o.mark);});

/* ============================ NGƯỜI CHƠI ============================ */
const SPAWN={x:1.5,y:2.0001,z:6.5};
const Pl={x:SPAWN.x,y:SPAWN.y,z:SPAWN.z};
let vy=0,onGround=false,yaw=-Math.PI/2,pitch=-0.12,view=1;
let walkPhase=0,amp=0,swing=0,jumpHeld=false;
function solidAt(x,y,z){
  if(y<0)return true;
  if(x<0||x>=W||z<0||z>=D)return true;
  if(y>=H)return false;
  return world[I(x,y,z)]!==0;
}
function collides(){
  const r=0.3;
  const x0=Math.floor(Pl.x-r),x1=Math.floor(Pl.x+r),y0=Math.floor(Pl.y),y1=Math.floor(Pl.y+1.79),
        z0=Math.floor(Pl.z-r),z1=Math.floor(Pl.z+r);
  for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++)for(let x=x0;x<=x1;x++)if(solidAt(x,y,z))return true;
  return false;
}
function moveH(axis,d,moving){
  const o=Pl[axis];Pl[axis]=o+d;
  if(!collides())return;
  if(d!==0&&tryPush(axis,d,o+d)){Pl[axis]=o;return;}
  if(onGround&&moving){
    Pl.y+=1.01;const ok=!collides();Pl.y-=1.01;
    if(ok){Pl[axis]=o;if(vy<=0){vy=8;onGround=false;}return;}
  }
  Pl[axis]=o;
}

/* ============================ ĐIỀU KHIỂN ============================ */
let nearObj=null;
function interact(){if(S.started&&!S.ended&&!panelOpen&&nearObj){swing=1;nearObj.fn();}}
window.addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();
  if(k==='escape'){closePanel();return;}
  if(panelOpen)return;
  keys[k]=true;
  if(k===' '||k.startsWith('arrow'))e.preventDefault();
  if(k==='v')view=(view+1)%3;
  if(k==='e')interact();
  if(k==='h')useHint();
  if(k==='i')oQuests();
  if(k==='r'&&S.started&&!S.ended)resetSok();
});
window.addEventListener('keyup',e=>{keys[e.key.toLowerCase()]=false;});
window.addEventListener('blur',()=>{for(const k in keys)keys[k]=false;});
const cv=renderer.domElement;
cv.addEventListener('contextmenu',e=>e.preventDefault());
const looks={};
cv.addEventListener('pointerdown',e=>{window.focus();looks[e.pointerId]={x:e.clientX,y:e.clientY};cv.setPointerCapture(e.pointerId);});
cv.addEventListener('pointermove',e=>{
  const l=looks[e.pointerId];if(!l||panelOpen)return;
  yaw-=(e.clientX-l.x)*0.0055;
  pitch=Math.max(-1.4,Math.min(1.4,pitch-(e.clientY-l.y)*0.0055));
  l.x=e.clientX;l.y=e.clientY;
});
const endLook=e=>{delete looks[e.pointerId];};
cv.addEventListener('pointerup',endLook);cv.addEventListener('pointercancel',endLook);
let joyId=null;const joyEl=$('joy'),knob=$('knob');
function joyMove(e){
  const r=joyEl.getBoundingClientRect();
  let dx=e.clientX-(r.left+r.width/2),dy=e.clientY-(r.top+r.height/2);
  const m=46,len=Math.hypot(dx,dy);if(len>m){dx*=m/len;dy*=m/len;}
  knob.style.transform='translate('+dx+'px,'+dy+'px)';
  joy.x=Math.abs(dx/m)<.15?0:dx/m;joy.y=Math.abs(dy/m)<.15?0:dy/m;
}
joyEl.addEventListener('pointerdown',e=>{joyId=e.pointerId;joyEl.setPointerCapture(e.pointerId);joyMove(e);});
joyEl.addEventListener('pointermove',e=>{if(e.pointerId===joyId)joyMove(e);});
function joyEnd(e){if(e.pointerId!==joyId)return;joyId=null;joy.x=joy.y=0;knob.style.transform='translate(0,0)';}
joyEl.addEventListener('pointerup',joyEnd);joyEl.addEventListener('pointercancel',joyEnd);
function hold(id,on,off){
  const el=$(id);
  el.addEventListener('pointerdown',e=>{e.stopPropagation();el.setPointerCapture(e.pointerId);on();});
  const up=()=>{if(off)off();};
  el.addEventListener('pointerup',up);el.addEventListener('pointercancel',up);
}
hold('bJump',()=>{jumpHeld=true;},()=>{jumpHeld=false;});
hold('bAct',interact);
hold('bInv',oQuests);
hold('bHint',useHint);
hold('bReset',()=>{if(S.started&&!S.ended)resetSok();});
hold('bView',()=>{view=(view+1)%3;});

/* ============================ BẮT ĐẦU / KẾT THÚC ============================ */
function getBest(){try{return +localStorage.getItem('escape3d_v2_best')||0;}catch(e){return 0;}}
function setBest(v){try{localStorage.setItem('escape3d_v2_best',String(v));}catch(e){}}
function showStart(){
  $('overlay').style.display='flex';
  let h='<h2>⏳ Escape Time 3D · Bản 2</h2><p>Thoát khỏi <b>3 căn phòng</b> bằng cách <b>hành động</b>: đẩy thùng, nhớ dãy đèn màu và băng qua cầu ô nền ẩn.</p>'+
   '<p class="cap">Đi lại bằng cần trái, kéo màn hình để nhìn. Lại gần vật có dấu <b style="color:#ffd400">◆</b> vàng rồi bấm ✋ (phím E). Bố cục mỗi lần chơi đều khác.</p>';
  for(const k in DIFF)h+='<button class="pb'+(k==='Thường'?'':' alt')+'" data-d="'+k+'">'+k+' — '+DIFF[k][3]+'</button>';
  const b=getBest();if(b)h+='<p class="cap">🏆 Kỷ lục trên máy này: <b>'+b+'</b> điểm</p>';
  $('ovBody').innerHTML=h;
  $('ovBody').querySelectorAll('button[data-d]').forEach(bt=>bt.addEventListener('click',()=>startGame(bt.getAttribute('data-d'))));
}
function startGame(d){
  S.diff=d;const c=DIFF[d];
  S.duration=c[0];S.hints=c[1];S.mult=c[2];
  $('overlay').style.display='none';
  toast('⚙️ Đang chuẩn bị các căn phòng…',1200);
  applySok(genSok(c[5]));
  genSim(c[4]);
  genPath(c[6]);
  setLamp(-1);
  S.startT=performance.now();S.started=true;
  $('hn').textContent=S.hints;
  try{if(!actx)actx=new (window.AudioContext||window.webkitAudioContext)();}catch(e){}
  toast('⏳ Cánh cửa sập lại sau lưng bạn. <b>Đồng hồ bắt đầu chạy!</b> Hãy đọc <b>biển hướng dẫn</b> ở bức tường phía bắc.',7000);
}
function endGame(win){
  if(S.ended)return;
  S.ended=true;S.endT=performance.now();closePanel();
  const left=Math.max(0,timeLeft());let h;
  if(win){
    const score=Math.floor((left*10+S.hints*100+(S.used===0?500:0))*S.mult);
    const ratio=left/S.duration,stars=ratio>=.5?3:ratio>=.25?2:1;
    const best=getBest(),nb=score>best;if(nb)setBest(score);
    h='<h2>🎉 BẠN ĐÃ THOÁT!</h2><p style="font-size:34px;text-align:center;margin:4px">'+'⭐'.repeat(stars)+'☆'.repeat(3-stars)+'</p>'+
      '<p>Điểm: <b>'+score+'</b>'+(nb?' 🏆 <b>kỷ lục mới!</b>':'')+'<br>Thời gian còn lại: <b>'+fmt(left)+'</b><br>Gợi ý đã dùng: <b>'+S.used+'</b> · Độ khó: <b>'+S.diff+'</b></p>';
  }else{
    h='<h2>⌛ HẾT GIỜ!</h2><p>Cánh cửa khóa lại mãi mãi… nhưng bạn có thể thử lại với bố cục hoàn toàn mới.</p>';
  }
  h+='<button id="again" class="pb">🔄 Chơi lại (bố cục mới)</button>';
  $('ovBody').innerHTML=h;$('overlay').style.display='flex';
  $('again').addEventListener('click',()=>location.reload());
}

/* ============================ VÒNG LẶP ============================ */
let lastSec=-1,lastCompass='';
function update(dt){
  const active=S.started&&!S.ended&&!panelOpen;
  let ix=0,iz=0;
  if(active){
    ix=((keys.d||keys.arrowright)?1:0)-((keys.a||keys.arrowleft)?1:0)+joy.x;
    iz=((keys.s||keys.arrowdown)?1:0)-((keys.w||keys.arrowup)?1:0)+joy.y;
  }
  let len=Math.hypot(ix,iz);if(len>1){ix/=len;iz/=len;len=1;}
  const sy=Math.sin(yaw),cy=Math.cos(yaw),fwd=-iz,rgt=ix;
  const dirx=rgt*cy+fwd*(-sy),dirz=rgt*(-sy)+fwd*(-cy);
  const speed=keys.shift?5.6:4.3,moving=len>0.1;
  pushCD=Math.max(0,pushCD-dt);
  vy=Math.max(-40,vy-25*dt);
  if(active&&(jumpHeld||keys[' '])&&onGround){vy=8;onGround=false;}
  moveH('x',dirx*speed*dt,moving);moveH('z',dirz*speed*dt,moving);
  const oy=Pl.y;Pl.y+=vy*dt;
  if(collides()){if(vy<0){Pl.y=Math.floor(Pl.y)+1.0001;onGround=true;}else Pl.y=oy;vy=0;}
  else onGround=false;
  if(Pl.y<-10){Pl.x=SPAWN.x;Pl.y=SPAWN.y+2;Pl.z=SPAWN.z;vy=0;}

  if(hiT>0){hiT-=dt;if(hiT<=0){hiT=0;paintCrates();rebuildAll();}}
  if(S.started&&!S.ended){
    updateSim(dt);
    if(active&&!S.flags.r2&&!SIM.played&&Pl.x>13.3&&Pl.x<23.5)playSeq();
    if(active){const p=padAt();if(p!==SIM.curPad){SIM.curPad=p;if(p>=0)pressPad(p);}}
    updatePath(dt,active);
  }

  nearObj=null;
  if(active){
    let best=2.6;
    for(const o of OBJS){const dd=Math.hypot(o.x-Pl.x,o.z-Pl.z);if(dd<best){best=dd;nearObj=o;}}
  }
  const pr=$('prompt'),ba=$('bAct');
  if(nearObj){pr.style.display='block';pr.textContent='✋ '+nearObj.label;ba.classList.add('near');}
  else{pr.style.display='none';ba.classList.remove('near');}
  const t=performance.now()*0.003;
  for(const o of OBJS){o.mark.visible=!S.done[o.id];o.mark.position.y=5.2+Math.sin(t+o.x)*0.15;o.mark.rotation.y=t;}
  $('bReset').style.display=(S.started&&!S.ended&&!S.flags.r1&&Pl.x<12)?'flex':'none';

  if(S.started&&!S.ended){
    const left=timeLeft(),sec=Math.ceil(left);
    if(sec!==lastSec){
      lastSec=sec;const tm=$('timer');tm.textContent='⏳ '+fmt(left);
      tm.className='ui '+(left<60?'danger':left<180?'warn':'ok');
    }
    if(left<=0)endGame(false);
    else if(S.flags.r3&&Pl.x>37.7)endGame(true);
  }else if(!S.started){$('timer').textContent='⏳ Escape Time 3D';}

  const fx=-Math.sin(yaw),fz=-Math.cos(yaw);
  const cmp='🧭 '+(Math.abs(fx)>Math.abs(fz)?(fx>0?'Đông':'Tây'):(fz<0?'Bắc':'Nam'));
  if(cmp!==lastCompass){lastCompass=cmp;$('compass').textContent=cmp;}

  const walking=moving&&onGround;
  amp+=((walking?1:0)-amp)*Math.min(1,dt*10);
  walkPhase+=dt*speed*2.1*(walking?1:0);
  const sw=Math.sin(walkPhase)*0.9*amp;
  legR.rotation.x=sw;legL.rotation.x=-sw;armL.rotation.x=sw;
  swing=Math.max(0,swing-dt*3.2);
  armR.rotation.x=-sw-Math.sin(swing*Math.PI)*1.7;
  head.rotation.x=-pitch*0.8;
  model.position.set(Pl.x,Pl.y,Pl.z);model.rotation.y=yaw+Math.PI;

  const ex=Pl.x,ey=Pl.y+1.62,ez=Pl.z,cp=Math.cos(pitch);
  const dx=-Math.sin(yaw)*cp,dy=Math.sin(pitch),dz=-Math.cos(yaw)*cp;
  if(view===0){
    model.visible=false;camera.position.set(ex,ey,ez);camera.rotation.set(pitch,yaw,0,'YXZ');
  }else{
    model.visible=true;
    const sgn=view===1?-1:1;let d=0.3;
    for(;d<=3.8;d+=0.15){if(solidAt(Math.floor(ex+dx*sgn*d),Math.floor(ey+dy*sgn*d),Math.floor(ez+dz*sgn*d)))break;}
    const dist=Math.max(0.4,d-0.3);
    camera.position.set(ex+dx*sgn*dist,ey+dy*sgn*dist,ez+dz*sgn*dist);
    if(view===1)camera.rotation.set(pitch,yaw,0,'YXZ');
    else camera.rotation.set(-pitch,yaw+Math.PI,0,'YXZ');
  }
}
let last=performance.now(),frames=0;
function frame(now){
  const dt=Math.min(0.05,(now-last)/1000);last=now;
  update(dt);renderer.render(scene,camera);frames++;
  if(frames===2)showStart();
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
window.__T={S:S,Pl:Pl,get:get,update:update,startGame:startGame,SOK:SOK,SIM:SIM,PATH:PATH,
  solveSok:solveSok,nbr:nbr,ci:ci,CXs:CXs,CZs:CZs,crateCells:crateCells,currentHint:currentHint,
  setYaw:v=>{yaw=v;},getVy:()=>vy,DOORS:DOORS,keys:keys,joy:joy,resetSok:resetSok,genSok:genSok};
})();
</script>
</body>
</html>
"""

components.html(HTML, height=720, scrolling=False)
