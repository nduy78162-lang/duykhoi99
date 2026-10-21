"""
⏳ ESCAPE TIME 3D — thoát phòng giải đố kiểu Minecraft, chạy trên Streamlit
===========================================================================
Cài đặt:  pip install "streamlit>=1.30"
Chạy:     streamlit run escape3d.py

Game dùng three.js (tải từ cdnjs) nhúng vào Streamlit, nên máy cần có mạng.

Điều khiển
  Điện thoại : cần trái = đi · kéo ngón tay lên màn hình = nhìn · ⬆ nhảy
               ✋ tương tác với vật thể ở gần · 💡 gợi ý · 🎒 túi đồ · 👁 đổi góc nhìn
  Máy tính   : W A S D = đi · Space = nhảy · kéo chuột trái = nhìn
               E = tương tác · H = gợi ý · I = túi đồ · V = đổi góc nhìn · Esc = đóng bảng
"""

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Escape Time 3D",
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
input,select{-webkit-user-select:text;user-select:text}
.ui{position:absolute;color:#fff;text-shadow:0 1px 3px #000}
#timer{top:8px;left:50%;transform:translateX(-50%);font-size:26px;font-weight:800;
  letter-spacing:2px;padding:2px 16px;border-radius:12px;background:rgba(0,0,0,.45);
  font-variant-numeric:tabular-nums;text-shadow:none}
#timer.ok{color:#5be38a}#timer.warn{color:#ffd24a}
#timer.danger{color:#ff5a4a;animation:pulse 1s infinite}
@keyframes pulse{50%{opacity:.55}}
#toast{top:56px;left:50%;transform:translateX(-50%);width:max-content;max-width:86%;
  text-align:center;font-size:14px;background:rgba(0,0,0,.6);padding:8px 12px;
  border-radius:10px;display:none;line-height:1.35}
#prompt{right:16px;bottom:166px;font-size:13px;background:rgba(0,0,0,.55);padding:4px 10px;
  border-radius:10px;display:none;max-width:46%;text-align:right}
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
#bInv{top:8px;left:8px;width:46px;height:46px}
#bHint{top:8px;right:8px;width:50px;height:46px;border-radius:23px}
#bView{top:62px;right:8px;width:46px;height:46px}
#cross{top:50%;left:50%;width:14px;height:14px;transform:translate(-50%,-50%);pointer-events:none;display:none}
#cross:before,#cross:after{content:"";position:absolute;background:rgba(255,255,255,.8);box-shadow:0 0 2px #000}
#cross:before{left:6px;top:0;width:2px;height:14px}
#cross:after{left:0;top:6px;width:14px;height:2px}
#overlay,#panel{position:absolute;inset:0;display:none;align-items:center;justify-content:center;
  background:rgba(8,12,20,.72);z-index:10;padding:12px;box-sizing:border-box}
.card{background:#1f2937;color:#fff;border:2px solid #4b5b73;border-radius:14px;
  padding:16px 18px;width:100%;max-width:430px;max-height:92%;overflow:auto;
  box-sizing:border-box;font-size:15px;line-height:1.45;touch-action:pan-y;text-shadow:none}
.card h2{margin:0 0 8px;font-size:20px}
.card p{margin:6px 0}
.cap{opacity:.7;font-size:13px}
.big{font-size:26px;letter-spacing:3px;line-height:1.5}
.pb{display:block;width:100%;margin-top:10px;padding:11px;font-size:16px;font-weight:700;
  border:0;border-radius:10px;background:#f5b72d;color:#222}
.pb.alt{background:#3a4a63;color:#fff}
.card input,.card select{width:100%;box-sizing:border-box;margin-top:8px;padding:10px;font-size:18px;
  border-radius:8px;border:2px solid #4b5b73;background:#111827;color:#fff;text-align:center;
  letter-spacing:4px}
.card select{letter-spacing:0;font-size:15px;text-align:left}
.card label{display:block;font-size:13px;margin-top:6px;opacity:.9}
#fb{margin-top:8px;font-weight:700;min-height:20px}
.item{margin:6px 0}
.hint{color:#ffd24a}
#pClose{float:right;background:none;border:0;color:#fff;font-size:22px;margin:-6px -6px 0 0}
.row{display:flex;gap:8px}.row .pb{margin-top:10px}
</style>
</head>
<body>
<div id="timer" class="ui ok">--:--</div>
<div id="toast" class="ui"></div>
<div id="prompt" class="ui"></div>
<div id="cross" class="ui"></div>
<div id="joy" class="ui"><div id="knob"></div></div>
<div id="bJump" class="btn">⬆</div>
<div id="bAct" class="btn">✋</div>
<div id="bInv" class="btn">🎒</div>
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
const norm=s=>String(s||'').replace(/\s+/g,'').toUpperCase();
const fmt=s=>{s=Math.max(0,Math.floor(s));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');};

/* ============================ DỮ LIỆU CÂU ĐỐ ============================ */
function rnd(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;
  let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;
  return((t^t>>>14)>>>0)/4294967296;};}
const R=rnd((Math.random()*1e9)|0);
const pick=a=>a[Math.floor(R()*a.length)];
const WORDS=['ESCAPE','SECRET','PUZZLE','HIDDEN','ORIGIN','SILVER'];
const RIDDLES=[
 [['Số nguyên tố chẵn duy nhất',2],['Số hoàn hảo nhỏ nhất',6],['Bình phương của 3',9]],
 [['Số ngày trong một tuần',7],['Số cạnh của hình tam giác',3],['Số mặt của một con xúc xắc',6]],
 [['Số chân của con nhện',8],['Số ngón tay trên một bàn tay',5],['Số màu trong cầu vồng',7]]
];
const SEQ1=[['2, 6, 12, 20, ?',30,'các tích n×(n+1)'],['3, 8, 15, 24, ?',35,'bình phương trừ 1'],
 ['1, 4, 9, 16, 25, ?',36,'các số chính phương'],['5, 10, 20, 40, ?',80,'nhân đôi mỗi bước'],
 ['4, 7, 11, 16, ?',22,'hiệu tăng dần 3, 4, 5…']];
const SEQ2=[['1, 1, 2, 3, 5, 8, ?',13,'mỗi số bằng tổng hai số liền trước'],['1, 2, 4, 7, 11, 16, ?',22,'hiệu tăng dần 1, 2, 3…'],
 ['2, 3, 5, 7, 11, 13, ?',17,'các số nguyên tố'],['100, 91, 82, 73, ?',64,'giảm 9 mỗi bước'],
 ['3, 6, 12, 24, ?',48,'nhân đôi mỗi bước']];
const OPTS=['🔴 Đỏ','🟢 Lục','🟡 Vàng','🔵 Xanh dương'];
const SOL=['🔵 Xanh dương','🟡 Vàng','🔴 Đỏ','🟢 Lục'];
const EMO=['🌸','🐦','⭐','🌙'];
const P=(function(){
  const counts=[0,0,0,0].map(()=>1+Math.floor(R()*9));
  const word=pick(WORDS),shift=2+Math.floor(R()*4);
  const cipher=word.split('').map(c=>String.fromCharCode((c.charCodeAt(0)-65+shift)%26+65)).join('');
  const riddle=pick(RIDDLES),s1=pick(SEQ1),s2=pick(SEQ2);
  return{counts:counts,safe:counts.join(''),word:word,shift:shift,cipher:cipher,riddle:riddle,
    keypad:riddle.map(r=>r[1]).join(''),s1:s1,s2:s2,final:''+s1[1]+s2[1],surprise:pick(['time','hint','joke'])};
})();
const DIFF={'Dễ':[900,4,1,'15 phút · 4 gợi ý'],'Thường':[600,3,1.5,'10 phút · 3 gợi ý'],'Khó':[360,1,2,'6 phút · 1 gợi ý']};
const HINT_PEN=30;

/* ============================ THẾ GIỚI ============================ */
const W=48,H=10,D=13,CS=16,NCX=W/CS,NCZ=1;
const world=new Uint8Array(W*H*D);
const I=(x,y,z)=>x+W*(z+D*y);
const inb=(x,y,z)=>x>=0&&x<W&&z>=0&&z<D&&y>=0&&y<H;
const get=(x,y,z)=>inb(x,y,z)?world[I(x,y,z)]:0;
const set=(x,y,z,v)=>{if(inb(x,y,z))world[I(x,y,z)]=v;};
function box(x0,y0,z0,x1,y1,z1,id){for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++)for(let x=x0;x<=x1;x++)set(x,y,z,id);}
/* id: 1 ván sàn, 2 tường gạch, 3 trần, 4 đèn, 5 giá sách, 6 sắt, 7 két, 8 gạch phòng thí nghiệm,
   9 đỏ, 10 lục, 11 vàng, 12 xanh, 13 mặt đồng hồ, 14 cửa, 15 thảm, 16 bàn, 17 vàng, 18 tủ, 19 bảng,
   20 cỏ, 21 đất, 22 thân cây, 23 lá */
box(0,0,0,W-1,0,D-1,21);
const FLOOR=[1,8,1];
for(let r=0;r<3;r++){
  const x0=r*12;
  box(x0,1,0,x0+12,1,12,FLOOR[r]);
  box(x0,2,0,x0+12,6,12,2);
  box(x0+1,2,1,x0+11,6,11,0);
  box(x0,7,0,x0+12,7,12,3);
  for(const rx of [3,6,9])for(const rz of [3,6,9])set(x0+rx,7,rz,4);
  if(r!==1)box(x0+4,1,4,x0+8,1,8,15);
}
const DOORS=[{x:12,z:6},{x:24,z:6},{x:36,z:6}];
for(const d of DOORS){set(d.x,2,d.z,14);set(d.x,3,d.z,14);}
box(37,1,0,W-1,1,D-1,20);
// phòng 1
box(8,2,1,10,4,1,5);
set(1,2,9,7);set(1,3,9,6);
box(5,2,9,7,2,9,16);
// phòng 2
box(16,2,2,19,2,2,16);set(16,3,2,9);set(17,3,2,10);set(18,3,2,11);set(19,3,2,12);
set(22,2,10,18);set(22,3,10,18);
set(14,2,10,17);
// phòng 3
box(29,2,1,31,2,1,6);box(29,3,1,31,5,1,6);set(30,4,1,13);
box(33,3,1,35,4,1,19);
// sân ngoài trời
function tree(x,z){
  const h=1,th=4+((R()*2)|0);
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
function openDoor(i){const d=DOORS[i];set(d.x,2,d.z,0);set(d.x,3,d.z,0);rebuildAround(d.x,d.z);}

/* ============================ TEXTURE ============================ */
const TS=16,COLS=8,ROWS=3;
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
const GRASS=[96,160,56],DIRT=[134,96,67];
fillTile(0,[162,130,78],.12,(x,y)=>(y%4===3)?[118,90,50]:null);
fillTile(1,[122,122,128],.15,(x,y)=>(y%8===7||(x+(((y>>3)&1)*8))%16===0)?[78,78,84]:null);
fillTile(2,[62,46,36],.15,(x,y)=>(y%4===3)?[44,32,24]:null);
fillTile(3,[255,220,120],.12,(x,y)=>((x+y)%5===0)?[255,245,185]:null);
const BOOK=[[170,40,40],[40,90,170],[60,140,60],[200,170,50],[120,60,150]];
fillTile(4,[120,85,45],.1,(x,y)=>(y%8<2)?[100,70,38]:BOOK[(x+((y>>3)*2))%5]);
fillTile(5,[190,190,196],.08,(x,y)=>(x===0||y===0||x===15||y===15)?[140,140,148]:null);
fillTile(6,[190,190,196],.08,(x,y)=>{const d=Math.hypot(x-7.5,y-7.5);
  if(d<1.6)return[235,205,70];if(d<4)return[62,62,70];
  return(x===0||y===0||x===15||y===15)?[140,140,148]:null;});
fillTile(7,[226,231,236],.06,(x,y)=>(x%8===0||y%8===0)?[190,196,202]:null);
fillTile(8,[200,50,50],.12);fillTile(9,[60,170,70],.12);
fillTile(10,[235,200,50],.12);fillTile(11,[60,100,210],.12);
fillTile(12,[240,230,200],.05,(x,y)=>{const d=Math.hypot(x-7.5,y-7.5);
  if(d>6.2&&d<7.8)return[40,40,40];
  if(x===8&&y>=3&&y<=8)return[30,30,30];
  if(y===8&&x>=8&&x<=11)return[30,30,30];return null;});
fillTile(13,[150,150,156],.08,(x,y)=>{
  if(x===3&&(y===8||y===9))return[240,200,60];
  return(x%4===1||y%8===0)?[98,98,104]:null;});
fillTile(14,[150,30,40],.1,(x,y)=>(x%15===0||y%15===0)?[220,180,60]:null);
fillTile(15,[92,62,36],.15,(x,y)=>(y%5===4)?[66,44,24]:null);
fillTile(16,[250,210,60],.1,(x,y)=>(x<3&&y<3)?[255,245,170]:null);
fillTile(17,[110,116,126],.1,(x,y)=>{
  if(x>=11&&x<=12&&y>=5&&y<=10)return[232,200,60];
  return(y===7||x===0||x===15)?[72,76,84]:null;});
fillTile(18,[30,72,52],.1,(x,y)=>{
  if(x<1||x>14||y<1||y>14)return[112,82,46];
  if((y===5&&x>3&&x<12)||(y===9&&x>3&&x<9))return[226,226,226];return null;});
fillTile(19,GRASS,.25);
fillTile(20,DIRT,.25,(x,y)=>y<4?GRASS:(y===4&&x%3===0?GRASS:null));
fillTile(21,DIRT,.3);
fillTile(22,[102,81,51],.2,(x,y)=>x%4===0?[78,60,36]:null);
fillTile(23,[48,120,40],.45,(x,y)=>((x*5+y*3)%7===0)?[28,88,26]:null);
const atlasTex=new THREE.CanvasTexture(atlas);
atlasTex.magFilter=atlasTex.minFilter=THREE.NearestFilter;atlasTex.generateMipmaps=false;
// [mặt trên, mặt bên, mặt dưới]
const BT={1:[0,0,0],2:[1,1,1],3:[2,2,2],4:[3,3,3],5:[0,4,0],6:[5,5,5],7:[5,6,5],8:[7,7,7],
 9:[8,8,8],10:[9,9,9],11:[10,10,10],12:[11,11,11],13:[12,12,12],14:[13,13,13],15:[14,14,14],
 16:[15,15,15],17:[16,16,16],18:[17,17,17],19:[18,18,18],20:[19,20,21],21:[21,21,21],22:[22,22,22],23:[23,23,23]};

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
      const n=pos.length/3,sh=b===4?1:f.s;
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
function rebuildAround(x,z){
  const cx=(x/CS)|0,cz=(z/CS)|0;
  buildChunk(cx,cz);
  if(x%CS===0&&cx>0)buildChunk(cx-1,cz);
  if(x%CS===CS-1&&cx<NCX-1)buildChunk(cx+1,cz);
}
for(let cx=0;cx<NCX;cx++)for(let cz=0;cz<NCZ;cz++)buildChunk(cx,cz);

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

// bức tranh treo tường (vẽ đúng số lượng cần đếm)
(function(){
  const c=document.createElement('canvas');c.width=256;c.height=160;
  const x=c.getContext('2d');
  const g=x.createLinearGradient(0,0,0,160);g.addColorStop(0,'#101a4a');g.addColorStop(1,'#2b3f7a');
  x.fillStyle=g;x.fillRect(0,0,256,160);
  x.font='24px sans-serif';x.textBaseline='middle';
  for(let i=0;i<4;i++)x.fillText(EMO[i].repeat(P.counts[i]),10,22+i*37);
  const tex=new THREE.CanvasTexture(c);
  const pic=new THREE.Mesh(new THREE.PlaneGeometry(3.6,2.25),new THREE.MeshBasicMaterial({map:tex}));
  pic.position.set(5.5,4.4,1.03);scene.add(pic);
  const fr=new THREE.Mesh(new THREE.BoxGeometry(3.9,2.55,0.08),new THREE.MeshBasicMaterial({color:0x8a5a2b}));
  fr.position.set(5.5,4.4,1.0);scene.add(fr);
})();

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

/* ============================ TRẠNG THÁI ============================ */
const S={started:false,ended:false,diff:'Thường',duration:600,startT:0,penalty:0,hints:3,used:0,
  flags:{},done:{},inv:[],mult:1,endT:0};
const ITEMS={'Chìa khóa đồng':['🗝️','Chiếc chìa khóa đồng nhỏ, vẫn còn âm ấm.'],
 'Mật thư':['📜',null],'Dung dịch phát sáng':['🧪','Chất lỏng xanh lơ, tỏa ánh sáng dịu.'],
 'Thẻ từ':['💳','Thẻ từ có vạch đỏ, in chữ “CỬA THÉP”.'],
 'Bánh răng vàng':['⚙️','Bánh răng vàng nặng tay, như khớp với một cỗ máy lớn.']};
const has=n=>S.inv.indexOf(n)>=0;
function timeLeft(){const ref=S.ended?S.endT:performance.now();return S.duration-(ref-S.startT)/1000-S.penalty;}
let toastTimer=null;
function toast(html,ms){
  const t=$('toast');t.innerHTML=html;t.style.display='block';
  clearTimeout(toastTimer);toastTimer=setTimeout(()=>{t.style.display='none';},ms||4500);
}
function give(name,msg){if(!has(name))S.inv.push(name);toast(msg,5500);}

/* ============================ LOGIC CÂU ĐỐ ============================ */
function trySafe(c){if(norm(c)!==P.safe)return false;S.flags.safe=true;S.done.safe=true;
  give('Chìa khóa đồng','🔓 Cạch! Két sắt mở. Bạn nhận được <b>chìa khóa đồng</b>.');return true;}
function useKeyOnDesk(){if(!has('Chìa khóa đồng')||S.flags.drawer)return false;S.flags.drawer=true;S.done.desk=true;
  give('Mật thư','📂 Ngăn kéo mở ra! Bạn tìm thấy một <b>mật thư</b> viết bằng mật mã.');return true;}
function tryDoor0(w){if(norm(w)!==P.word)return false;S.flags.door0=true;S.done.door0=true;openDoor(0);
  toast('🚪 <b>Click!</b> Cánh cửa gỗ bật mở. Hãy sang phòng bên cạnh.',5000);return true;}
function tryPotion(arr){if(arr.length!==4||arr.join()!==SOL.join())return false;S.flags.potion=true;S.done.bottles=true;
  give('Dung dịch phát sáng','✨ Bình sủi bọt rồi tỏa sáng! Bạn nhận được <b>dung dịch phát sáng</b>.');return true;}
function useWall(){if(!has('Dung dịch phát sáng')||S.flags.wall)return false;S.flags.wall=true;S.done.wall=true;
  toast('✨ Chữ phát sáng hiện lên trên tường! Đó là <b>ba câu đố</b>.',5000);return true;}
function tryCabinet(c){if(norm(c)!==P.keypad)return false;S.flags.cabinet=true;S.done.cabinet=true;
  if(!has('Thẻ từ'))S.inv.push('Thẻ từ');if(!has('Bánh răng vàng'))S.inv.push('Bánh răng vàng');
  toast('🔓 Tủ mở! Bên trong có một <b>thẻ từ</b> và một <b>bánh răng vàng</b>.',5500);return true;}
function openGift(){if(S.flags.gift)return;S.flags.gift=true;S.done.gift=true;
  if(P.surprise==='time'){S.penalty-=45;toast('🎁 <b>BẤT NGỜ!</b> Đồng hồ cát phép thuật: bạn được <b>cộng 45 giây</b>!',6000);}
  else if(P.surprise==='hint'){S.hints++;toast('🎁 <b>BẤT NGỜ!</b> Một con đom đóm giấy cho bạn <b>thêm 1 lượt gợi ý</b>.',6000);}
  else toast('🎁 <b>BẤT NGỜ!</b> Chú hề lò xo bật ra: “Vì sao đồng hồ hay đi muộn? Vì nó tích tắc quá nhiều!”',7000);}
function useCard(){if(!has('Thẻ từ')||S.flags.door1)return false;S.flags.door1=true;S.done.door1=true;openDoor(1);
  toast('💚 Đèn xanh bật sáng. Cửa thép trượt mở!',5000);return true;}
function useGear(){if(!has('Bánh răng vàng')||S.flags.clock)return false;S.flags.clock=true;S.done.clock=true;
  toast('⚙️ Bánh răng khớp vào! Đồng hồ <b>bắt đầu chạy</b> và một ngăn bí mật bật mở.',5500);return true;}
function tryExit(c){if(norm(c)!==P.final)return false;S.flags.exit=true;S.done.exit=true;openDoor(2);
  toast('🌞 Cửa thoát hiểm mở! <b>Hãy bước ra ngoài!</b>',6000);return true;}
function currentHint(){
  const f=S.flags;
  if(!f.safe)return f.seenPainting?'Đếm từng loại hình trong <b>bức tranh</b>, ghép 4 số theo thứ tự hoa–chim–sao–trăng cho <b>két sắt</b>.':'Hãy nhìn thật kỹ <b>bức tranh</b>, có thứ để đếm.';
  if(!f.drawer)return 'Chìa khóa đồng hợp với ổ khóa ở <b>bàn làm việc</b>.';
  if(!f.door0)return f.seenShelf?'Lùi '+P.shift+' bước mỗi chữ cái. Chữ đầu “'+P.cipher[0]+'” sẽ thành “'+P.word[0]+'”.':'Hãy xem <b>giá sách</b>, có thứ giúp bạn đọc mật thư.';
  if(!f.potion)return 'Lục luôn đứng ngay sau Đỏ và Đỏ không đứng đầu. Đáp án bắt đầu bằng 🔵 Xanh dương.';
  if(!f.wall)return 'Dung dịch phát sáng làm hiện chữ vô hình trên <b>bức tường</b> ở phòng này.';
  if(!f.cabinet)return 'Giải ba câu đố trên tường, ghép ba chữ số theo thứ tự cho <b>tủ kim loại</b>.';
  if(!f.door1)return '<b>Thẻ từ</b> dùng cho cánh cửa thép.';
  if(!f.clock)return '<b>Bánh răng vàng</b> thuộc về chiếc đồng hồ khổng lồ.';
  return 'Quy luật dãy ở đồng hồ: '+P.s1[2]+'. Quy luật dãy trên bảng: '+P.s2[2]+'. Mã = đáp án đồng hồ rồi đáp án bảng.';
}
function useHint(){
  if(!S.started||S.ended)return;
  if(S.hints<=0){toast('Bạn đã hết lượt gợi ý.',2500);return;}
  S.hints--;S.used++;S.penalty+=HINT_PEN;
  toast('💡 <span class="hint"><b>Gợi ý:</b></span> '+currentHint(),9000);
}

/* ============================ BẢNG TƯƠNG TÁC ============================ */
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
function fb(t){const e=q('#fb');if(e)e.textContent=t;}
const okBtn='<button id="ok" class="pb alt">Đóng</button>';
function codeUI(label,len,ph){
  return '<p>'+label+'</p><input id="c1" inputmode="'+(len?'numeric':'text')+'" maxlength="'+(len||12)+'" placeholder="'+ph+'" autocomplete="off"><button id="go" class="pb">Thử</button><div id="fb"></div>';
}
function bindClose(){onBtn('ok',closePanel);}

function oPainting(){
  S.flags.seenPainting=true;S.done.painting=true;
  let rows='';EMO.forEach((e,i)=>{rows+='<div class="big">'+e.repeat(P.counts[i])+'</div>';});
  openPanel('🖼️ Bức tranh','<p>Một khu vườn ban đêm, từng thứ được vẽ rất rõ ràng, như thể ai đó muốn bạn đếm chúng:</p>'+rows+
    '<p class="cap">Góc tranh ghi: “Đếm theo thứ tự: hoa, chim, sao, trăng.”</p>'+okBtn);bindClose();
}
function oShelf(){
  S.flags.seenShelf=true;S.done.shelf=true;
  openPanel('📚 Giá sách','<p>Cuốn <b>“Julius Caesar”</b> kẹp một mẩu giấy:</p><p class="hint">“Muốn đọc mật thư, hãy <b>lùi '+P.shift+' bước</b> trong bảng chữ cái cho mỗi chữ cái.”</p>'+
    '<p class="cap">Ví dụ lùi 1 bước: C → B, B → A. Lùi quá A thì quay vòng về Z.</p>'+okBtn);bindClose();
}
function oSafe(){
  if(S.flags.safe){openPanel('🔐 Két sắt','<p>Két đã mở, bên trong trống rỗng.</p>'+okBtn);bindClose();return;}
  openPanel('🔐 Két sắt',codeUI('Két sắt có bàn phím <b>4 chữ số</b>.',4,'____'));
  onBtn('go',()=>{if(trySafe(q('#c1').value))closePanel();else fb('❌ Két kêu bíp bíp. Sai mã!');});
}
function oDesk(){
  if(S.flags.drawer){openPanel('🗄️ Bàn làm việc','<p>Ngăn kéo đã mở, chỉ còn bụi.</p>'+okBtn);bindClose();return;}
  if(has('Chìa khóa đồng')){
    openPanel('🗄️ Bàn làm việc','<p>Ngăn kéo khóa kín, ổ khóa hình bông hoa.</p><button id="use" class="pb">🗝️ Dùng chìa khóa đồng</button>');
    onBtn('use',()=>{useKeyOnDesk();closePanel();});
  }else{openPanel('🗄️ Bàn làm việc','<p>Ngăn kéo khóa kín. Bạn cần một chiếc chìa khóa phù hợp.</p>'+okBtn);bindClose();}
}
function oDoor0(){
  if(S.flags.door0){openPanel('🚪 Cửa gỗ','<p>Cửa đã mở. Hãy bước sang phòng tiếp theo.</p>'+okBtn);bindClose();return;}
  openPanel('🚪 Cửa gỗ',codeUI('Bàn phím chữ cái với <b>6 ô</b>. Hãy nhập mật khẩu.',6,'______'));
  onBtn('go',()=>{if(tryDoor0(q('#c1').value))closePanel();else fb('❌ Bàn phím chớp đỏ. Sai mật khẩu!');});
}
function oBottles(){
  if(S.flags.potion){openPanel('🧪 Bàn hóa chất','<p>Dung dịch phát sáng đã nằm trong túi bạn.</p>'+okBtn);bindClose();return;}
  let sel='';for(let i=0;i<4;i++)sel+='<label>Lần đổ thứ '+(i+1)+'<select id="b'+i+'"><option value="">— chọn lọ —</option>'+OPTS.map(o=>'<option>'+o+'</option>').join('')+'</select></label>';
  openPanel('🧪 Bàn hóa chất','<p>Bốn lọ màu và một bình trống. Tờ ghi chú viết:</p><p class="hint">• 🟢 Lục đổ <b>ngay sau</b> 🔴 Đỏ.<br>• 🔴 Đỏ <b>không</b> đổ đầu tiên.<br>• 🟡 Vàng <b>không</b> đứng đầu và phải <b>cạnh</b> 🔵 Xanh dương.<br>• 🔵 Xanh dương <b>không</b> đứng cuối.</p>'+sel+'<button id="go" class="pb">⚗️ Đổ vào bình</button><div id="fb"></div>');
  onBtn('go',()=>{
    const a=[0,1,2,3].map(i=>q('#b'+i).value);
    if(a.indexOf('')>=0||new Set(a).size<4){fb('⚠️ Hãy chọn đủ 4 lọ khác nhau.');return;}
    if(tryPotion(a))closePanel();else fb('❌ Bình sủi bọt, khói tím bốc lên. Sai thứ tự!');
  });
}
function oWall(){
  if(!S.flags.potion){openPanel('🧱 Bức tường','<p>Bức tường trắng trơn, nhưng thoang thoảng mùi hóa chất, như thể có gì đó vô hình trên đó.</p>'+okBtn);bindClose();return;}
  if(!S.flags.wall){openPanel('🧱 Bức tường','<p>Dung dịch trong túi bạn đang rung nhẹ.</p><button id="use" class="pb">🧪 Rưới dung dịch lên tường</button>');
    onBtn('use',()=>{useWall();oWall();});return;}
  let r='';P.riddle.forEach((x,i)=>{r+='<p><b>'+(i+1)+'.</b> '+x[0]+'</p>';});
  openPanel('🧱 Bức tường','<p>Chữ phát sáng hiện ra:</p>'+r+'<p class="cap">Ba đáp án (mỗi đáp án một chữ số), ghép theo thứ tự, tạo thành mật mã.</p>'+okBtn);bindClose();
}
function oCabinet(){
  if(S.flags.cabinet){openPanel('🗃️ Tủ kim loại','<p>Tủ đã mở, bạn đã lấy hết đồ.</p>'+okBtn);bindClose();return;}
  openPanel('🗃️ Tủ kim loại',codeUI('Bảng số <b>3 chữ số</b>.',3,'___'));
  onBtn('go',()=>{if(tryCabinet(q('#c1').value))closePanel();else fb('❌ Bảng số kêu bíp bíp. Sai mã!');});
}
function oGift(){
  if(S.flags.gift){openPanel('🎁 Hộp quà','<p>Hộp quà đã trống rỗng.</p>'+okBtn);bindClose();return;}
  openPanel('🎁 Hộp quà','<p>Hộp quà vàng thắt ruy băng, có thẻ ghi: <i>“Dành cho kẻ dám mở.”</i></p><button id="use" class="pb">🎁 Mở hộp quà</button>');
  onBtn('use',()=>{openGift();closePanel();});
}
function oDoor1(){
  if(S.flags.door1){openPanel('🚪 Cửa thép','<p>Cửa thép đã mở. Hãy sang phòng cuối cùng.</p>'+okBtn);bindClose();return;}
  if(has('Thẻ từ')){openPanel('🚪 Cửa thép','<p>Cánh cửa thép nặng nề, bên cạnh có khe quẹt thẻ.</p><button id="use" class="pb">💳 Quẹt thẻ từ</button>');
    onBtn('use',()=>{useCard();closePanel();});}
  else{openPanel('🚪 Cửa thép','<p>Cánh cửa thép nặng nề, bên cạnh có khe quẹt thẻ. Bạn cần một tấm thẻ từ.</p>'+okBtn);bindClose();}
}
function oClock(){
  if(S.flags.clock){openPanel('🕰️ Đồng hồ cổ','<p>Đồng hồ đã chạy! Trong ngăn bí mật có tờ giấy:</p><p class="hint"><b>Phần 1 của mã:</b><br>'+P.s1[0]+'</p>'+okBtn);bindClose();return;}
  if(has('Bánh răng vàng')){openPanel('🕰️ Đồng hồ cổ','<p>Chiếc đồng hồ cao ba mét, kim đứng im, trục đang chờ một bánh răng.</p><button id="use" class="pb">⚙️ Lắp bánh răng vàng</button>');
    onBtn('use',()=>{useGear();oClock();});}
  else{openPanel('🕰️ Đồng hồ cổ','<p>Kim đứng im. Sau mặt kính, một trục trống đang thiếu một bánh răng…</p>'+okBtn);bindClose();}
}
function oBoard(){
  S.done.board=true;
  openPanel('📝 Bảng phấn','<p>Dòng chữ phấn: <i>“Mã mở cửa gồm hai phần ghép nối.”</i></p><p class="hint"><b>Phần 2 của mã:</b><br>'+P.s2[0]+'</p><p class="cap">Phần 1 nằm đâu đó bên trong chiếc đồng hồ…</p>'+okBtn);bindClose();
}
function oExit(){
  if(S.flags.exit){openPanel('🚪 Cửa thoát hiểm','<p>Cửa đã mở! Hãy bước ra ngoài.</p>'+okBtn);bindClose();return;}
  openPanel('🚪 Cửa thoát hiểm',codeUI('Ô nhập <b>4 chữ số</b>: hai số đầu là đáp án dãy ở <b>đồng hồ</b>, hai số sau là đáp án dãy trên <b>bảng phấn</b>.',4,'____'));
  onBtn('go',()=>{if(tryExit(q('#c1').value))closePanel();else fb('❌ Cửa rung lên rồi im lìm. Sai mã!');});
}
function oInventory(){
  if(!S.inv.length){openPanel('🎒 Túi đồ','<p>Túi đồ đang trống.</p>'+okBtn);bindClose();return;}
  let h='';S.inv.forEach(n=>{const it=ITEMS[n];const d=n==='Mật thư'?'Tờ giấy ghi: <b>'+P.cipher+'</b>':it[1];
    h+='<div class="item">'+it[0]+' <b>'+n+'</b> — '+d+'</div>';});
  openPanel('🎒 Túi đồ',h+okBtn);bindClose();
}
// vật thể tương tác: x, y, z là vị trí đứng gần
const OBJS=[
 {id:'painting',label:'Bức tranh',x:5.5,z:2.6,fn:oPainting},
 {id:'shelf',label:'Giá sách',x:9,z:2.6,fn:oShelf},
 {id:'safe',label:'Két sắt',x:2.6,z:9,fn:oSafe},
 {id:'desk',label:'Bàn làm việc',x:6,z:8,fn:oDesk},
 {id:'door0',label:'Cửa gỗ',x:11,z:6.5,fn:oDoor0},
 {id:'bottles',label:'Bàn hóa chất',x:17.5,z:3.6,fn:oBottles},
 {id:'wall',label:'Bức tường lạ',x:22,z:2.6,fn:oWall},
 {id:'cabinet',label:'Tủ kim loại',x:21,z:10,fn:oCabinet},
 {id:'gift',label:'Hộp quà',x:14.6,z:9.4,fn:oGift},
 {id:'door1',label:'Cửa thép',x:23,z:6.5,fn:oDoor1},
 {id:'clock',label:'Đồng hồ cổ',x:30,z:2.6,fn:oClock},
 {id:'board',label:'Bảng phấn',x:34,z:2.6,fn:oBoard},
 {id:'exit',label:'Cửa thoát hiểm',x:35,z:6.5,fn:oExit}
];
// dấu hiệu "?" vàng bay trên vật thể chưa xử lý
const markGeo=new THREE.OctahedronGeometry(0.2);
const markMat=new THREE.MeshBasicMaterial({color:0xffd400});
OBJS.forEach(o=>{o.mark=new THREE.Mesh(markGeo,markMat);o.mark.position.set(o.x,5.2,o.z);scene.add(o.mark);});

/* ============================ NGƯỜI CHƠI ============================ */
const SPAWN={x:6.5,y:2.0001,z:6.5};
const Pl={x:SPAWN.x,y:SPAWN.y,z:SPAWN.z};
let vy=0,onGround=false,yaw=0,pitch=-0.12,view=1;
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
  if(k==='i')oInventory();
});
window.addEventListener('keyup',e=>{keys[e.key.toLowerCase()]=false;});
window.addEventListener('blur',()=>{for(const k in keys)keys[k]=false;});
const cv=renderer.domElement;
cv.addEventListener('contextmenu',e=>e.preventDefault());
const looks={};
cv.addEventListener('pointerdown',e=>{
  window.focus();
  looks[e.pointerId]={x:e.clientX,y:e.clientY};
  cv.setPointerCapture(e.pointerId);
});
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
hold('bInv',oInventory);
hold('bHint',useHint);
hold('bView',()=>{view=(view+1)%3;});

/* ============================ BẮT ĐẦU / KẾT THÚC ============================ */
function bestKey(){return 'escape3d_best';}
function getBest(){try{return +localStorage.getItem(bestKey())||0;}catch(e){return 0;}}
function setBest(v){try{localStorage.setItem(bestKey(),String(v));}catch(e){}}
function showStart(){
  const ov=$('overlay');ov.style.display='flex';
  let h='<h2>⏳ Escape Time 3D</h2><p>Bạn bị nhốt trong dinh thự khối vuông có <b>3 căn phòng</b>. Khám phá, giải đố, gom vật phẩm và thoát ra ngoài ánh nắng trước khi hết giờ!</p>'+
   '<p class="cap">Đi lại bằng cần trái, kéo màn hình để nhìn. Lại gần vật thể có dấu <b style="color:#ffd400">◆</b> vàng rồi bấm ✋ (hoặc phím E). Mã và câu đố khác nhau mỗi lần chơi.</p>';
  for(const k in DIFF)h+='<button class="pb'+(k==='Thường'?'':' alt')+'" data-d="'+k+'">'+k+' — '+DIFF[k][3]+'</button>';
  const b=getBest();if(b)h+='<p class="cap">🏆 Kỷ lục trên máy này: <b>'+b+'</b> điểm</p>';
  $('ovBody').innerHTML=h;
  $('ovBody').querySelectorAll('button[data-d]').forEach(bt=>bt.addEventListener('click',()=>startGame(bt.getAttribute('data-d'))));
}
function startGame(d){
  S.diff=d;S.duration=DIFF[d][0];S.hints=DIFF[d][1];S.mult=DIFF[d][2];
  S.startT=performance.now();S.started=true;
  $('overlay').style.display='none';$('cross').style.display='none';
  toast('⏳ Cánh cửa sập lại sau lưng bạn. <b>Đồng hồ bắt đầu chạy!</b> Hãy nhìn quanh phòng.',6000);
}
function endGame(win){
  if(S.ended)return;
  S.ended=true;S.endT=performance.now();closePanel();
  const left=Math.max(0,timeLeft());let h;
  if(win){
    const score=Math.floor((left*10+S.hints*100+(S.used===0?500:0))*S.mult);
    const ratio=left/S.duration,stars=ratio>=.5?3:ratio>=.25?2:1;
    const best=getBest();const nb=score>best;if(nb)setBest(score);
    h='<h2>🎉 BẠN ĐÃ THOÁT!</h2><p style="font-size:34px;text-align:center;margin:4px">'+'⭐'.repeat(stars)+'☆'.repeat(3-stars)+'</p>'+
      '<p>Điểm: <b>'+score+'</b>'+(nb?' 🏆 <b>kỷ lục mới!</b>':'')+'<br>Thời gian còn lại: <b>'+fmt(left)+'</b><br>Gợi ý đã dùng: <b>'+S.used+'</b> · Độ khó: <b>'+S.diff+'</b></p>';
  }else{
    h='<h2>⌛ HẾT GIỜ!</h2><p>Cánh cửa khóa lại mãi mãi… nhưng bạn có thể thử lại với căn phòng hoàn toàn mới.</p>'+
      '<details><summary>🔍 Xem đáp án lượt này</summary><p class="cap">Két sắt: <b>'+P.safe+'</b><br>Mật khẩu cửa gỗ: <b>'+P.word+'</b> (mật thư '+P.cipher+', lùi '+P.shift+')<br>Thứ tự đổ lọ: '+SOL.join(' → ')+
      '<br>Tủ kim loại: <b>'+P.keypad+'</b><br>Mã thoát hiểm: <b>'+P.final+'</b></p></details>';
  }
  h+='<button id="again" class="pb">🔄 Chơi lại (câu đố mới)</button>';
  $('ovBody').innerHTML=h;$('overlay').style.display='flex';
  $('again').addEventListener('click',()=>location.reload());
}

/* ============================ VÒNG LẶP ============================ */
let lastSec=-1;
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
  vy=Math.max(-40,vy-25*dt);
  if(active&&(jumpHeld||keys[' '])&&onGround){vy=8;onGround=false;}
  moveH('x',dirx*speed*dt,moving);moveH('z',dirz*speed*dt,moving);
  const oy=Pl.y;Pl.y+=vy*dt;
  if(collides()){if(vy<0){Pl.y=Math.floor(Pl.y)+1.0001;onGround=true;}else Pl.y=oy;vy=0;}
  else onGround=false;
  if(Pl.y<-10){Pl.x=SPAWN.x;Pl.y=SPAWN.y+2;Pl.z=SPAWN.z;vy=0;}

  // tương tác gần nhất
  nearObj=null;
  if(active){
    let best=2.6;
    for(const o of OBJS){const d=Math.hypot(o.x-Pl.x,o.z-Pl.z);if(d<best){best=d;nearObj=o;}}
  }
  const pr=$('prompt'),ba=$('bAct');
  if(nearObj){pr.style.display='block';pr.textContent='✋ '+nearObj.label;ba.classList.add('near');}
  else{pr.style.display='none';ba.classList.remove('near');}
  const t=performance.now()*0.003;
  for(const o of OBJS){o.mark.visible=!S.done[o.id];o.mark.position.y=5.2+Math.sin(t+o.x)*0.15;o.mark.rotation.y=t;}

  // thời gian, thắng, thua
  if(S.started&&!S.ended){
    const left=timeLeft(),sec=Math.ceil(left);
    if(sec!==lastSec){
      lastSec=sec;const tm=$('timer');tm.textContent='⏳ '+fmt(left);
      tm.className='ui '+(left<60?'danger':left<180?'warn':'ok');
      $('hn').textContent=S.hints;
    }
    if(left<=0)endGame(false);
    else if(S.flags.exit&&Pl.x>37.7)endGame(true);
  }else if(!S.started){$('timer').textContent='⏳ Escape Time 3D';$('hn').textContent='';}

  // hoạt ảnh
  const walking=moving&&onGround;
  amp+=((walking?1:0)-amp)*Math.min(1,dt*10);
  walkPhase+=dt*speed*2.1*(walking?1:0);
  const sw=Math.sin(walkPhase)*0.9*amp;
  legR.rotation.x=sw;legL.rotation.x=-sw;armL.rotation.x=sw;
  swing=Math.max(0,swing-dt*3.2);
  armR.rotation.x=-sw-Math.sin(swing*Math.PI)*1.7;
  head.rotation.x=-pitch*0.8;
  model.position.set(Pl.x,Pl.y,Pl.z);model.rotation.y=yaw+Math.PI;

  // camera
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
window.__T={S:S,P:P,Pl:Pl,world:world,get:get,trySafe:trySafe,useKeyOnDesk:useKeyOnDesk,tryDoor0:tryDoor0,
  tryPotion:tryPotion,useWall:useWall,tryCabinet:tryCabinet,useCard:useCard,useGear:useGear,tryExit:tryExit,
  currentHint:currentHint,SOL:SOL,update:update,startGame:startGame,has:has,DOORS:DOORS,keys:keys,joy:joy,OBJS:OBJS};
})();
</script>
</body>
</html>
"""

components.html(HTML, height=720, scrolling=False)
