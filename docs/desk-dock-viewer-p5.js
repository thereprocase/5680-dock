import * as THREE from 'three';
import {SoftwareRenderer} from './desk-dock-software.js';
import {OrbitControls} from './vendor/OrbitControls.js';
if(new URLSearchParams(location.search).has('embed'))document.body.classList.add('embedded');
const $=id=>document.getElementById(id);let canvas=$('scene');
const scene=new THREE.Scene();scene.background=new THREE.Color('#182a31');
let renderer;try{renderer=new THREE.WebGLRenderer({canvas,antialias:true});}catch{const replacement=canvas.cloneNode();canvas.replaceWith(replacement);canvas=replacement;renderer=new SoftwareRenderer({canvas});}
const camera=new THREE.PerspectiveCamera(36,1,1,4000);camera.up.set(0,0,1);
const controls=new OrbitControls(camera,canvas);controls.enableDamping=true;
scene.add(new THREE.HemisphereLight(0xeaf8ff,0x344247,2.5));
for(const [p,i] of [[[200,400,700],3],[[-400,-200,300],2]]){const l=new THREE.DirectionalLight(0xffffff,i);l.position.set(...p);scene.add(l);}
const meshes=[],air=new THREE.Group();scene.add(air);air.visible=false;
let manifest=null,playing=false,start=0,selected=null;
const TOGGLE={laptop:['laptop'],fans:['fan'],pegs:['peg','lock'],fasteners:['pin','key'],guards:['guard'],ties:['tie'],centre:['centre']};
const pretty=n=>n.replace('Precision_5680_REFERENCE','Laptop (reference)').replace(/fan_120mm_M(\d)/,'120 mm fan, module $1 (purchased)').replaceAll('-',' ');
function stop(){playing=false;$('play').textContent='▶ Play docking motion';$('play').setAttribute('aria-pressed','false');}
function update(){if(!manifest)return;const e=+$('explode').value/100,t=+$('motion').value/100;
$('explodeValue').textContent=Math.round(e*100)+'%';const lift=Math.max(0,(t-.2)/.8)*145,x=manifest.undocked_x_offset_mm*Math.min(1,t/.2),up=manifest.laptop_up;
$('motionValue').textContent=t===0?'Seated':lift>0?Math.round(lift)+' mm lift':x.toFixed(1)+' mm slide';
$('state').textContent=e>0?'Exploded: parts move along their assembly directions':lift>0?'Lift / lower onto the seat pegs':t>0?'Slide clear of the plug end':'Docked · lid toward you · 8° lean';
for(const m of meshes){const p=m.userData;const isLaptop=p.group==='laptop';
if(isLaptop&&!e)m.position.set(x,up[1]*lift,up[2]*lift);else m.position.set(p.explode[0]*e,p.explode[1]*e,p.explode[2]*e);
let vis=true;for(const [id,groups] of Object.entries(TOGGLE))if(groups.includes(p.group)&&!$(id).checked)vis=false;m.visible=vis;}
air.visible=$('air').checked&&e===0;}
function view(name){const views={home:[[-330,-640,520],[177,30,115]],lid:[[177,900,260],[177,40,130]],under:[[177,-760,300],[177,0,100]],plug:[[-330,-160,210],[50,20,90]],exploded:[[-420,-760,640],[177,20,120]]};
if(name==='exploded'){$('explode').value=100;$('motion').value=0;update();}const [pos,tgt]=views[name]||views.home;camera.position.set(...pos);controls.target.set(...tgt);controls.update();
document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===name)));}
function select(m){if(selected)selected.material.emissive.setHex(0);selected=m;if(m){m.material.emissive.setHex(0x235549);$('part').value=m.userData.name;$('detail').textContent=pretty(m.userData.name)+(m.userData.note?': '+m.userData.note:'')+(m.userData.reference?' Reference body, not printed.':'');}else{$('part').value='';$('detail').textContent='Select a part in the model or the list to see what it does.';}}
try{
const [man,buffer]=await Promise.all([fetch('models/desk-dock-p5/model.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(r.status);return r.json();}),fetch('models/desk-dock-p5/model.bin',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(r.status);return r.arrayBuffer();})]);
manifest=man;
for(const p of man.parts){const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(buffer,p.positionOffset,p.vertexCount*3),3));g.setIndex(new THREE.BufferAttribute(new Uint32Array(buffer,p.indexOffset,p.indexCount),1));g.computeVertexNormals();
const mat=new THREE.MeshStandardMaterial({color:new THREE.Color(p.color[0]/255,p.color[1]/255,p.color[2]/255),roughness:.72,metalness:.05,transparent:p.reference,opacity:p.reference?(p.group==='laptop'?.28:.85):1});
const m=new THREE.Mesh(g,mat);m.userData=p;scene.add(m);meshes.push(m);const o=document.createElement('option');o.value=p.name;o.textContent=pretty(p.name);$('part').append(o);}
// Arrows show the intended extraction direction only; they are not a CFD result.
const ex=man.exhaust_axis;for(const x of man.fan_centers_x){air.add(new THREE.ArrowHelper(new THREE.Vector3(ex[0],ex[1],ex[2]),new THREE.Vector3(x,150,150),90,0x79decd,22,11));air.add(new THREE.ArrowHelper(new THREE.Vector3(0,0,-1),new THREE.Vector3(x,0,62),40,0x79decd,14,7));}
$('loading').hidden=true;window.deskDockReady=true;update();view(new URLSearchParams(location.search).get('view')||'home');
}catch(e){$('loading').textContent='Could not load the P5 CAD model.';console.error(e);}
for(const id of ['explode','motion'])$(id).addEventListener('input',()=>{stop();$(id==='explode'?'motion':'explode').value=0;update();});
for(const id of [...Object.keys(TOGGLE),'air'])$(id).addEventListener('change',update);
document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>view(b.dataset.view));
$('part').onchange=()=>select(meshes.find(m=>m.userData.name===$('part').value));
$('reset').onclick=()=>{stop();$('explode').value=$('motion').value=0;for(const id of Object.keys(TOGGLE))$(id).checked=true;$('air').checked=false;select(null);update();view('home');};
$('play').onclick=()=>{if(playing){stop();return;}playing=true;start=performance.now();$('explode').value=0;$('laptop').checked=true;$('play').textContent='Ⅱ Pause';$('play').setAttribute('aria-pressed','true');};
let down;canvas.addEventListener('pointerdown',e=>down=[e.clientX,e.clientY]);canvas.addEventListener('pointerup',e=>{if(!down||Math.hypot(e.clientX-down[0],e.clientY-down[1])>4)return;const r=canvas.getBoundingClientRect();const ray=new THREE.Raycaster();ray.setFromCamera(new THREE.Vector2(((e.clientX-r.left)/r.width)*2-1,-((e.clientY-r.top)/r.height)*2+1),camera);const hit=ray.intersectObjects(meshes.filter(m=>m.visible))[0];select(hit?hit.object:null);});
new ResizeObserver(()=>{const r=canvas.parentElement.getBoundingClientRect();renderer.setSize(r.width,r.height,false);camera.aspect=r.width/r.height;camera.updateProjectionMatrix();}).observe(canvas.parentElement);
function frame(now){requestAnimationFrame(frame);if(playing){const q=((now-start)/1000)%10;const t=q<4?q/4:q<5?1:q<9?1-(q-5)/4:0;$('motion').value=t*100;update();}controls.update();renderer.render(scene,camera);}
frame(0);
window.deskDockState=()=>({parts:meshes.length,visible:meshes.filter(m=>m.visible).length,explosion:+$('explode').value,motion:+$('motion').value,playing});
