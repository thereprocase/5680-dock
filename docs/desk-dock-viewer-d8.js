import * as THREE from 'three';
import {SoftwareRenderer} from './desk-dock-software.js';
import {OrbitControls} from './vendor/OrbitControls.js';

const $=id=>document.getElementById(id);
if(new URLSearchParams(location.search).has('embed'))document.body.classList.add('embedded');
const LEAN=5*Math.PI/180, FAN_ANGLE=18*Math.PI/180;
let canvas=$('scene');
const scene=new THREE.Scene();scene.background=new THREE.Color('#182a31');
let renderer;
try{renderer=new THREE.WebGLRenderer({canvas,antialias:true});}
catch{
  const replacement=canvas.cloneNode();canvas.replaceWith(replacement);canvas=replacement;
  renderer=new SoftwareRenderer(canvas);$('air').disabled=true;
  $('air').parentElement.title='Airflow arrows need WebGL. Air enters below the laptop and exits the fans 18° upward.';
}
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
const camera=new THREE.PerspectiveCamera(36,1,1,4000);camera.up.set(0,0,1);
const controls=new OrbitControls(camera,canvas);controls.enableDamping=true;
scene.add(new THREE.HemisphereLight(0xeaf8ff,0x344247,2.5));
for(const [position,intensity] of [[[200,400,700],3],[[-400,-200,300],2]]){
  const light=new THREE.DirectionalLight(0xffffff,intensity);light.position.set(...position);scene.add(light);
}
const meshes=[],air=new THREE.Group();scene.add(air);air.visible=false;
const moving=n=>n==='Precision_5680_REFERENCE'||n.startsWith('RUBBER_FOOT_');
const guard=n=>/fan_guard_retainer|fan_top_clip|outlet_guard|fan_thumb_lock|fan_M3_screw_envelope/.test(n);
const fan=n=>/fan_frame|fan_hub|blade/.test(n);
const cap=n=>/removable_plug_cap|cassette_cap|plug_cap/.test(n);
const handControl=n=>/thumb|knob|handwheel|hand_|push_pin|pivot_pin|printed_chassis_stop|_lock_/.test(n);
const nearFar=n=>n.startsWith('01_')?'far end':n.startsWith('02_')?'loading end':'';
function pretty(n){
  const end=nearFar(n),suffix=end?' · '+end:'';
  if(moving(n))return n.startsWith('RUBBER_FOOT_')?'Laptop rubber foot':'Precision 5680 laptop';
  if(n.includes('manifold'))return 'Shell with integral feet'+suffix;
  if(n==='connector_module_body')return 'Removable connector module';
  if(n==='cassette_Z_saddle')return 'Vertical plug slide';
  if(n.startsWith('cassette_Z_lock'))return 'Vertical slide hand lock';
  if(n.startsWith('cassette_Y_lock'))return 'Lateral slide hand lock';
  if(n.startsWith('connector_mount_lock'))return 'Module mounting hand lock';
  if(n.includes('fan_top_clip'))return 'Replaceable fan clip'+suffix;
  if(n.includes('_desk_pad_'))return 'Shell foot grip pad'+suffix;
  if(n.includes('fan_guard_retainer'))return 'Removable fan guard'+suffix;
  if(n.includes('fan_thumb_lock'))return 'Fan guard hand lock'+suffix;
  if(n.includes('fan_M3_screw_envelope'))return 'Fan guard M3 screw'+suffix;
  if(n.includes('fan_captive_nut'))return 'Retained fan nut'+suffix;
  if(n.includes('bottom_panel'))return 'Ribbed bottom cover'+suffix;
  if(n.includes('bottom_thumb_lock'))return 'Duct floor hand lock'+suffix;
  if(n.includes('bridge_thumb_lock'))return 'Body joining hand lock'+suffix;
  if(n.includes('bridge_key'))return 'Body joining key';
  if(n.includes('plug_cap_quarter_turn_keeper'))return 'Plug cap quarter-turn keeper';
  if(n.includes('cap_push_pin'))return 'Plug cap push pin';
  if(cap(n))return 'Lift-off plug cap';
  if(n==='breakaway_spring_cartridge')return 'Replaceable breakaway spring';
  if(n==='breakaway_carrier')return 'Folding plug carrier';
  if(n==='breakaway_preload_hand_nut')return 'Breakaway preload adjuster';
  if(n==='breakaway_pivot_pin_10mm')return 'Printed hinge axle';
  if(n.includes('cassette_thumb_knob'))return 'Cassette hand lock';
  if(n.includes('stop_thumb_knob'))return 'Chassis stop hand control';
  if(n.includes('X_depth_overmold_clamp'))return 'Lateral plug slide and clamp';
  if(n.includes('fan_frame'))return '120 × 120 × 25 mm fan'+suffix;
  if(n.includes('fan_hub'))return 'Fan hub'+suffix;
  if(n.includes('blade'))return 'Fan blade'+suffix;
  if(n.includes('lid_bearing'))return 'Soft lid contact';
  if(n.includes('corner_pad'))return 'Soft end seat';
  if(n.includes('hinge_seal'))return 'Exhaust seal';
  if(n.includes('foot_'))return 'Desk grip pad'+suffix;
  return n.replace(/^\d+_/,'').replace(/_REFERENCE/g,'').replaceAll('_',' ').replace(/\b\w/,s=>s.toUpperCase());
}
function partColor(p){
  const n=p.name;
  if(n.includes('manifold'))return [136,149,152];
  if(n==='connector_module_body')return [78,129,152];
  if(n==='cassette_Z_saddle')return [139,166,126];
  if(n.includes('bottom_panel'))return [86,142,159];
  if(n.includes('fan_top_clip'))return [119,155,128];
  if(n==='breakaway_spring_cartridge')return [154,157,116];
  if(handControl(n))return [102,143,132];
  if(p.reference||fan(n))return p.color;
  if(/liner|corner_pad|seal|soft_tip/.test(n))return [106,120,111];
  if(n.includes('foot_')||n.includes('_desk_pad_'))return [34,40,41];
  if(/nut|washer|metal/.test(n))return p.color;
  return [61,69,72];
}
let playing=false,start=0,selected=null,viewMode='home',folded=false;
let foldAngle=0,foldMotion=null,hinge=null,moduleService=null;
let moduleParts=new Set(),moduleLocks=new Set();
const hingeAxis=new THREE.Vector3(),hingePivot=new THREE.Vector3(),rotation=new THREE.Quaternion(),pivotRotated=new THREE.Vector3();
function camLift(angle){return hinge?Math.min(hinge.rise,Math.sqrt(hinge.preload**2+2*hinge.torque*Math.abs(angle*Math.PI/180)/hinge.springRate)-hinge.preload):0;}
function stopFold(){foldMotion=null;}
function poseHolder(mesh){
  const p=mesh.userData;
  mesh.quaternion.identity();
  if(!hinge){mesh.geometry=folded&&p.foldedGeometry?p.foldedGeometry:p.readyGeometry;return;}
  mesh.geometry=p.readyGeometry;
  const lift=camLift(foldAngle);
  if(p.motion==='rotate'){
    rotation.setFromAxisAngle(hingeAxis,foldAngle*Math.PI/180);mesh.quaternion.copy(rotation);
    pivotRotated.copy(hingePivot).applyQuaternion(rotation);
    mesh.position.add(hingePivot).sub(pivotRotated).addScaledVector(hingeAxis,-lift);
  }else if(p.motion==='axial')mesh.position.addScaledVector(hingeAxis,-lift);
  else if(p.motion==='spring'&&p.lastLift!==lift){
    const position=mesh.geometry.attributes.position,source=p.springReady,w=p.springWeights;
    for(let i=0;i<w.length;i++){
      position.array[i*3]=source[i*3]-hingeAxis.x*lift*w[i];
      position.array[i*3+1]=source[i*3+1]-hingeAxis.y*lift*w[i];
      position.array[i*3+2]=source[i*3+2]-hingeAxis.z*lift*w[i];
    }
    position.needsUpdate=true;mesh.geometry.computeVertexNormals();mesh.geometry.computeBoundingSphere();p.lastLift=lift;
  }
}
const hints={
  home:'Shell perimeter feet carry the laptop. Ribbed covers close the underside, and the connector removes as a complete module.',
  service:'The grilles and replaceable top clips are hidden. The fan frames remain seated in their pockets.',
  module:'Unload the laptop and remove the two mounting locks. Pull the module 4.3 mm in local −Y to clear the keys, then withdraw it outboard along −X.',
  exploded:'Inspect the guards, fans, duct floors and joining keys. These offsets show the parts, not a tested assembly sequence.',
  under:'The continuous low lip supports alignment along the underside edge. It stays below the rubber feet and leaves the intake open.',
  plug:'The cap is hidden. Slide the plug in Y (±3 mm) and Z (−4 to +5 mm), lock both stages, then set the independent X chassis stop.'
};
function stop(){playing=false;$('play').textContent='Play docking motion';$('play').setAttribute('aria-pressed','false');}
function offset(p){
  const n=p.name,s=p.center[0]>177?1:-1;
  if(moving(n))return [18,Math.sin(LEAN)*145,Math.cos(LEAN)*145];
  if(n.includes('manifold'))return [s*54,0,0];
  if(n.includes('bridge_key'))return [0,0,55];
  if(n.includes('bridge_thumb_lock'))return [0,0,80];
  if(n.includes('bridge_captive_nut'))return [s*54,0,12];
  if(n.includes('bottom_panel'))return [s*54,0,-60];
  if(n.includes('bottom_thumb_lock'))return [s*54,0,-85];
  if(n.includes('bottom_captive_nut'))return [s*54,0,-16];
  if(n.includes('foot_')||n.includes('_desk_pad_'))return [s*54,0,-85];
  if(guard(n))return [s*54,135,45];
  if(n.includes('fan_captive_nut'))return [s*54,40,-5];
  if(fan(n))return [s*54,70,23];
  if(n.includes('quarter_turn_keeper'))return [-54,0,60];
  if(cap(n))return [-78,0,8];
  if(n.includes('lid_bearing'))return [s*54,-28,0];
  if(/seal|corner_pad/.test(n))return [s*54,0,35];
  return [-65,0,30];
}
function update(){
  const e=+$('explode').value/100,t=+$('motion').value/100,service=+$('moduleMotion').value/100;
  const keyTravel=(moduleService?.keyReleaseMm??4.3)*Math.min(1,service/.2);
  const outboard=(moduleService?.outboardTravelMm??70)*Math.max(0,(service-.2)/.8);
  $('moduleValue').textContent=service===0?'Seated':outboard>0?outboard.toFixed(1)+' mm outboard':keyTravel.toFixed(1)+' mm key release';
  const lift=Math.max(0,(t-.2)/.8)*135,x=18*Math.min(1,t/.2);
  $('explodeValue').textContent=Math.round(e*100)+'%';
  $('motionValue').textContent=t===0?'Seated':lift>0?Math.round(lift)+' mm lift':x.toFixed(1)+' mm slide';
  const serviceLabel=!$('guards').checked?($('fans').checked?'Guards removed · fans seated in pockets':'Fans removed · pockets exposed'):'Fans enclosed in the plenum pockets';
  $('state').textContent=e>0?'Exploded assembly':lift>0?'Lift / lower onto the end seats':t>0?'Slide clear of the far-side plug':viewMode==='service'?serviceLabel:viewMode==='plug'&&!$('cover').checked?'Plug cap removed':'Docked · lid toward you';
  if(viewMode==='service')$('viewHint').textContent=$('guards').checked?'Remove the two top clips, then lift the grille from its open-top rails. Hide the grilles and clips to inspect the fan seating.':$('fans').checked?hints.service:'Fans and grilles are hidden. The open-top pockets and guide rails are exposed.';
  if(viewMode==='plug')$('viewHint').textContent=$('cover').checked?'The cap captures the original plug. Hide it to inspect the cassette and independent chassis stop.':hints.plug;
  for(const mesh of meshes){
    const p=mesh.userData;mesh.position.set(...p.explode).multiplyScalar(e);poseHolder(mesh);
    if(moduleParts.has(p.name)&&service>0)mesh.position.add(new THREE.Vector3(-outboard,-Math.cos(LEAN)*keyTravel,Math.sin(LEAN)*keyTravel));
    if(moving(p.name)&&!e)mesh.position.set(x,Math.sin(LEAN)*lift,Math.cos(LEAN)*lift);
    mesh.visible=(!moving(p.name)||$('laptop').checked)&&(!cap(p.name)||$('cover').checked)&&(!guard(p.name)||$('guards').checked)&&(!fan(p.name)||$('fans').checked)&&(!moduleLocks.has(p.name)||service===0);
  }
  air.visible=$('air').checked&&e===0&&service===0;
  folded=foldAngle>=44.999;
  $('laptop').disabled=foldAngle>0||!!foldMotion||service>0;
  $('laptop').parentElement.title=$('laptop').disabled?'Return the holder and connector module to their seated positions before showing the laptop.':'';
  $('fold').textContent=foldMotion?'Pause holder motion':foldAngle>0?'Click back to ready':'Fold away';$('fold').setAttribute('aria-pressed',String(foldAngle>0));
  $('foldAngle').value=foldAngle;$('foldValue').textContent=foldAngle.toFixed(1)+'°';
  if(service>0){$('state').textContent=outboard>0?'Module withdrawn · '+outboard.toFixed(1)+' mm':'Module keys releasing';$('viewHint').textContent=hints.module+' The viewer interpolates between finite checked CAD poses.';}
  if(foldAngle>0||foldMotion){$('state').textContent=folded?'Cassette folded clear':'Holder retreat · '+foldAngle.toFixed(1)+'°';$('viewHint').textContent='The holder pivots while the cam compresses the spring. This is a slow motion demonstration; release force and cable flex need a prototype test.';}
}
function pointCamera(name,includeMotion=false){
  const stageRect=canvas.parentElement.getBoundingClientRect();
  camera.aspect=stageRect.width/stageRect.height;camera.updateProjectionMatrix();
  const views={
    home:[[-300,800,470],[170,35,145]],
    service:[[177,535,155],[177,49,76]],
    exploded:[[-410,950,480],[170,55,130]],
    under:[[100,-880,370],[177,0,140]],
    plug:[[-250,-220,225],[-26,15,130]],
    module:[[-380,-275,245],[-65,25,115]]
  };
  const [position,target]=views[name];camera.position.set(...position);controls.target.set(...target);
  if(!['plug','module'].includes(name)&&meshes.length){
    scene.updateMatrixWorld(true);
    const bounds=new THREE.Box3();
    for(const mesh of meshes)if(mesh.visible){
      bounds.expandByObject(mesh);
      if(includeMotion&&moving(mesh.userData.name)){
        mesh.geometry.computeBoundingBox();
        bounds.union(mesh.geometry.boundingBox.clone().translate(new THREE.Vector3(18,Math.sin(LEAN)*135,Math.cos(LEAN)*135)));
      }
    }
    const center=bounds.getCenter(new THREE.Vector3()),forward=new THREE.Vector3(...target).sub(new THREE.Vector3(...position)).normalize();
    const right=new THREE.Vector3().crossVectors(forward,camera.up).normalize(),up=new THREE.Vector3().crossVectors(right,forward).normalize();
    const vertical=Math.tan(camera.fov*Math.PI/360),horizontal=vertical*camera.aspect;
    let distance=100;
    for(const x of [bounds.min.x,bounds.max.x])for(const y of [bounds.min.y,bounds.max.y])for(const z of [bounds.min.z,bounds.max.z]){
      const rel=new THREE.Vector3(x,y,z).sub(center),depth=rel.dot(forward);
      distance=Math.max(distance,1.2*Math.abs(rel.dot(right))/horizontal-depth,1.2*Math.abs(rel.dot(up))/vertical-depth);
    }
    controls.target.copy(center);camera.position.copy(center).addScaledVector(forward,-distance);
  }
  controls.update();
}
function setView(name){
  stop();stopFold();folded=false;foldAngle=0;viewMode=name;$('explode').value=name==='exploded'?65:0;$('motion').value=0;$('moduleMotion').value=0;
  for(const id of ['laptop','cover','fans','guards'])$(id).checked=true;
  $('air').checked=false;
  if(name==='service'){$('guards').checked=false;$('laptop').checked=false;}
  if(name==='module')$('laptop').checked=false;
  if(name==='exploded')$('laptop').checked=false;
  if(name==='plug')$('cover').checked=false;
  $('viewHint').textContent=hints[name];
  document.querySelectorAll('[data-view]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.view===name)));
  update();pointCamera(name);
}
function describe(n){
  if(moving(n))return 'Laptop reference. Both Thunderbolt ports are on the keyboard-left edge, at the far plug end. The rubber feet remain outside the intended bearing contacts.';
  if(n.includes('manifold'))return 'Four integral perimeter feet per half carry the laptop through the shell to separate desk pads. The ribs and local bosses support thin removable covers. Fan pockets preserve the underside intake.';
  if(n==='connector_module_body')return 'The complete connector, printed breakaway hinge, live Y/Z slides and independent X stop remove together. Unload the laptop, remove two mounting locks, pull local −Y by 4.3 mm, then withdraw outboard along −X.';
  if(n==='cassette_Z_saddle'||n.startsWith('cassette_Z_lock'))return 'Live vertical adjustment from −4 to +5 mm. Two accessible printed hand locks secure the same saddle at the selected height; no replacement shims.';
  if(n.startsWith('cassette_Y_lock')||n==='X_depth_overmold_clamp')return 'Live lateral adjustment of ±3 mm. The underside hand lock clamps the plug cradle; positive shoulders carry docking thrust. Plug X stays fixed while the separate chassis stop sets engagement.';
  if(n.startsWith('connector_mount_lock'))return 'Two printed hand locks clamp the complete connector module to its keyed shell interface. Remove these before using the module-service motion.';
  if(n.includes('fan_top_clip'))return 'Separate replaceable top clip with an in-plane printed leaf. It retains the fan and grille; pad thickness remains configurable for the actual fan frame. Fit and fatigue require a physical check.';
  if(n.includes('fan_guard_retainer'))return 'Flat 4 mm grille with 1.6 mm bars, printed on its broad face. Remove the two top clips and lift it from the open-top rails to service the fan. No perimeter gasket is required by this design.';
  if(n.includes('fan_thumb_lock'))return 'Turn by hand to release the fan guard. Retention, reach and clamp force need prototype checks.';
  if(n.includes('fan_captive_nut'))return 'An enclosed side-entry trap keeps the nut from falling rearward when the guard screw is removed. Its loading porch is accessible through the open duct floor.';
  if(n.includes('bottom_panel'))return 'A 2 mm skin, perimeter rib and shallow cross ribs close the duct. Both covers total about 94 g of PETG, 48% below D7. Dedicated shell feet carry gravity directly, allowing these covers to stay light.';
  if(n.includes('bridge_key'))return 'Hand-fastened bridge on the low central deck joins the two plenum halves. Check hand access and retention before loading the stand.';
  if(fan(n))return '120 x 120 x 25 mm fan reference. The suction face stays in place while the thicker frame grows outward. Discharge remains 18 degrees above the desk. Check the actual fan and lead exit before printing.';
  if(n.includes('plug_cap_quarter_turn_keeper'))return 'Rotate 90° to align the keyway, then lift the keeper and slide the cap toward the cable. It is retained while locked and removable while unlocked.';
  if(cap(n))return 'Pull the large printed pin toward the open side, then lift the cap. Its grip on the actual cable overmold needs a physical fit and pull test.';
  if(n.includes('breakaway'))return 'Resettable printed hinge for a misaligned docking strike. Firm seating at 20 N and a 50 N-class release are calibration targets. Return the cassette by hand to reset; keep its cable loop loose.';
  if(n.includes('stop'))return 'Independent chassis stop limits insertion travel so the connector does not carry the seating load. Set it after aligning the plug.';
  if(/cassette|overmold_clamp/.test(n))return 'Plug capture and calibration assembly. Adjust live Y/Z slides before setting the independent X chassis stop.';
  if(n.includes('lid_bearing'))return 'Replaceable soft contact between the lid and the plenum. The shell carries the lean load.';
  if(/corner_pad/.test(n))return 'Soft profiled end seat carries the laptop case at its bare end margin.';
  if(n.includes('seal'))return 'Compliant exhaust seal. It seals airflow; the end seats carry the laptop weight.';
  if(n.includes('foot_')||n.includes('_desk_pad_'))return 'Soft pad directly below an integral shell foot. Test sliding and tip stability with the actual laptop and cable loads.';
  if(handControl(n))return 'Hand-operated fastener for assembly or calibration. Physical access and retention require prototype checks.';
  return 'D8 assembly component. See the design guide for assembly, fit and print-planning limits.';
}
function select(mesh){
  if(selected)selected.material.emissive.setHex(0);selected=mesh;
  if(mesh){mesh.material.emissive.setHex(0x235549);$('part').value=mesh.userData.name;$('detail').textContent=pretty(mesh.userData.name)+'. '+describe(mesh.userData.name);}
  else{$('part').value='';$('detail').textContent='Select a part in the model or the list to see what it does.';}
}
try{
  const [manifest,buffer]=await Promise.all([
    fetch('models/desk-dock-d8/model.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(r.status);return r.json();}),
    fetch('models/desk-dock-d8/model.bin',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error(r.status);return r.arrayBuffer();})
  ]);
  hinge=manifest.breakawayAnimation;moduleService=manifest.moduleService;
  moduleParts=new Set(moduleService?.movingParts??[]);moduleLocks=new Set(moduleService?.removedLocks??[]);
  if(hinge){hingeAxis.fromArray(hinge.axis);hingePivot.fromArray(hinge.pivot);}
  for(const p of manifest.parts){
    const makeGeometry=q=>{const g=new THREE.BufferGeometry();g.setAttribute('position',new THREE.BufferAttribute(new Float32Array(buffer,q.positionOffset,q.vertexCount*3),3));g.setIndex(new THREE.BufferAttribute(new Uint32Array(buffer,q.indexOffset,q.indexCount),1));g.computeVertexNormals();return g;};
    const geometry=makeGeometry(p),foldedGeometry=p.folded?makeGeometry(p.folded):null;
    const material=new THREE.MeshStandardMaterial({color:new THREE.Color(...partColor(p).map(v=>v/255)).convertSRGBToLinear(),roughness:.76,metalness:p.reference ? .2 : .04,flatShading:true});
    const mesh=new THREE.Mesh(geometry,material);mesh.userData={...p,explode:offset(p),readyGeometry:geometry,foldedGeometry};
    if(p.motion==='spring'){mesh.userData.springReady=geometry.attributes.position.array.slice();mesh.userData.springWeights=new Float32Array(buffer,p.springWeightOffset,p.vertexCount);}
    scene.add(mesh);meshes.push(mesh);
    const option=document.createElement('option');option.value=p.name;option.textContent=pretty(p.name);$('part').append(option);
  }
  // Direction arrows only: no CFD or measured-flow claim.
  for(const x of [84,269.68]){
    air.add(new THREE.ArrowHelper(new THREE.Vector3(0,Math.cos(FAN_ANGLE),Math.sin(FAN_ANGLE)),new THREE.Vector3(x,76,76),75,0x79decd,12,7));
    air.add(new THREE.ArrowHelper(new THREE.Vector3(0,1,0),new THREE.Vector3(x,-82,128),55,0x80c8ff,10,6));
    air.add(new THREE.ArrowHelper(new THREE.Vector3(0,0,-1),new THREE.Vector3(x,0,72),32,0xf3b76d,8,5));
  }
  $('loading').hidden=true;window.deskDockReady=true;setView('home');
}catch(error){$('loading').textContent='The D8 CAD could not be loaded. Use the local viewer launcher and reload.';console.error(error);}
for(const id of ['explode','motion'])$(id).addEventListener('input',()=>{
  stop();stopFold();foldAngle=0;folded=false;$('moduleMotion').value=0;
  $(id==='explode'?'motion':'explode').value=0;
  viewMode=id==='explode'&&+$(id).value>0?'exploded':'home';
  $('viewHint').textContent=hints[viewMode];
  if(id==='motion')$('laptop').checked=true;
  update();
});
$('moduleMotion').oninput=()=>{
  stop();stopFold();foldAngle=0;folded=false;viewMode='module';
  $('explode').value=0;$('motion').value=0;$('laptop').checked=false;
  $('viewHint').textContent=hints.module;
  document.querySelectorAll('[data-view]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.view==='module')));
  update();
};
for(const id of ['laptop','cover','fans','guards','air'])$(id).addEventListener('change',update);
document.querySelectorAll('[data-view]').forEach(button=>button.onclick=()=>setView(button.dataset.view));
$('part').onchange=()=>select(meshes.find(mesh=>mesh.userData.name===$('part').value));
function holderView(){
  stop();viewMode='plug';$('moduleMotion').value=0;
  $('laptop').checked=false;$('explode').value=0;$('motion').value=0;
}
$('fold').onclick=()=>{
  if(foldMotion){stopFold();update();return;}
  holderView();
  const target=foldAngle>0?0:45;
  if(matchMedia('(prefers-reduced-motion: reduce)').matches||!hinge){foldAngle=target;update();}
  else{foldMotion={from:foldAngle,to:target,start:performance.now(),duration:target===0?1800:1400};update();}
};
$('foldAngle').oninput=()=>{const angle=+$('foldAngle').value;stopFold();holderView();foldAngle=angle;update();};
$('reset').onclick=()=>{select(null);setView('home');};
$('play').onclick=()=>{
  if(playing){stop();return;}
  stopFold();foldAngle=0;folded=false;viewMode='home';$('moduleMotion').value=0;$('explode').value=0;$('laptop').checked=true;
  $('viewHint').textContent=hints.home;playing=true;start=performance.now();$('play').textContent='Pause docking motion';$('play').setAttribute('aria-pressed','true');update();
};
let down;
canvas.addEventListener('pointerdown',event=>down=[event.clientX,event.clientY]);
canvas.addEventListener('pointerup',event=>{
  if(!down||Math.hypot(event.clientX-down[0],event.clientY-down[1])>5)return;
  const rect=canvas.getBoundingClientRect(),ray=new THREE.Raycaster();
  ray.setFromCamera(new THREE.Vector2((event.clientX-rect.left)/rect.width*2-1,1-(event.clientY-rect.top)/rect.height*2),camera);
  const hit=ray.intersectObjects(meshes.filter(mesh=>mesh.visible))[0];if(hit)select(hit.object);
});
canvas.addEventListener('keydown',event=>{if(event.key==='Escape'){stop();stopFold();select(null);update();}});
new ResizeObserver(()=>{
  const rect=canvas.parentElement.getBoundingClientRect();renderer.setSize(rect.width,rect.height,false);camera.aspect=rect.width/rect.height;camera.updateProjectionMatrix();
}).observe(canvas.parentElement);
function frame(now){
  requestAnimationFrame(frame);
  if(playing){const q=((now-start)/1000)%10,t=q<4?q/4:q<5?1:q<9?1-(q-5)/4:0;$('motion').value=t*100;update();}
  if(foldMotion){const t=Math.min(1,(now-foldMotion.start)/foldMotion.duration),e=t*t*(3-2*t);foldAngle=foldMotion.from+(foldMotion.to-foldMotion.from)*e;if(t===1)stopFold();update();}
  controls.update();renderer.render(scene,camera);
}
requestAnimationFrame(frame);
window.deskDockState=()=>({revision:'D8',parts:meshes.length,visible:meshes.filter(m=>m.visible).length,explosion:+$('explode').value,motion:+$('motion').value,view:viewMode,moduleMotion:+$('moduleMotion').value,moduleParts:meshes.filter(m=>moduleParts.has(m.userData.name)).map(m=>({name:m.userData.name,position:m.position.toArray()})),playing,folded,foldAngle,foldAnimating:!!foldMotion,camLift:camLift(foldAngle),guardsVisible:meshes.filter(m=>guard(m.userData.name)&&m.visible).length,fansVisible:meshes.filter(m=>fan(m.userData.name)&&m.visible).length,positions:meshes.filter(m=>moving(m.userData.name)).map(m=>m.position.toArray())});
window.deskDockOrientation=()=>{
  const c=new THREE.PerspectiveCamera(36,1,1,4000);c.up.set(0,0,1);c.position.set(177,930,240);c.lookAt(177,30,155);c.updateMatrixWorld();
  const left=new THREE.Vector3(0,0,120).project(c),right=new THREE.Vector3(353.68,0,120).project(c);
  return {revision:'D8',keyboardLeftScreenX:left.x,keyboardRightScreenX:right.x,keyboardLeftAppearsOnRight:left.x>right.x,withdrawalX:18,laptopLeanDeg:5,fanDischargeDeg:18};
};
