/* ═══ CUSTOM CURSOR ═══════════════════════════════════ */
const dot = document.getElementById('cursor-dot');
const ring = document.getElementById('cursor-ring');
let mx = 0, my = 0, rx = 0, ry = 0;
document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY; });
(function animCursor() {
  rx += (mx - rx) * 0.12;
  ry += (my - ry) * 0.12;
  dot.style.left = mx + 'px'; dot.style.top = my + 'px';
  ring.style.left = rx + 'px'; ring.style.top = ry + 'px';
  requestAnimationFrame(animCursor);
})();

// Ripple on click
document.addEventListener('click', e => {
  const r = document.createElement('div');
  r.style.cssText = `position:fixed;left:${e.clientX}px;top:${e.clientY}px;width:4px;height:4px;border:2px solid rgba(34,197,94,0.6);border-radius:50%;transform:translate(-50%,-50%);pointer-events:none;z-index:9997;animation:rippleClick 0.6s ease-out forwards`;
  document.body.appendChild(r);
  setTimeout(() => r.remove(), 600);
});
const rs = document.createElement('style');
rs.textContent = `@keyframes rippleClick{to{width:80px;height:80px;opacity:0}}`;
document.head.appendChild(rs);

/* ═══ BUTTON RIPPLE EFFECT ════════════════════════════ */
document.querySelectorAll('.btn').forEach(btn => {
  btn.addEventListener('mousemove', e => {
    const r = btn.getBoundingClientRect();
    btn.style.setProperty('--x', ((e.clientX - r.left) / r.width * 100) + '%');
    btn.style.setProperty('--y', ((e.clientY - r.top) / r.height * 100) + '%');
  });
});

/* ═══ NAV SCROLL ══════════════════════════════════════ */
window.addEventListener('scroll', () => {
  document.getElementById('main-nav').classList.toggle('scrolled', window.scrollY > 60);
});

/* ═══ SCROLL REVEAL ═══════════════════════════════════ */
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); } });
}, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
document.querySelectorAll('.reveal, .reveal-left, .reveal-right').forEach(el => revealObserver.observe(el));

/* ═══ COUNTER ANIMATION ═══════════════════════════════ */
function animCount(id, target, decimals = 0) {
  const el = document.getElementById(id);
  if (!el) return;
  let start = 0;
  const step = target / 70;
  const interval = setInterval(() => {
    start = Math.min(start + step, target);
    el.textContent = decimals ? start.toFixed(decimals) : Math.floor(start);
    if (start >= target) clearInterval(interval);
  }, 22);
}
const statsObserver = new IntersectionObserver(entries => {
  if (entries[0].isIntersecting) {
    animCount('stat1', 10); animCount('stat2', 500); animCount('stat3', 98); animCount('stat4', 4.9, 1);
    statsObserver.disconnect();
  }
}, { threshold: 0.5 });
const strip = document.querySelector('.stats-strip');
if (strip) statsObserver.observe(strip);

/* ═══ THREE.JS: HERO BACKGROUND ══════════════════════ */
(function () {
  if (typeof THREE === 'undefined') return;
  const canvas = document.getElementById('hero-canvas');
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(canvas.offsetWidth, canvas.offsetHeight);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, canvas.offsetWidth / canvas.offsetHeight, 0.1, 100);
  camera.position.z = 5;

  // Animated grid plane
  const gridGeo = new THREE.PlaneGeometry(30, 30, 40, 40);
  const gridMat = new THREE.MeshBasicMaterial({ color: 0x16a34a, wireframe: true, transparent: true, opacity: 0.07 });
  const grid = new THREE.Mesh(gridGeo, gridMat);
  grid.rotation.x = -Math.PI / 2.8;
  grid.position.y = -2;
  scene.add(grid);

  // Floating spheres
  const spheres = [];
  for (let i = 0; i < 18; i++) {
    const r = Math.random() * 0.15 + 0.04;
    const geo = new THREE.SphereGeometry(r, 8, 8);
    const mat = new THREE.MeshBasicMaterial({
      color: Math.random() > 0.5 ? 0x22c55e : 0x86efac,
      transparent: true, opacity: Math.random() * 0.4 + 0.1, wireframe: Math.random() > 0.5
    });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set((Math.random() - 0.5) * 16, (Math.random() - 0.5) * 8, (Math.random() - 0.5) * 4);
    mesh._speed = { x: (Math.random() - 0.5) * 0.003, y: (Math.random() - 0.5) * 0.002 };
    mesh._phase = Math.random() * Math.PI * 2;
    scene.add(mesh);
    spheres.push(mesh);
  }

  // Particle ring
  const ringCount = 120;
  const ringGeo = new THREE.BufferGeometry();
  const rPos = new Float32Array(ringCount * 3);
  for (let i = 0; i < ringCount; i++) {
    const angle = (i / ringCount) * Math.PI * 2;
    rPos[i * 3] = Math.cos(angle) * 6 + (Math.random() - 0.5) * 0.4;
    rPos[i * 3 + 1] = (Math.random() - 0.5) * 0.5;
    rPos[i * 3 + 2] = Math.sin(angle) * 3 + (Math.random() - 0.5) * 0.4;
  }
  ringGeo.setAttribute('position', new THREE.BufferAttribute(rPos, 3));
  const ring3d = new THREE.Points(ringGeo, new THREE.PointsMaterial({ color: 0x22c55e, size: 0.05, transparent: true, opacity: 0.5 }));
  ring3d.rotation.x = 0.6;
  scene.add(ring3d);

  let mouseX = 0, mouseY = 0;
  document.addEventListener('mousemove', e => {
    mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
    mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
  });

  let t = 0;
  function animate() {
    requestAnimationFrame(animate);
    t += 0.008;
    grid.rotation.z = t * 0.03;
    ring3d.rotation.y = t * 0.15;
    camera.position.x += (mouseX * 0.6 - camera.position.x) * 0.03;
    camera.position.y += (-mouseY * 0.4 - camera.position.y) * 0.03;
    camera.lookAt(scene.position);
    spheres.forEach(s => {
      s.position.y += Math.sin(t + s._phase) * 0.003;
      s.position.x += s._speed.x;
      s.rotation.y += 0.005;
      if (Math.abs(s.position.x) > 8) s._speed.x *= -1;
    });
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener('resize', () => {
    const w = canvas.offsetWidth, h = canvas.offsetHeight;
    renderer.setSize(w, h);
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
  });
})();

/* ═══ THREE.JS: 3D PARCEL HERO ═══════════════════════ */
(function () {
  if (typeof THREE === 'undefined') return;
  const canvas = document.getElementById('parcel-canvas');
  if (!canvas) return;
  const w = canvas.offsetWidth, h = canvas.offsetHeight;
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(w, h);
  renderer.shadowMap.enabled = true;

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 100);
  camera.position.set(3, 2.5, 4);
  camera.lookAt(0, 0, 0);

  scene.add(new THREE.AmbientLight(0xffffff, 0.3));
  const dirLight = new THREE.DirectionalLight(0x86efac, 2.5);
  dirLight.position.set(5, 8, 5); dirLight.castShadow = true; scene.add(dirLight);
  const fillLight = new THREE.DirectionalLight(0x22c55e, 0.8);
  fillLight.position.set(-5, 2, -3); scene.add(fillLight);
  const rimLight = new THREE.PointLight(0x166534, 1.5, 10);
  rimLight.position.set(-2, -1, 3); scene.add(rimLight);

  // Main box
  const box = new THREE.Mesh(
    new THREE.BoxGeometry(2, 1.4, 2),
    new THREE.MeshPhongMaterial({ color: 0x1a5c2e, shininess: 80, specular: 0x22c55e, transparent: true, opacity: 0.95 })
  );
  box.castShadow = true; scene.add(box);

  // Tape strips
  const tapeMat = new THREE.MeshPhongMaterial({ color: 0x22c55e, shininess: 120, specular: 0x86efac });
  const tape1 = new THREE.Mesh(new THREE.BoxGeometry(0.3, 1.45, 2.01), tapeMat); scene.add(tape1);
  const tape2 = new THREE.Mesh(new THREE.BoxGeometry(2.01, 1.45, 0.3), tapeMat.clone()); scene.add(tape2);

  // Lid
  const lid = new THREE.Mesh(new THREE.BoxGeometry(2.05, 0.12, 2.05), new THREE.MeshPhongMaterial({ color: 0x166534, shininess: 60 }));
  lid.position.y = 0.76; scene.add(lid);

  // Label
  const label = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 0.7), new THREE.MeshPhongMaterial({ color: 0xdcfce7, shininess: 40 }));
  label.position.set(0, -0.1, 1.01); scene.add(label);

  // Orbiters
  const orbiters = [];
  [0.8, 1.6, 2.4].forEach((radius, i) => {
    const orb = new THREE.Mesh(
      new THREE.BoxGeometry(0.18, 0.18, 0.18),
      new THREE.MeshPhongMaterial({ color: [0x22c55e, 0x86efac, 0x4ade80][i], shininess: 60 })
    );
    orb._radius = radius; orb._speed = 0.8 + i * 0.3; orb._phase = i * 2.1; orb._y = (i - 1) * 0.5;
    scene.add(orb); orbiters.push(orb);
  });

  // Glow + grid
  const glowMat = new THREE.MeshBasicMaterial({ color: 0x22c55e, transparent: true, opacity: 0.06 });
  const glow = new THREE.Mesh(new THREE.CircleGeometry(2, 32), glowMat);
  glow.rotation.x = -Math.PI / 2; glow.position.y = -0.72; scene.add(glow);
  const gridHelper = new THREE.GridHelper(6, 10, 0x22c55e, 0x166534);
  gridHelper.material.transparent = true; gridHelper.material.opacity = 0.15;
  gridHelper.position.y = -0.72; scene.add(gridHelper);

  let t = 0, hover = false;
  canvas.addEventListener('mouseenter', () => hover = true);
  canvas.addEventListener('mouseleave', () => hover = false);

  function animate() {
    requestAnimationFrame(animate); t += 0.012;
    box.position.y = Math.sin(t * 0.8) * 0.08;
    box.rotation.y = t * 0.4;
    box.rotation.x = Math.sin(t * 0.3) * 0.06;
    lid.position.y = 0.76 + box.position.y; lid.rotation.copy(box.rotation);
    tape1.position.y = box.position.y; tape1.rotation.y = box.rotation.y;
    tape2.position.y = box.position.y; tape2.rotation.y = box.rotation.y;
    label.position.y = -0.1 + box.position.y; label.rotation.y = box.rotation.y;
    if (hover) box.rotation.y += 0.02;
    orbiters.forEach(orb => {
      const angle = t * orb._speed + orb._phase;
      orb.position.x = Math.cos(angle) * orb._radius;
      orb.position.z = Math.sin(angle) * orb._radius * 0.5;
      orb.position.y = orb._y + Math.sin(t + orb._phase) * 0.15 + box.position.y;
      orb.rotation.x += 0.03; orb.rotation.y += 0.02;
    });
    glowMat.opacity = 0.04 + Math.sin(t) * 0.03;
    rimLight.intensity = 1.2 + Math.sin(t * 1.5) * 0.4;
    renderer.render(scene, camera);
  }
  animate();

  window.addEventListener('resize', () => {
    const nw = canvas.offsetWidth, nh = canvas.offsetHeight;
    renderer.setSize(nw, nh); camera.aspect = nw / nh; camera.updateProjectionMatrix();
  });
})();

/* ═══ PARTICLES CANVAS (2D) ══════════════════════════ */
(function () {
  const c = document.getElementById('particles-canvas');
  const ctx = c.getContext('2d');
  function resize() { c.width = window.innerWidth; c.height = window.innerHeight; }
  resize(); window.addEventListener('resize', resize);
  const pts = Array.from({ length: 55 }, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    r: Math.random() * 1.2 + 0.3,
    vx: (Math.random() - 0.5) * 0.3,
    vy: (Math.random() - 0.5) * 0.25,
    alpha: Math.random() * 0.4 + 0.1
  }));
  function frame() {
    ctx.clearRect(0, 0, c.width, c.height);
    pts.forEach(p => {
      p.x += p.vx; p.y += p.vy;
      if (p.x < 0) p.x = c.width; if (p.x > c.width) p.x = 0;
      if (p.y < 0) p.y = c.height; if (p.y > c.height) p.y = 0;
      ctx.beginPath(); ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(134,239,172,${p.alpha})`; ctx.fill();
    });
    pts.forEach((a, i) => {
      pts.slice(i + 1).forEach(b => {
        const dx = a.x - b.x, dy = a.y - b.y, dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 110) {
          ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y);
          ctx.strokeStyle = `rgba(34,197,94,${0.08 * (1 - dist / 110)})`; ctx.lineWidth = 0.5; ctx.stroke();
        }
      });
    });
    requestAnimationFrame(frame);
  }
  frame();
})();

/* ═══ ESTIMATOR ══════════════════════════════════════ */
function calcEstimate() {
  const w = parseFloat(document.getElementById('est-weight').value) || 1;
  const type = document.getElementById('est-type').value;
  const base = 80, wc = Math.round(w * 20), sf = 20;
  const expr = type === 'express' ? 80 : 0;
  const frag = type === 'fragile' ? 50 : 0;
  const total = base + wc + sf + expr + frag;
  document.getElementById('est-base').textContent = '₹' + base;
  document.getElementById('est-wc').textContent = '₹' + wc;
  document.getElementById('est-sf').textContent = '₹' + (sf + expr + frag);
  document.getElementById('est-cost').textContent = '₹' + total;
  document.getElementById('est-time').textContent = type === 'express' ? '1-2 business days' : '3-5 business days';
  document.getElementById('est-result').style.display = 'block';
  document.getElementById('est-placeholder').style.display = 'none';
}

/* ═══ TRACKER ════════════════════════════════════════ */
function scrollToTrack() {
  document.getElementById('track-section').scrollIntoView({ behavior: 'smooth' });
}

function doTrack() {
  const id = document.getElementById('track-input').value.trim();
  const result = document.getElementById('track-result');
  const err = document.getElementById('track-error');
  result.style.display = 'none'; err.style.display = 'none';
  if (!id) { err.style.display = 'block'; err.textContent = 'Please enter a tracking ID'; return; }
  if (!id.toUpperCase().startsWith('SS')) {
    err.style.display = 'block'; err.textContent = '❌ Invalid tracking ID. SwiftShip IDs start with "SS"'; return;
  }
  renderMiniTimeline();
  result.style.display = 'block';
}

function renderMiniTimeline() {
  const stages = ['Created', 'Confirmed', 'Picked Up', 'At Hub', 'In Transit', 'Dest. Hub', 'Out for Delivery', 'OTP', 'Delivered'];
  const icons = ['📦', '✅', '🚗', '🏭', '🚛', '🏢', '🛵', '🔑', '🎉'];
  const current = 4;
  const row = document.getElementById('mini-timeline-content');
  let html = '';
  stages.forEach((s, i) => {
    if (i > 0) html += `<div class="mini-connector ${i <= current ? 'done' : ''}"></div>`;
    html += `<div class="mini-stage ${i < current ? 'done' : i === current ? 'active' : ''}">
      <div class="mini-stage-dot">${i <= current ? icons[i] : '○'}</div>
      <span>${s}</span>
    </div>`;
  });
  row.innerHTML = html;
}

/* ═══ MISC ═══════════════════════════════════════════ */
function gotoCreate() { window.location.href = 'create.html'; }
function logout() { window.location.href = 'login.html'; }

function showToast(msg, type = 'success') {
  const t = document.createElement('div');
  t.className = `toast toast-${type}`;
  t.textContent = msg;
  document.getElementById('toast-container').appendChild(t);
  setTimeout(() => {
    t.style.opacity = '0'; t.style.transform = 'translateX(30px)'; t.style.transition = 'all 0.3s';
    setTimeout(() => t.remove(), 300);
  }, 3500);
}











// # sourceURL=script.js
