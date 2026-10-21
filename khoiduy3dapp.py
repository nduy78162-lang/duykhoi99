"""
🧱 KHỐI DUY 3D — game voxel kiểu Minecraft chạy trên Streamlit
==============================================================
Cài đặt:  pip install "streamlit>=1.30"
Chạy:     streamlit run khoiduy3d.py

Game dùng three.js (tải từ cdnjs) nhúng vào Streamlit, nên máy cần có mạng.

Điều khiển
  Điện thoại : cần trái = đi · kéo ngón tay lên màn hình = nhìn · ⬆ nhảy
               ⛏ đào (giữ để đào liên tục) · 🧱 đặt khối · chạm ô trên cùng để đổi khối
  Máy tính   : W A S D = đi · Space = nhảy · kéo chuột trái = nhìn
               click trái = đào · click phải = đặt khối · 1-8 / lăn chuột = đổi khối
               V = đổi góc nhìn · F = bay/hạ · Shift = chạy (hoặc đi xuống khi bay)
"""

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="Khối Duy 3D",
    page_icon="🧱",
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
html,body{margin:0;height:100%;overflow:hidden;background:#87ceeb;
  font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  -webkit-user-select:none;user-select:none;touch-action:none;-webkit-touch-callout:none}
canvas{display:block;touch-action:none}
.ui{position:absolute;color:#fff;text-shadow:0 1px 3px #000}
#hotbar{top:8px;left:50%;transform:translateX(-50%);display:flex;gap:4px;
  background:rgba(0,0,0,.4);padding:4px;border-radius:8px}
.slot{width:34px;height:34px;border:2px solid #555;border-radius:4px;
  image-rendering:pixelated;background-color:#444}
.slot.sel{border-color:#fff;box-shadow:0 0 8px #fff}
#hud{top:58px;left:50%;transform:translateX(-50%);font-size:12px;white-space:nowrap}
#msg{top:50%;left:50%;transform:translate(-50%,-50%);font-size:16px;text-align:center;
  background:rgba(0,0,0,.45);padding:10px 16px;border-radius:10px;max-width:80%}
#cross{top:50%;left:50%;width:18px;height:18px;transform:translate(-50%,-50%);pointer-events:none}
#cross:before,#cross:after{content:"";position:absolute;background:rgba(255,255,255,.85);
  box-shadow:0 0 2px #000}
#cross:before{left:8px;top:0;width:2px;height:18px}
#cross:after{left:0;top:8px;width:18px;height:2px}
.btn{position:absolute;border-radius:50%;background:rgba(0,0,0,.4);
  border:2px solid rgba(255,255,255,.75);color:#fff;display:flex;align-items:center;
  justify-content:center;font-size:24px;touch-action:none}
.btn:active,.btn.on{background:rgba(255,255,255,.35)}
#joy{left:18px;bottom:24px;width:124px;height:124px;border-radius:50%;
  background:rgba(255,255,255,.16);border:2px solid rgba(255,255,255,.5);touch-action:none}
#knob{position:absolute;left:36px;top:36px;width:52px;height:52px;border-radius:50%;
  background:rgba(255,255,255,.55);pointer-events:none}
#bJump{right:20px;bottom:26px;width:66px;height:66px}
#bBreak{right:24px;bottom:106px;width:62px;height:62px}
#bPlace{right:98px;bottom:52px;width:62px;height:62px}
#bDown{right:98px;bottom:126px;width:50px;height:50px;font-size:20px;display:none}
#bView{top:8px;right:8px;width:44px;height:44px;font-size:20px}
#bFly{top:60px;right:8px;width:44px;height:44px;font-size:20px}
</style>
</head>
<body>
<div id="msg" class="ui">⏳ Đang tạo thế giới…</div>
<div id="cross" class="ui" style="display:none"></div>
<div id="hotbar" class="ui"></div>
<div id="hud" class="ui"></div>
<div id="joy" class="ui"><div id="knob"></div></div>
<div id="bJump" class="btn">⬆</div>
<div id="bBreak" class="btn">⛏</div>
<div id="bPlace" class="btn">🧱</div>
<div id="bDown" class="btn">⬇</div>
<div id="bView" class="btn">👁</div>
<div id="bFly" class="btn">🕊</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
  onerror="document.getElementById('msg').textContent='❌ Không tải được three.js. Hãy kiểm tra kết nối mạng rồi tải lại trang.'"></script>
<script>
(function(){
if(typeof THREE==='undefined')return;
const $=id=>document.getElementById(id);

/* ============================ THẾ GIỚI ============================ */
const W=48,H=32,D=48,CS=16,NCX=W/CS,NCZ=D/CS;
const world=new Uint8Array(W*H*D);
const I=(x,y,z)=>x+W*(z+D*y);
const inb=(x,y,z)=>x>=0&&x<W&&z>=0&&z<D&&y>=0&&y<H;
const get=(x,y,z)=>inb(x,y,z)?world[I(x,y,z)]:0;
const set=(x,y,z,v)=>{if(inb(x,y,z))world[I(x,y,z)]=v;};

function rnd(seed){return function(){seed|=0;seed=seed+0x6D2B79F5|0;
  let t=Math.imul(seed^seed>>>15,1|seed);t=t+Math.imul(t^t>>>7,61|t)^t;
  return((t^t>>>14)>>>0)/4294967296;};}
const R=rnd((Math.random()*1e9)|0);
const G=[];for(let i=0;i<64*64;i++)G.push(R());
const g2=(i,j)=>G[(i&63)+64*(j&63)];
function vn(x,z){
  const xi=Math.floor(x),zi=Math.floor(z),xf=x-xi,zf=z-zi;
  const u=xf*xf*(3-2*xf),v=zf*zf*(3-2*zf);
  const a=g2(xi,zi)+(g2(xi+1,zi)-g2(xi,zi))*u;
  const b=g2(xi,zi+1)+(g2(xi+1,zi+1)-g2(xi,zi+1))*u;
  return a+(b-a)*v;
}
// 1 cỏ, 2 đất, 3 đá, 4 gỗ, 5 lá, 6 cát, 7 ván, 8 gạch
const hm=new Int16Array(W*D);
for(let z=0;z<D;z++)for(let x=0;x<W;x++){
  const h=Math.floor(6+vn(x/14,z/14)*10+vn(x/5,z/5)*2.5);
  hm[x+W*z]=h;
  const sandy=h<=8;
  for(let y=0;y<=h;y++){
    let b;
    if(y===h)b=sandy?6:1;
    else if(y>h-4)b=sandy?6:2;
    else b=3;
    set(x,y,z,b);
  }
}
function tree(x,z,h){
  const th=4+((R()*2)|0);
  for(let i=1;i<=th;i++)set(x,h+i,z,4);
  for(let dy=th-1;dy<=th+1;dy++){
    const r=dy>=th+1?1:2;
    for(let dx=-r;dx<=r;dx++)for(let dz=-r;dz<=r;dz++){
      if(Math.abs(dx)===r&&Math.abs(dz)===r&&dy<th+1&&R()<.5)continue;
      if(!get(x+dx,h+dy,z+dz))set(x+dx,h+dy,z+dz,5);
    }
  }
}
for(let i=0;i<60;i++){
  const x=3+((R()*(W-6))|0),z=3+((R()*(D-6))|0),h=hm[x+W*z];
  if(get(x,h,z)!==1)continue;
  if(Math.abs(x-W/2)<4&&Math.abs(z-D/2)<4)continue;
  tree(x,z,h);
}

/* ============================ TEXTURE ============================ */
const TS=16,COLS=8,ROWS=2;
const atlas=document.createElement('canvas');
atlas.width=TS*COLS;atlas.height=TS*ROWS;
const ac=atlas.getContext('2d');
const cl=v=>Math.max(0,Math.min(255,v|0));
function fillTile(t,c,v,fn){
  for(let y=0;y<TS;y++)for(let x=0;x<TS;x++){
    let q=c;
    if(fn){const r=fn(x,y);if(r)q=r;}
    const k=1+(Math.random()-.5)*v;
    ac.fillStyle='rgb('+cl(q[0]*k)+','+cl(q[1]*k)+','+cl(q[2]*k)+')';
    ac.fillRect((t%COLS)*TS+x,((t/COLS)|0)*TS+y,1,1);
  }
}
const GRASS=[96,160,56],DIRT=[134,96,67];
fillTile(0,GRASS,.25);
fillTile(1,DIRT,.25,(x,y)=>y<4?GRASS:(y===4&&x%3===0?GRASS:null));
fillTile(2,DIRT,.3);
fillTile(3,[125,125,125],.3,(x,y)=>((x*7+y*13)%11===0)?[95,95,95]:null);
fillTile(4,[102,81,51],.2,(x,y)=>x%4===0?[78,60,36]:null);
fillTile(5,[160,130,80],.15,(x,y)=>{
  const d=Math.max(Math.abs(x-7.5),Math.abs(y-7.5));
  return(Math.floor(d)%3===0)?[118,90,54]:null;});
fillTile(6,[48,120,40],.45,(x,y)=>((x*5+y*3)%7===0)?[28,88,26]:null);
fillTile(7,[219,205,150],.12);
fillTile(8,[162,130,78],.12,(x,y)=>(y%4===3)?[118,90,50]:null);
fillTile(9,[150,70,58],.1,(x,y)=>(y%4===3||(x+(((y>>2)%2)*4))%8===0)?[192,182,172]:null);

const atlasTex=new THREE.CanvasTexture(atlas);
atlasTex.magFilter=atlasTex.minFilter=THREE.NearestFilter;
atlasTex.generateMipmaps=false;
// [mặt trên, mặt bên, mặt dưới]
const BT={1:[0,1,2],2:[2,2,2],3:[3,3,3],4:[5,4,5],5:[6,6,6],6:[7,7,7],7:[8,8,8],8:[9,9,9]};

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
scene.fog=new THREE.Fog(0x9fd3f2,22,70);
const chunks={};
function buildChunk(cx,cz){
  const pos=[],uv=[],col=[],ind=[];
  const e=0.002;
  for(let y=0;y<H;y++)for(let z=cz*CS;z<(cz+1)*CS;z++)for(let x=cx*CS;x<(cx+1)*CS;x++){
    const b=get(x,y,z);if(!b)continue;
    for(const f of FACES){
      const nx=x+f.dir[0],ny=y+f.dir[1],nz=z+f.dir[2];
      if(ny<0||get(nx,ny,nz))continue;
      const t=BT[b][f.dir[1]>0?0:f.dir[1]<0?2:1];
      const tc=t%COLS,tr=(t/COLS)|0;
      const u0=tc/COLS+e,u1=(tc+1)/COLS-e;
      const v0=1-(tr+1)/ROWS+e,v1=1-tr/ROWS-e;
      const n=pos.length/3;
      for(const c of f.c){
        pos.push(x+c.p[0],y+c.p[1],z+c.p[2]);
        uv.push(c.u[0]?u1:u0,c.u[1]?v1:v0);
        col.push(f.s,f.s,f.s);
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
  g.setIndex(ind);
  g.computeBoundingSphere();
  const m=new THREE.Mesh(g,worldMat);
  chunks[key]=m;scene.add(m);
}
function rebuildAround(x,z){
  const cx=(x/CS)|0,cz=(z/CS)|0;
  buildChunk(cx,cz);
  if(x%CS===0&&cx>0)buildChunk(cx-1,cz);
  if(x%CS===CS-1&&cx<NCX-1)buildChunk(cx+1,cz);
  if(z%CS===0&&cz>0)buildChunk(cx,cz-1);
  if(z%CS===CS-1&&cz<NCZ-1)buildChunk(cx,cz+1);
}
for(let cx=0;cx<NCX;cx++)for(let cz=0;cz<NCZ;cz++)buildChunk(cx,cz);

/* ============================ ĐỒ HỌA ============================ */
const renderer=new THREE.WebGLRenderer({antialias:false});
renderer.setPixelRatio(Math.min(window.devicePixelRatio||1,1.5));
document.body.insertBefore(renderer.domElement,document.body.firstChild);
const camera=new THREE.PerspectiveCamera(75,1,0.1,140);
scene.add(new THREE.AmbientLight(0xffffff,0.75));
const sun=new THREE.DirectionalLight(0xffffff,0.6);
sun.position.set(3,10,5);scene.add(sun);
function resize(){
  const w=window.innerWidth,h=window.innerHeight;
  if(!w||!h)return;
  renderer.setSize(w,h);camera.aspect=w/h;camera.updateProjectionMatrix();
}
window.addEventListener('resize',resize);resize();

// mây
const clouds=[];
const cloudMat=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.88});
for(let i=0;i<14;i++){
  const c=new THREE.Mesh(new THREE.BoxGeometry(6+R()*8,1.2,4+R()*5),cloudMat);
  c.position.set(-30+R()*(W+60),H+5+R()*3,-30+R()*(D+60));
  scene.add(c);clouds.push(c);
}

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
function part(w,h,d,m,y){
  const g=new THREE.BoxGeometry(w*U,h*U,d*U);g.translate(0,y*U,0);
  return new THREE.Mesh(g,m);
}
const body=part(8,12,4,mat(SHIRT),18);model.add(body);
const head=new THREE.Group();head.position.y=24*U;
head.add(part(8,8,8,[mat(SKIN),mat(SKIN),mat(HAIR),mat(SKIN),
  new THREE.MeshLambertMaterial({map:faceTex}),mat(HAIR)],4));
model.add(head);
function limb(x,y,top,topCol,botCol,topH){
  const g=new THREE.Group();g.position.set(x*U,y*U,0);
  g.add(part(4,topH,4,mat(topCol),-topH/2));
  g.add(part(4,12-topH,4,mat(botCol),-topH-(12-topH)/2));
  model.add(g);return g;
}
const armR=limb(-6,24,0,SHIRT,SKIN,4);
const armL=limb(6,24,0,SHIRT,SKIN,4);
const legR=limb(-2,12,0,PANTS,PANTS,12);
const legL=limb(2,12,0,PANTS,PANTS,12);
scene.add(model);

/* ============================ NGƯỜI CHƠI ============================ */
const SPAWN={x:W/2+.5,y:hm[(W/2)+W*(D/2)]+1.001,z:D/2+.5};
const P={x:SPAWN.x,y:SPAWN.y,z:SPAWN.z};
let vy=0,onGround=false,fly=false,yaw=0,pitch=-0.15,view=1,sel=1;
let walkPhase=0,amp=0,swing=0,breakHeld=false,breakT=0,jumpHeld=false,downHeld=false;
const keys={};const joy={x:0,y:0};

function solidAt(x,y,z){
  if(y<0)return true;
  if(x<0||x>=W||z<0||z>=D)return true;
  if(y>=H)return false;
  return world[I(x,y,z)]!==0;
}
function collides(){
  const r=0.3;
  const x0=Math.floor(P.x-r),x1=Math.floor(P.x+r),y0=Math.floor(P.y),y1=Math.floor(P.y+1.79),
        z0=Math.floor(P.z-r),z1=Math.floor(P.z+r);
  for(let y=y0;y<=y1;y++)for(let z=z0;z<=z1;z++)for(let x=x0;x<=x1;x++)
    if(solidAt(x,y,z))return true;
  return false;
}
function moveH(axis,d,moving){
  const o=P[axis];P[axis]=o+d;
  if(!collides())return;
  if(onGround&&!fly&&moving){
    P.y+=1.01;const ok=!collides();P.y-=1.01;
    if(ok){P[axis]=o;if(vy<=0){vy=8;onGround=false;}return;}
  }
  P[axis]=o;
}

/* ===== bắn tia (DDA) ===== */
function raycast(ox,oy,oz,dx,dy,dz,maxD){
  let x=Math.floor(ox),y=Math.floor(oy),z=Math.floor(oz);
  const sx=dx>0?1:-1,sy=dy>0?1:-1,sz=dz>0?1:-1;
  const tdx=dx!==0?Math.abs(1/dx):Infinity,tdy=dy!==0?Math.abs(1/dy):Infinity,tdz=dz!==0?Math.abs(1/dz):Infinity;
  let tmx=dx!==0?(dx>0?x+1-ox:ox-x)*tdx:Infinity;
  let tmy=dy!==0?(dy>0?y+1-oy:oy-y)*tdy:Infinity;
  let tmz=dz!==0?(dz>0?z+1-oz:oz-z)*tdz:Infinity;
  let px=null,py=0,pz=0;
  for(let i=0;i<80;i++){
    if(get(x,y,z))return{x:x,y:y,z:z,prev:px===null?null:[px,py,pz]};
    px=x;py=y;pz=z;
    if(tmx<tmy&&tmx<tmz){if(tmx>maxD)break;x+=sx;tmx+=tdx;}
    else if(tmy<tmz){if(tmy>maxD)break;y+=sy;tmy+=tdy;}
    else{if(tmz>maxD)break;z+=sz;tmz+=tdz;}
  }
  return null;
}
let target=null;
const hl=new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(1.01,1.01,1.01)),
  new THREE.LineBasicMaterial({color:0x000000}));
hl.visible=false;scene.add(hl);

function doBreak(){
  swing=1;
  if(!target||target.y===0)return;
  set(target.x,target.y,target.z,0);
  rebuildAround(target.x,target.z);
}
function overlapsPlayer(x,y,z){
  return x<P.x+.3&&x+1>P.x-.3&&y<P.y+1.8&&y+1>P.y&&z<P.z+.3&&z+1>P.z-.3;
}
function doPlace(){
  swing=1;
  if(!target||!target.prev)return;
  const x=target.prev[0],y=target.prev[1],z=target.prev[2];
  if(!inb(x,y,z)||get(x,y,z)||overlapsPlayer(x,y,z))return;
  set(x,y,z,sel);
  rebuildAround(x,z);
}

/* ============================ HOTBAR ============================ */
const url=atlas.toDataURL();
const slots=[];
for(let id=1;id<=8;id++){
  const t=BT[id][1],tc=t%COLS,tr=(t/COLS)|0;
  const d=document.createElement('div');d.className='slot';
  d.style.backgroundImage='url('+url+')';
  d.style.backgroundSize='800% 200%';
  d.style.backgroundPosition=(tc/(COLS-1)*100)+'% '+(tr/(ROWS-1)*100)+'%';
  d.addEventListener('pointerdown',e=>{e.stopPropagation();select(id);});
  $('hotbar').appendChild(d);slots.push(d);
}
function select(id){sel=((id-1+8)%8)+1;slots.forEach((s,i)=>s.classList.toggle('sel',i===sel-1));}
select(1);

/* ============================ ĐIỀU KHIỂN ============================ */
window.addEventListener('keydown',e=>{
  const k=e.key.toLowerCase();keys[k]=true;
  if(k===' '||k.startsWith('arrow'))e.preventDefault();
  if(k==='v')view=(view+1)%3;
  if(k==='f')toggleFly();
  if(k>='1'&&k<='8')select(+k);
});
window.addEventListener('keyup',e=>{keys[e.key.toLowerCase()]=false;});
window.addEventListener('wheel',e=>{select(sel+(e.deltaY>0?1:-1));},{passive:true});
window.addEventListener('blur',()=>{for(const k in keys)keys[k]=false;});
function toggleFly(){fly=!fly;vy=0;$('bDown').style.display=fly?'flex':'none';$('bFly').classList.toggle('on',fly);}

// nhìn xung quanh + thao tác chuột
const cv=renderer.domElement;
cv.addEventListener('contextmenu',e=>e.preventDefault());
const looks={};
cv.addEventListener('pointerdown',e=>{
  window.focus();
  if(e.pointerType==='mouse'&&e.button===2){doPlace();return;}
  looks[e.pointerId]={x:e.clientX,y:e.clientY,sx:e.clientX,sy:e.clientY,t:performance.now()};
  cv.setPointerCapture(e.pointerId);
});
cv.addEventListener('pointermove',e=>{
  const l=looks[e.pointerId];if(!l)return;
  yaw-=(e.clientX-l.x)*0.0055;
  pitch=Math.max(-1.5,Math.min(1.5,pitch-(e.clientY-l.y)*0.0055));
  l.x=e.clientX;l.y=e.clientY;
});
function endLook(e){
  const l=looks[e.pointerId];if(!l)return;
  const moved=Math.hypot(e.clientX-l.sx,e.clientY-l.sy);
  if(e.type==='pointerup'&&e.pointerType==='mouse'&&e.button===0&&moved<6&&performance.now()-l.t<350)doBreak();
  delete looks[e.pointerId];
}
cv.addEventListener('pointerup',endLook);
cv.addEventListener('pointercancel',endLook);

// cần điều khiển
let joyId=null;
const joyEl=$('joy'),knob=$('knob');
function joyMove(e){
  const r=joyEl.getBoundingClientRect();
  let dx=e.clientX-(r.left+r.width/2),dy=e.clientY-(r.top+r.height/2);
  const m=46,len=Math.hypot(dx,dy);
  if(len>m){dx*=m/len;dy*=m/len;}
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
  const up=()=>off&&off();
  el.addEventListener('pointerup',up);el.addEventListener('pointercancel',up);
}
hold('bJump',()=>{jumpHeld=true;},()=>{jumpHeld=false;});
hold('bDown',()=>{downHeld=true;},()=>{downHeld=false;});
hold('bBreak',()=>{breakHeld=true;breakT=0;},()=>{breakHeld=false;});
hold('bPlace',()=>doPlace());
hold('bView',()=>{view=(view+1)%3;});
hold('bFly',()=>toggleFly());

/* ============================ VÒNG LẶP ============================ */
let hudT=0,frames=0;
function update(dt){
  let ix=((keys.d||keys.arrowright)?1:0)-((keys.a||keys.arrowleft)?1:0)+joy.x;
  let iz=((keys.s||keys.arrowdown)?1:0)-((keys.w||keys.arrowup)?1:0)+joy.y;
  let len=Math.hypot(ix,iz);
  if(len>1){ix/=len;iz/=len;len=1;}
  const fwd=-iz,rgt=ix;
  const sy=Math.sin(yaw),cy=Math.cos(yaw);
  const dirx=rgt*cy+fwd*(-sy),dirz=rgt*(-sy)+fwd*(-cy);
  const sprint=keys.shift&&!fly?1.35:1;
  const speed=(fly?9:4.3)*sprint;
  const moving=len>0.1;

  if(fly){
    vy=(jumpHeld||keys[' ']?6.5:0)+(downHeld||keys.shift?-6.5:0);
  }else{
    vy=Math.max(-40,vy-25*dt);
    if((jumpHeld||keys[' '])&&onGround){vy=8;onGround=false;}
  }
  moveH('x',dirx*speed*dt,moving);
  moveH('z',dirz*speed*dt,moving);
  const oy=P.y;P.y+=vy*dt;
  if(collides()){
    if(vy<0){P.y=Math.floor(P.y)+1.0001;onGround=true;}else P.y=oy;
    vy=0;
  }else onGround=false;
  if(P.y<-20){P.x=SPAWN.x;P.y=SPAWN.y+3;P.z=SPAWN.z;vy=0;}

  if(breakHeld){breakT-=dt;if(breakT<=0){doBreak();breakT=0.25;}}

  // hoạt ảnh
  const walking=moving&&(onGround||fly);
  amp+=((walking?1:0)-amp)*Math.min(1,dt*10);
  walkPhase+=dt*speed*2.1*(walking?1:0);
  const sw=Math.sin(walkPhase)*0.9*amp;
  legR.rotation.x=sw;legL.rotation.x=-sw;
  armL.rotation.x=sw;
  swing=Math.max(0,swing-dt*3.2);
  armR.rotation.x=-sw-Math.sin(swing*Math.PI)*1.7;
  head.rotation.x=-pitch*0.8;
  model.position.set(P.x,P.y,P.z);
  model.rotation.y=yaw+Math.PI;

  // camera
  const ex=P.x,ey=P.y+1.62,ez=P.z;
  const cp=Math.cos(pitch);
  const dx=-Math.sin(yaw)*cp,dy=Math.sin(pitch),dz=-Math.cos(yaw)*cp;
  let ox=ex,oy2=ey,oz=ez,reach=5.5;
  if(view===0){
    model.visible=false;
    camera.position.set(ex,ey,ez);camera.rotation.set(pitch,yaw,0,'YXZ');
  }else{
    model.visible=true;
    const sgn=view===1?-1:1;
    let d=0.3;
    for(;d<=4;d+=0.15){
      if(solidAt(Math.floor(ex+dx*sgn*d),Math.floor(ey+dy*sgn*d),Math.floor(ez+dz*sgn*d)))break;
    }
    const dist=Math.max(0.4,d-0.3);
    camera.position.set(ex+dx*sgn*dist,ey+dy*sgn*dist,ez+dz*sgn*dist);
    if(view===1){
      camera.rotation.set(pitch,yaw,0,'YXZ');
      ox=camera.position.x;oy2=camera.position.y;oz=camera.position.z;reach=dist+5.5;
    }else{
      camera.rotation.set(-pitch,yaw+Math.PI,0,'YXZ');
    }
  }
  target=raycast(ox,oy2,oz,dx,dy,dz,reach);
  if(target){hl.visible=true;hl.position.set(target.x+.5,target.y+.5,target.z+.5);}
  else hl.visible=false;

  for(const c of clouds){c.position.x+=dt*0.9;if(c.position.x>W+35)c.position.x=-35;}

  hudT-=dt;
  if(hudT<=0){
    hudT=0.3;
    $('hud').textContent='X '+P.x.toFixed(1)+'  Y '+P.y.toFixed(1)+'  Z '+P.z.toFixed(1)+(fly?'  · đang bay':'');
  }
}
let last=performance.now();
function frame(now){
  const dt=Math.min(0.05,(now-last)/1000);last=now;
  update(dt);
  renderer.render(scene,camera);
  frames++;
  if(frames===2){
    $('msg').innerHTML='🧱 Kéo màn hình để nhìn · cần trái để đi<br>⛏ đào · 🧱 đặt khối · chạm ô trên cùng để đổi khối';
    $('cross').style.display='block';
    setTimeout(()=>{$('msg').style.display='none';},7000);
  }
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);
})();
</script>
</body>
</html>
"""

components.html(HTML, height=720, scrolling=False)
