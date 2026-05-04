

/* ══ CURSOR ═════════════════════════════════════ */
const dot=document.getElementById('cdot'),ring=document.getElementById('cring');
let mx=0,my=0,rx=0,ry=0;
document.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY;});
(function loop(){rx+=(mx-rx)*.11;ry+=(my-ry)*.11;dot.style.left=mx+'px';dot.style.top=my+'px';ring.style.left=rx+'px';ring.style.top=ry+'px';requestAnimationFrame(loop);})();
document.addEventListener('click',e=>{
  const r=document.createElement('div');
  r.style.cssText=`position:fixed;left:${e.clientX}px;top:${e.clientY}px;width:4px;height:4px;border:2px solid rgba(34,197,94,.6);border-radius:50%;transform:translate(-50%,-50%);pointer-events:none;z-index:9997;animation:rpl .55s ease-out forwards`;
  document.body.appendChild(r);setTimeout(()=>r.remove(),600);
});
const rs=document.createElement('style');
rs.textContent='@keyframes rpl{to{width:72px;height:72px;opacity:0}}';
document.head.appendChild(rs);

/* ══ SCROLL REVEAL ══════════════════════════════ */
const ro=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting)e.target.classList.add('in');}),{threshold:.1,rootMargin:'0px 0px -30px 0px'});
document.querySelectorAll('.reveal,.reveal-right').forEach(el=>ro.observe(el));

/* ══ HERO PROGRESS BAR ══════════════════════════ */
setTimeout(()=>{
  const pb=document.getElementById('hero-progress');
  if(pb) pb.style.width='55%';
},600);

/* ══ 2D PARTICLES (Hero) ════════════════════════ */
(function(){
  const c=document.getElementById('hero-particles');
  if(!c)return;
  const ctx=c.getContext('2d');
  function resize(){c.width=c.parentElement.offsetWidth;c.height=c.parentElement.offsetHeight;}
  resize();window.addEventListener('resize',resize);
  const pts=Array.from({length:40},()=>({x:Math.random()*2000,y:Math.random()*500,vx:(Math.random()-.5)*.25,vy:(Math.random()-.5)*.2,r:Math.random()*1+.3,a:Math.random()*.35+.07}));
  function frame(){
    ctx.clearRect(0,0,c.width,c.height);
    pts.forEach(p=>{
      p.x+=p.vx;p.y+=p.vy;
      if(p.x<0)p.x=c.width;if(p.x>c.width)p.x=0;
      if(p.y<0)p.y=c.height;if(p.y>c.height)p.y=0;
      ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
      ctx.fillStyle=`rgba(134,239,172,${p.a})`;ctx.fill();
    });
    pts.forEach((a,i)=>{
      pts.slice(i+1).forEach(b=>{
        const dx=a.x-b.x,dy=a.y-b.y,d=Math.sqrt(dx*dx+dy*dy);
        if(d<90){ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.strokeStyle=`rgba(34,197,94,${.07*(1-d/90)})`;ctx.lineWidth=.5;ctx.stroke();}
      });
    });
    requestAnimationFrame(frame);
  }
  frame();
})();

/* ══ THREE.JS: 3D ROUTE GLOBE ════════════════════ */
(function(){
  if(typeof THREE==='undefined')return;
  const canvas=document.getElementById('globe-canvas');
  if(!canvas)return;
  const W=canvas.offsetWidth||300,H=canvas.offsetHeight||300;
  const renderer=new THREE.WebGLRenderer({canvas,alpha:true,antialias:true});
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));
  renderer.setSize(W,H);
  const scene=new THREE.Scene();
  const camera=new THREE.PerspectiveCamera(42,W/H,.1,100);
  camera.position.set(0,0,4.5);

  // Globe sphere
  const globeGeo=new THREE.SphereGeometry(1.6,64,64);
  const globeMat=new THREE.MeshPhongMaterial({
    color:0x0f3d1f,wireframe:false,transparent:true,opacity:.9,
    shininess:60,specular:0x22c55e
  });
  const globe=new THREE.Mesh(globeGeo,globeMat);
  scene.add(globe);

  // Wireframe overlay
  const wireMat=new THREE.MeshBasicMaterial({color:0x22c55e,wireframe:true,transparent:true,opacity:.08});
  scene.add(new THREE.Mesh(new THREE.SphereGeometry(1.62,24,24),wireMat));

  // Atmosphere glow
  const atmGeo=new THREE.SphereGeometry(1.72,32,32);
  const atmMat=new THREE.MeshBasicMaterial({color:0x22c55e,transparent:true,opacity:.06,side:THREE.BackSide});
  scene.add(new THREE.Mesh(atmGeo,atmMat));

  // Lat/Lon to 3D
  function ll3d(lat,lon,r=1.65){
    const phi=THREE.MathUtils.degToRad(90-lat);
    const theta=THREE.MathUtils.degToRad(lon+180);
    return new THREE.Vector3(
      -(r*Math.sin(phi)*Math.cos(theta)),
      r*Math.cos(phi),
      r*Math.sin(phi)*Math.sin(theta)
    );
  }

  // City dots — Mumbai & Delhi
  [
    {lat:19.07,lon:72.87,color:0x22c55e,size:0.055},
    {lat:28.63,lon:77.22,color:0x86efac,size:0.055}
  ].forEach(({lat,lon,color,size})=>{
    const pos=ll3d(lat,lon);
    const dot=new THREE.Mesh(
      new THREE.SphereGeometry(size,12,12),
      new THREE.MeshBasicMaterial({color})
    );
    dot.position.copy(pos);
    scene.add(dot);
    // Pulse ring
    const ring=new THREE.Mesh(
      new THREE.RingGeometry(size+.01,size+.05,16),
      new THREE.MeshBasicMaterial({color,transparent:true,opacity:.5,side:THREE.DoubleSide})
    );
    ring.position.copy(pos);
    ring.lookAt(0,0,0);
    ring._phase=Math.random()*Math.PI*2;
    scene.add(ring);
    ring._obj=dot; ring._baseSize=size;
  });

  // Flight arc Mumbai → Delhi
  const mum=ll3d(19.07,72.87);
  const del=ll3d(28.63,77.22);
  const arcPoints=[];
  const N=60;
  for(let i=0;i<=N;i++){
    const t=i/N;
    const v=new THREE.Vector3().lerpVectors(mum,del,t);
    const lift=Math.sin(t*Math.PI)*0.35;
    v.normalize().multiplyScalar(1.65+lift);
    arcPoints.push(v);
  }
  const arcGeo=new THREE.BufferGeometry().setFromPoints(arcPoints);
  const arcMat=new THREE.LineBasicMaterial({color:0x22c55e,transparent:true,opacity:.85,linewidth:2});
  const arcLine=new THREE.Line(arcGeo,arcMat);
  scene.add(arcLine);

  // Animated plane dot on arc
  const planeDot=new THREE.Mesh(
    new THREE.SphereGeometry(.055,8,8),
    new THREE.MeshBasicMaterial({color:0xffffff})
  );
  scene.add(planeDot);

  // Star field (background points)
  const starGeo=new THREE.BufferGeometry();
  const starPos=new Float32Array(300*3);
  for(let i=0;i<300;i++){const v=new THREE.Vector3().randomDirection().multiplyScalar(6+Math.random()*3);starPos[i*3]=v.x;starPos[i*3+1]=v.y;starPos[i*3+2]=v.z;}
  starGeo.setAttribute('position',new THREE.BufferAttribute(starPos,3));
  scene.add(new THREE.Points(starGeo,new THREE.PointsMaterial({color:0x86efac,size:.025,transparent:true,opacity:.4})));

  // Lights
  scene.add(new THREE.AmbientLight(0x166534,1.2));
  const dl=new THREE.DirectionalLight(0x86efac,2);dl.position.set(5,5,5);scene.add(dl);
  const pl=new THREE.PointLight(0x22c55e,1.5,10);pl.position.set(-3,2,3);scene.add(pl);

  // Orbit interaction
  let isDragging=false,prevX=0,prevY=0,rotY=0,rotX=0.3,velY=0,velX=0;
  canvas.addEventListener('mousedown',e=>{isDragging=true;prevX=e.clientX;prevY=e.clientY;});
  window.addEventListener('mouseup',()=>isDragging=false);
  window.addEventListener('mousemove',e=>{
    if(!isDragging)return;
    velY=(e.clientX-prevX)*.008;velX=(e.clientY-prevY)*.004;
    rotY+=velY;rotX+=velX;
    prevX=e.clientX;prevY=e.clientY;
  });

  let t=0,arcT=0;
  function animate(){
    requestAnimationFrame(animate);
    t+=0.008;
    if(!isDragging){velY*=.96;velX*=.96;rotY+=velY;rotX+=velX;rotY+=0.003;}
    globe.rotation.y=rotY;globe.rotation.x=Math.max(-.4,Math.min(.4,rotX));
    arcLine.rotation.copy(globe.rotation);
    // Move plane dot along arc
    arcT=(arcT+0.004)%1;
    const ai=Math.floor(arcT*(arcPoints.length-1));
    const lerpPt=arcPoints[Math.min(ai,arcPoints.length-1)].clone();
    const rot=new THREE.Euler().copy(globe.rotation);
    lerpPt.applyEuler(rot);
    planeDot.position.copy(lerpPt);
    // City pulse rings
    scene.children.filter(c=>c._phase!==undefined).forEach(ring=>{
      ring.scale.setScalar(1+Math.sin(t*2+ring._phase)*.2);
      ring.material.opacity=.3+Math.sin(t*2+ring._phase)*.2;
    });
    renderer.render(scene,camera);
  }
  animate();
})();

/* ══ TIMELINE DATA ══════════════════════════════ */
const STAGES=[
  {key:'created',  label:'Order Created',       icon:'📦',desc:'Parcel order placed on SwiftShip',      time:'Apr 22 · 3:15 PM',loc:'System'},
  {key:'confirmed',label:'Confirmed',            icon:'✅',desc:'Payment received, order confirmed',      time:'Apr 22 · 3:00 PM',loc:'System'},
  {key:'picked',   label:'Picked Up',            icon:'🚗',desc:'Parcel collected from sender address',   time:'Apr 23 · 11:00 AM',loc:'Mumbai'},
  {key:'hub',      label:'At Origin Hub',        icon:'🏭',desc:'Parcel received at Mumbai sorting hub',  time:'Apr 23 · 2:00 PM',loc:'Mumbai Sorting Hub'},
  {key:'transit',  label:'In Transit',           icon:'🚛',desc:'Parcel departed Mumbai, en route',       time:'Apr 24 · 10:30 AM',loc:'In Transit'},
  {key:'dest_hub', label:'Destination Hub',      icon:'🏢',desc:'Awaiting arrival at Delhi sorting hub',  time:'—',loc:'—'},
  {key:'ofd',      label:'Out for Delivery',     icon:'🛵',desc:'Delivery agent assigned',                time:'—',loc:'—'},
  {key:'otp',      label:'OTP Verification',     icon:'🔑',desc:'Receiver OTP verification pending',      time:'—',loc:'—'},
  {key:'delivered',label:'Delivered',            icon:'🎉',desc:'Parcel delivered successfully!',         time:'—',loc:'—'},
];
const CURRENT=4; // 0-based, "In Transit"

function renderTimeline(){
  const wrap=document.getElementById('main-timeline');
  if(!wrap)return;
  let html='';
  STAGES.forEach((s,i)=>{
    const isDone=i<CURRENT,isActive=i===CURRENT,isUp=i>CURRENT;
    const nc=isDone?'done':isActive?'active':'upcoming';
    const cc=i<STAGES.length-1?(isDone?'done':isActive?'partial':isUp?'dashed':'upcoming'):'';
    const tc=isUp?'upcoming':isActive?'active':'';
    const icon=isDone?'✓':s.icon;
    const connector=i<STAGES.length-1?`<div class="tl-connector ${cc}"></div>`:'';
    html+=`<div class="tl-item" style="animation:tlIn .5s ${i*.07}s both ease-out">
      ${connector}
      <div class="tl-node ${nc}">${icon}</div>
      <div class="tl-content" onclick="toggleTl(this)">
        <div class="tl-title ${tc}">${s.label}${isActive?` <span style="font-size:.68rem;font-weight:600;color:var(--g-light);background:rgba(34,197,94,.1);padding:2px 8px;border-radius:99px;margin-left:6px;">● NOW</span>`:''}</div>
        <div class="tl-sub">${isDone||isActive?s.time:'Pending'}</div>
        ${isDone||isActive?`<div class="tl-details">
          <div class="tl-detail-row">📅 <strong>${s.time}</strong></div>
          <div class="tl-detail-row">📍 <strong>${s.loc}</strong></div>
          <div class="tl-detail-row">💬 ${s.desc}</div>
          ${isActive?'<div class="tl-detail-row" style="color:var(--g-base);font-weight:600;margin-top:4px;">🔴 This is the current location of your parcel</div>':''}
        </div>`:''}
      </div>
    </div>`;
  });
  wrap.innerHTML=html;
  // Inject keyframe
  if(!document.getElementById('tlAnim')){
    const s=document.createElement('style');
    s.id='tlAnim';
    s.textContent='@keyframes tlIn{from{opacity:0;transform:translateX(-14px)}to{opacity:1;transform:translateX(0)}}';
    document.head.appendChild(s);
  }
}

function toggleTl(el){
  const d=el.querySelector('.tl-details');
  if(d) d.classList.toggle('open');
}

/* ══ EVENT LOG TOGGLE ═══════════════════════════ */
let logExpanded=false;
function toggleLog(btn){
  logExpanded=!logExpanded;
  btn.textContent=logExpanded?'Collapse ↑':'Show All';
}

/* ══ COPY TRACKING ══════════════════════════════ */
function copyTracking(){
  navigator.clipboard?.writeText('SS2024001234').catch(()=>{});
  showToast('Tracking ID copied! 📋','success');
}

/* ══ CANCEL MODAL ════════════════════════════════ */
function showCancelModal(){
  const overlay=document.getElementById('cancel-modal');
  document.getElementById('cancel-modal-content').innerHTML=`
    <div style="text-align:center;font-size:2.5rem;margin-bottom:1rem">⚠️</div>
    <h3 style="font-family:var(--font-head);font-size:1.25rem;color:var(--gray-700);text-align:center;margin-bottom:.5rem">Cancel Shipment?</h3>
    <p style="font-size:.88rem;color:var(--gray-400);text-align:center;margin-bottom:1.25rem">This action cannot be undone. Your parcel has not been picked up, so cancellation is permitted.</p>
    <div style="background:var(--off);border-radius:var(--r-sm);padding:10px 14px;text-align:center;margin-bottom:1rem;">
      <span style="font-family:monospace;font-weight:700;color:var(--g-base);letter-spacing:1px">SS2024001234</span>
    </div>
    <div style="margin-bottom:1rem">
      <label style="display:block;font-size:.75rem;font-weight:700;letter-spacing:.5px;text-transform:uppercase;color:var(--gray-400);margin-bottom:6px">Reason</label>
      <select style="width:100%;padding:10px 12px;border:1.5px solid var(--gray-200);border-radius:var(--r-sm);font-family:var(--font-body);font-size:.9rem;color:var(--gray-600);background:var(--white);">
        <option>Changed my mind</option><option>Wrong details</option><option>Not available</option><option>Other</option>
      </select>
    </div>
    <div style="background:#fffbeb;border:1px solid #fde68a;border-radius:var(--r-sm);padding:10px 14px;font-size:.78rem;color:#92400e;margin-bottom:1.25rem">
      💰 If payment was made, a refund will be processed within 5–7 business days.
    </div>
    <div style="display:flex;gap:10px">
      <button class="btn btn-outline" style="flex:1" onclick="closeCancelModal()">Keep Shipment</button>
      <button style="flex:1;padding:11px 22px;border-radius:var(--r-sm);background:var(--red);color:var(--white);font-family:var(--font-body);font-size:.9rem;font-weight:600;border:none;cursor:pointer;transition:all .2s" onclick="doCancel()">Yes, Cancel</button>
    </div>`;
  overlay.style.display='flex';
}
function closeCancelModal(){document.getElementById('cancel-modal').style.display='none';}
function doCancel(){closeCancelModal();showToast('Shipment cancelled successfully','success');}

/* ══ TOAST ═══════════════════════════════════════ */
function showToast(msg,type='success'){
  const t=document.createElement('div');
  t.className=`toast toast-${type}`;
  t.textContent=msg;
  document.getElementById('toast-container').appendChild(t);
  setTimeout(()=>{t.style.opacity='0';t.style.transform='translateX(28px)';t.style.transition='all .3s';setTimeout(()=>t.remove(),300);},3400);
}

/* ══ INIT ════════════════════════════════════════ */
renderTimeline();
// Open the active timeline node by default
setTimeout(()=>{
  const items=document.querySelectorAll('.tl-item');
  if(items[CURRENT]){
    const det=items[CURRENT].querySelector('.tl-details');
    if(det) det.classList.add('open');
  }
},400);

function logout(){window.location.href='login.html';}