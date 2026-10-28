// Procedural 3D dental implant scene (cut-away jaw, threaded implant, abutment, crown).
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { ParametricGeometry } from 'three/addons/geometries/ParametricGeometry.js';
import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';

const ss = THREE.MathUtils.smoothstep;
const clamp = THREE.MathUtils.clamp;
const lerp = THREE.MathUtils.lerp;
export const easeOut = t => 1 - Math.pow(1 - clamp(t, 0, 1), 3);
export const easeInOut = t => { t = clamp(t, 0, 1); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };

// ---- layout constants (scene units ~ mm) ----
export const GUM_TOP = 0.5, BONE_TOP = -2.2, BONE_BOT = -14.5, HALF_W = 17.5;
export const IMPLANT_L = 10, PITCH = 0.85;

// ---------- geometry ----------
export function implantGeometry({ L = IMPLANT_L, R = 2.0, pitch = PITCH, depth = 0.4, segU = 150, segV = 560 } = {}) {
  const collar = 0.85;
  const fn = (u, v, target) => {
    const y = -L + v * L;
    const th = u * Math.PI * 2;
    const s = (y + L) / L;
    const core = R * 0.74 + R * 0.14 * s;
    let ph = y / pitch + u; ph -= Math.floor(ph);
    let tri = 1 - Math.abs(2 * ph - 1);
    tri = Math.min(1, tri * 1.45);
    let thr = depth * tri;
    thr *= ss(-y, collar, collar + 0.5) * ss(y + L, 0.25, 1.7);
    const collarMix = 1 - ss(-y, collar - 0.05, collar + 0.15);
    let r = lerp(core + thr, core + depth * 0.62, collarMix);
    // bevel at the platform
    r -= 0.18 * ss(y, -0.18, 0);
    // rounded apex
    const a = Math.min(1, (y + L) / 1.15);
    r *= Math.sqrt(Math.max(0, 1 - (1 - a) * (1 - a)));
    target.set(r * Math.cos(th), y, -r * Math.sin(th));
  };
  const g = new ParametricGeometry(fn, segU, segV);
  return g;
}

function lathe(points, seg = 128) {
  const g = new THREE.LatheGeometry(points.map(p => new THREE.Vector2(p[0], p[1])), seg);
  return g;
}

export function abutmentGeometry() {
  // bottom sits on implant platform (y=0)
  const p = [[0, 0], [1.55, 0], [1.62, 0.12], [1.95, 0.9], [2.05, 1.55], [2.0, 1.7], [1.5, 1.8], [1.42, 2.2], [1.3, 5.2], [1.15, 5.55], [0.5, 5.65], [0, 5.65]];
  const curve = new THREE.SplineCurve(p.map(q => new THREE.Vector2(q[0], q[1])));
  const pts = curve.getPoints(90).map(v => [Math.max(0, v.x), v.y]);
  pts[0] = [0, 0]; pts[pts.length - 1] = [0, 5.65];
  return lathe(pts, 120);
}

export function crownGeometry({ seed = 0, scale = 1, wide = 1.0 } = {}) {
  const prof = [[0, 0], [2.25, 0], [2.6, 0.45], [3.4, 1.35], [4.15, 2.4], [4.55, 3.4], [4.6, 4.25], [4.4, 5.05], [3.95, 5.75], [3.2, 6.2], [2.1, 6.35], [1.0, 6.15], [0.001, 6.0]];
  const curve = new THREE.SplineCurve(prof.map(q => new THREE.Vector2(q[0], q[1])));
  const pts = curve.getPoints(110).map(v => new THREE.Vector2(Math.max(0, v.x), v.y));
  pts[0].set(0, 0); pts[pts.length - 1].set(0, 6.0);
  let g = new THREE.LatheGeometry(pts, 160);
  g.deleteAttribute('normal'); g.deleteAttribute('uv');
  g = mergeVertices(g, 1e-4);
  const pos = g.attributes.position;
  const rnd = (i) => { const x = Math.sin((i + 1) * 12.9898 + seed * 78.233) * 43758.5453; return x - Math.floor(x); };
  const cusps = [];
  for (let k = 0; k < 4; k++) {
    const a = Math.PI / 4 + k * Math.PI / 2 + (rnd(k) - .5) * 0.25;
    cusps.push({ x: Math.cos(a) * (2.35 + rnd(k + 9) * 0.3), z: Math.sin(a) * (2.2 + rnd(k + 5) * 0.3), h: 0.85 + rnd(k + 3) * 0.3 });
  }
  cusps.push({ x: 0.2, z: -2.9, h: 0.45 }); // distal cusp
  for (let i = 0; i < pos.count; i++) {
    let x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i);
    const r = Math.hypot(x, z);
    const occ = ss(y, 4.1, 5.9);
    let bump = 0;
    for (const c of cusps) { const d2 = (x - c.x) ** 2 + (z - c.z) ** 2; bump += c.h * Math.exp(-d2 / 2.1); }
    const fossa = -0.75 * Math.exp(-(r * r) / 2.2);
    const groove = -0.32 * (Math.exp(-(x * x) / 0.18) + Math.exp(-(z * z) / 0.18)) * ss(r, 0.3, 1.2) * (1 - ss(r, 3.4, 4.3));
    y += occ * (bump * 0.85 + fossa + groove);
    // gentle bulge + squash buccolingually
    x *= 1.05 * wide; z *= 0.93;
    pos.setXYZ(i, x * scale, y * scale, z * scale);
  }
  g.computeVertexNormals();
  return g;
}

export function rootGeometry({ len = 10.5, r0 = 1.6 } = {}) {
  const p = [[0.001, -len], [0.45, -len + 0.25], [0.85, -len + 1.6], [1.2, -len * 0.55], [r0, -1.2], [r0 + 0.15, 0.2], [r0 + 0.1, 0.8], [0.001, 0.8]];
  const curve = new THREE.SplineCurve(p.map(q => new THREE.Vector2(q[0], q[1])));
  const pts = curve.getPoints(60).map(v => new THREE.Vector2(Math.max(0.0005, v.x), v.y));
  return new THREE.LatheGeometry(pts, 64);
}


// sculpted gum: subdivided box -> rounded edges -> convex ridge with cuffs around teeth
export function gumGeometry({ w = HALF_W * 2 + 1, d = 13.6, top = GUM_TOP, bot = BONE_TOP, r = 1.25, teethX = [-9.6, 0, 9.6] } = {}) {
  const h = top - bot;
  let g = new THREE.BoxGeometry(w, h, d, 220, 10, 70);
  g.deleteAttribute('normal'); g.deleteAttribute('uv');
  g = mergeVertices(g, 1e-4);
  const pos = g.attributes.position, hw = w / 2, hh = h / 2, hd = d / 2;
  const v = new THREE.Vector3(), inner = new THREE.Vector3();
  for (let i = 0; i < pos.count; i++) {
    v.fromBufferAttribute(pos, i);
    inner.set(clamp(v.x, -hw + r, hw - r), clamp(v.y, -hh + r, hh - r), clamp(v.z, -hd + r, hd - r));
    const n = v.clone().sub(inner); const len = n.length();
    if (len > 1e-6) v.copy(inner).addScaledVector(n.divideScalar(len), r);
    // upper surface sculpt
    const up = ss(v.y, -hh * 0.2, hh);
    let dy = -0.55 * Math.pow(v.z / hd, 2);
    for (const tx of teethX) { const dd = Math.hypot((v.x - tx) / 4.9, v.z / 4.2); dy += 0.38 * Math.exp(-Math.pow(dd - 0.95, 2) / 0.05) - 0.25 * Math.exp(-dd * dd / 0.4); }
    // interdental papillae
    for (let k = 0; k < teethX.length - 1; k++) { const mx = (teethX[k] + teethX[k + 1]) / 2; dy += 0.35 * Math.exp(-Math.pow(v.x - mx, 2) / 1.6) * Math.exp(-v.z * v.z / 30); }
    v.y += dy * up;
    pos.setXYZ(i, v.x, v.y + (top + bot) / 2, v.z);
  }
  g.computeVertexNormals();
  return g;
}

// ---------- materials ----------
export function makeMaterials(clip) {
  const clipPlanes = clip ? [clip] : null;
  return {
    titanium: new THREE.MeshPhysicalMaterial({ color: 0xb4bcc6, metalness: 1, roughness: 0.27, clearcoat: 0.4, clearcoatRoughness: 0.2 }),
    abutment: new THREE.MeshPhysicalMaterial({ color: 0xd5dbe1, metalness: 1, roughness: 0.16 }),
    enamel: new THREE.MeshPhysicalMaterial({ color: 0xf1ebdf, roughness: 0.22, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.08, sheen: 0.4, sheenColor: new THREE.Color(0xfff6e8) }),
    zirconia: new THREE.MeshPhysicalMaterial({ color: 0xfbf8f2, roughness: 0.18, metalness: 0, clearcoat: 1, clearcoatRoughness: 0.05, sheen: 0.5, sheenColor: new THREE.Color(0xffffff) }),
    root: new THREE.MeshPhysicalMaterial({ color: 0xeadcbf, roughness: 0.5, clearcoat: 0.3 }),
    gum: new THREE.MeshPhysicalMaterial({ color: 0xe07b86, roughness: 0.38, clearcoat: 0.6, clearcoatRoughness: 0.25, sheen: 0.6, sheenColor: new THREE.Color(0xffb3bd), clippingPlanes: clipPlanes }),
    bone: new THREE.MeshPhysicalMaterial({ color: 0xe9dcc1, roughness: 0.78, clippingPlanes: clipPlanes }),
    dark: new THREE.MeshStandardMaterial({ color: 0x2a3036, metalness: 0.6, roughness: 0.5 }),
  };
}

const capVert = /* glsl */`varying vec3 vP; void main(){ vec4 w = modelMatrix*vec4(position,1.0); vP = w.xyz; gl_Position = projectionMatrix*viewMatrix*w; }`;
const noise = /* glsl */`
vec2 h2(vec2 p){ p=vec2(dot(p,vec2(127.1,311.7)),dot(p,vec2(269.5,183.3))); return fract(sin(p)*43758.5453);}
float worley(vec2 p){ vec2 i=floor(p), f=fract(p); float md=8.; for(int y=-1;y<=1;y++)for(int x=-1;x<=1;x++){vec2 g=vec2(float(x),float(y)); vec2 o=h2(i+g); vec2 r=g+o-f; md=min(md,dot(r,r));} return sqrt(md);}
`;
export function boneCapMaterial() {
  return new THREE.ShaderMaterial({
    uniforms: { uGlow: { value: 0 }, uGlowX: { value: 0 }, uHalfW: { value: HALF_W } },
    vertexShader: capVert,
    fragmentShader: noise + /* glsl */`
      varying vec3 vP; uniform float uGlow; uniform float uGlowX; uniform float uHalfW;
      void main(){
        vec2 p = vP.xy;
        float edge = min(min(p.x+uHalfW, uHalfW-p.x), min(p.y-(${BONE_BOT.toFixed(2)}), (${BONE_TOP.toFixed(2)})-p.y));
        float cort = 1.0-smoothstep(0.75,1.25,edge);
        vec2 q = p*0.62 + 0.55*vec2(worley(p*0.28), worley(p*0.28+3.1));
        float f1 = worley(q*1.25);
        float holes = smoothstep(0.50,0.40,f1);
        float f2 = worley(q*3.4+11.0);
        float small = smoothstep(0.30,0.20,f2)*0.6;
        vec3 base = vec3(0.945,0.895,0.80);
        vec3 marrow = mix(vec3(0.78,0.55,0.47), vec3(0.88,0.70,0.60), smoothstep(0.0,0.45,f1));
        vec3 c = mix(base, marrow, max(holes,small)*(1.0-cort)*smoothstep(0.0,0.6,edge-0.9));
        c = mix(c, vec3(0.975,0.95,0.90), cort);
        c *= 0.86 + 0.14*smoothstep(${BONE_BOT.toFixed(2)}, ${BONE_TOP.toFixed(2)}, p.y);
        // osseointegration glow around the implant
        float dx = abs(p.x-uGlowX);
        float inY = smoothstep(${(BONE_TOP - IMPLANT_L - 1.2).toFixed(2)}, ${(BONE_TOP - IMPLANT_L).toFixed(2)}, p.y) * (1.0-smoothstep(${BONE_TOP.toFixed(2)}-0.2, ${BONE_TOP.toFixed(2)}+0.3, p.y));
        float g = exp(-pow(max(dx-1.9,0.0),2.0)/2.2)*inY;
        c = mix(c, vec3(0.45,0.82,1.0), g*uGlow*0.75);
        gl_FragColor = vec4(pow(c, vec3(2.2)),1.0);
        #include <colorspace_fragment>
      }`,
  });
}
export function gumCapMaterial() {
  return new THREE.ShaderMaterial({
    vertexShader: capVert,
    fragmentShader: noise + /* glsl */`
      varying vec3 vP;
      void main(){
        vec2 p = vP.xy;
        float t = smoothstep(${BONE_TOP.toFixed(2)}, ${GUM_TOP.toFixed(2)}, p.y);
        vec3 c = mix(vec3(0.74,0.33,0.38), vec3(0.88,0.47,0.52), t);
        float w = worley(p*3.0);
        c *= 0.95 + 0.05*w;
        gl_FragColor = vec4(pow(c, vec3(2.2)),1.0);
        #include <colorspace_fragment>
      }`,
  });
}

// stencil-capped clipped solid (after three.js webgl_clipping_stencil)
function cappedSolid(geometry, material, capMaterial, plane, order) {
  const group = new THREE.Group();
  const base = new THREE.MeshBasicMaterial();
  base.depthWrite = false; base.depthTest = false; base.colorWrite = false;
  base.stencilWrite = true; base.stencilFunc = THREE.AlwaysStencilFunc;
  const back = base.clone(); back.side = THREE.BackSide; back.clippingPlanes = [plane];
  back.stencilFail = back.stencilZFail = back.stencilZPass = THREE.IncrementWrapStencilOp;
  const front = base.clone(); front.side = THREE.FrontSide; front.clippingPlanes = [plane];
  front.stencilFail = front.stencilZFail = front.stencilZPass = THREE.DecrementWrapStencilOp;
  const m0 = new THREE.Mesh(geometry, back); m0.renderOrder = order;
  const m1 = new THREE.Mesh(geometry, front); m1.renderOrder = order;
  capMaterial.stencilWrite = true; capMaterial.stencilRef = 0;
  capMaterial.stencilFunc = THREE.NotEqualStencilFunc;
  capMaterial.stencilFail = capMaterial.stencilZFail = capMaterial.stencilZPass = THREE.ReplaceStencilOp;
  const cap = new THREE.Mesh(new THREE.PlaneGeometry(200, 200), capMaterial);
  cap.renderOrder = order + 0.1;
  cap.onAfterRender = (r) => r.clearStencil();
  // plane normal (0,0,-1) keeps z<=0; cap lies on z=0 facing camera
  const solid = new THREE.Mesh(geometry, material); solid.renderOrder = order + 0.2;
  group.add(m0, m1, cap, solid);
  group.userData = { solid, cap };
  return group;
}

// ---------- scene ----------
export function buildScene(renderer, { transparent = false, bg = null, particles = true, neighbors = true, layout = 'single' } = {}) {
  const BR = 7.5;
  renderer.localClippingEnabled = true;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.95;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  const scene = new THREE.Scene();
  const pm = new THREE.PMREMGenerator(renderer);
  scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.75;
  if (bg) scene.background = bg;

  const clip = new THREE.Plane(new THREE.Vector3(0, 0, -1), 0);
  const M = makeMaterials(clip);

  // lights
  const key = new THREE.DirectionalLight(0xfff4e6, 2.0); key.position.set(10, 22, 16);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0004; key.shadow.normalBias = 0.02;
  Object.assign(key.shadow.camera, { left: -22, right: 22, top: 22, bottom: -22, near: 1, far: 70 });
  scene.add(key);
  const rim1 = new THREE.DirectionalLight(0x5fb4ff, 3.2); rim1.position.set(-14, 8, -14); scene.add(rim1);
  const rim2 = new THREE.DirectionalLight(0x8fe3ff, 1.6); rim2.position.set(16, 4, -10); scene.add(rim2);
  const fill = new THREE.HemisphereLight(0xdbe9ff, 0x1a2230, 0.5); scene.add(fill);

  const world = new THREE.Group(); scene.add(world);

  // jaw block
  const gumGeo = gumGeometry({ teethX: layout === 'bridge' ? [-BR, 0, BR] : neighbors ? [-9.6, 0, 9.6] : [0] });
  const boneGeo = new RoundedBoxGeometry(HALF_W * 2, BONE_TOP - BONE_BOT, 12.6, 6, 0.9);
  boneGeo.translate(0, (BONE_TOP + BONE_BOT) / 2, 0);
  const boneCap = boneCapMaterial();
  const bone = cappedSolid(boneGeo, M.bone, boneCap, clip, 1);
  const gum = cappedSolid(gumGeo, M.gum, gumCapMaterial(), clip, 2);
  bone.userData.solid.receiveShadow = true; gum.userData.solid.receiveShadow = true;
  world.add(bone, gum);

  // neighbouring natural teeth
  const teeth = new THREE.Group(); world.add(teeth);
  if (neighbors) {
    [-1, 1].forEach((side, k) => {
      const t = new THREE.Group();
      const c = new THREE.Mesh(crownGeometry({ seed: k + 3 }), M.enamel); c.castShadow = true; c.receiveShadow = true;
      t.add(c);
      [-1, 1].forEach(s2 => {
        const r = new THREE.Mesh(rootGeometry({ len: 10.2 + s2 * 0.6 }), M.root);
        r.position.set(s2 * 1.35, 0, 0); r.rotation.z = s2 * 0.07; r.renderOrder = 5;
        t.add(r);
      });
      t.position.set(side * 9.6, 0, 0);
      t.rotation.y = side * 0.12;
      teeth.add(t);
    });
  }

  // implant assembly (site at x=0)
  const implant = new THREE.Group();
  const post = new THREE.Mesh(implantGeometry(), M.titanium); post.castShadow = true; post.renderOrder = 6;
  const capTop = new THREE.Mesh(new THREE.CircleGeometry(1.95, 64).rotateX(-Math.PI / 2), M.titanium);
  const hex = new THREE.Mesh(new THREE.CylinderGeometry(0.85, 0.85, 0.04, 6), M.dark); hex.position.y = 0.01;
  implant.add(post, capTop, hex);
  world.add(implant);

  const ghost = new THREE.Mesh(implantGeometry({ segU: 40, segV: 160 }), new THREE.MeshBasicMaterial({ color: 0x3aa6dd, wireframe: true, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending }));
  ghost.position.y = BONE_TOP; ghost.scale.set(1.06, 1.0, 1.06); ghost.renderOrder = 9; world.add(ghost);
  const axisGeo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0, BONE_TOP - IMPLANT_L - 1.5, 0), new THREE.Vector3(0, 12, 0)]);
  const axis = new THREE.Line(axisGeo, new THREE.LineDashedMaterial({ color: 0x8fe3ff, dashSize: 0.6, gapSize: 0.4, transparent: true, opacity: 0, depthTest: false }));
  axis.computeLineDistances(); axis.renderOrder = 10; world.add(axis);

  const abut = new THREE.Mesh(abutmentGeometry(), M.abutment); abut.castShadow = true; abut.renderOrder = 6;
  world.add(abut);
  const crown = new THREE.Mesh(crownGeometry({ seed: 11, wide: 0.98 }), M.zirconia); crown.castShadow = true; crown.receiveShadow = true; crown.renderOrder = 7;
  world.add(crown);

  // 3-unit bridge on two implants
  const extra = { implants: [], abuts: [], crowns: [] };
  if (layout === 'bridge') {
    implant.position.x = abut.position.x = -BR;
    const i2 = implant.clone(); i2.position.x = BR; const a2 = abut.clone(); a2.position.x = BR;
    world.add(i2, a2); extra.implants.push(i2); extra.abuts.push(a2);
    crown.geometry = crownGeometry({ seed: 21, scale: 0.88 }); crown.position.x = -BR;
    [0, BR].forEach((x, k) => { const c = new THREE.Mesh(crownGeometry({ seed: 30 + k, scale: 0.88 }), M.zirconia); c.position.x = x; c.castShadow = c.receiveShadow = true; c.renderOrder = 7; world.add(c); extra.crowns.push(c); });
    // connectors between the units
    [-BR / 2, BR / 2].forEach(x => { const j = new THREE.Mesh(new THREE.SphereGeometry(2.2, 32, 24), M.zirconia); j.scale.set(1.2, 1.1, 1.3); j.position.set(x, 3.0, 0); crown.parent.add(j); extra.crowns.push(j); j.userData.base = 3.0; });
  }

  // scan plane: horizontal holographic slice
  const scanTex = (() => {
    const c = document.createElement('canvas'); c.width = 1024; c.height = 512; const x = c.getContext('2d');
    x.fillStyle = 'rgba(90,190,255,0.10)'; x.fillRect(0, 0, 1024, 512);
    x.strokeStyle = 'rgba(140,220,255,0.55)'; x.lineWidth = 2;
    for (let i = 0; i <= 1024; i += 32) { x.beginPath(); x.moveTo(i, 0); x.lineTo(i, 512); x.stroke(); }
    for (let j = 0; j <= 512; j += 32) { x.beginPath(); x.moveTo(0, j); x.lineTo(1024, j); x.stroke(); }
    x.strokeStyle = 'rgba(220,250,255,1)'; x.lineWidth = 10; x.strokeRect(5, 5, 1014, 502);
    const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t;
  })();
  const scan = new THREE.Mesh(new THREE.PlaneGeometry(HALF_W * 2 + 4, 17).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ map: scanTex, color: 0xffffff, transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, toneMapped: false }));
  scan.renderOrder = 11; world.add(scan);

  // ring pulse at crown margin
  const ring = new THREE.Mesh(new THREE.RingGeometry(4.6, 5.0, 96).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ color: new THREE.Color(0x8fe3ff).multiplyScalar(2.2), transparent: true, opacity: 0, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false }));
  ring.position.y = GUM_TOP + 0.05; ring.renderOrder = 12; world.add(ring);

  // soft glow beneath the jaw
  const glowTex = (() => { const c = document.createElement('canvas'); c.width = c.height = 256; const x = c.getContext('2d'); const g = x.createRadialGradient(128, 128, 0, 128, 128, 128); g.addColorStop(0, 'rgba(70,160,255,0.55)'); g.addColorStop(0.5, 'rgba(40,110,220,0.18)'); g.addColorStop(1, 'rgba(20,60,160,0)'); x.fillStyle = g; x.fillRect(0, 0, 256, 256); return new THREE.CanvasTexture(c); })();
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(70, 40).rotateX(-Math.PI / 2), new THREE.MeshBasicMaterial({ map: glowTex, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false }));
  floor.position.y = BONE_BOT - 1.2; floor.renderOrder = 0; floor.visible = !transparent; world.add(floor);

  // floating particles
  let dust = null;
  if (particles) {
    const n = 140, arr = new Float32Array(n * 3), seeds = [];
    for (let i = 0; i < n; i++) { const s = [Math.random(), Math.random(), Math.random()]; seeds.push(s); arr.set([(s[0] - .5) * 90, (s[1] - .5) * 50, -10 - s[2] * 40], i * 3); }
    const dg = new THREE.BufferGeometry(); dg.setAttribute('position', new THREE.BufferAttribute(arr, 3));
    const sprite = (() => { const c = document.createElement('canvas'); c.width = c.height = 64; const x = c.getContext('2d'); const g = x.createRadialGradient(32, 32, 0, 32, 32, 32); g.addColorStop(0, 'rgba(180,230,255,1)'); g.addColorStop(1, 'rgba(180,230,255,0)'); x.fillStyle = g; x.fillRect(0, 0, 64, 64); return new THREE.CanvasTexture(c); })();
    dust = new THREE.Points(dg, new THREE.PointsMaterial({ size: 0.9, map: sprite, transparent: true, opacity: 0.45, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false }));
    dust.userData.seeds = seeds; dust.userData.base = arr.slice();
    scene.add(dust);
  }

  const camera = new THREE.PerspectiveCamera(30, 16 / 9, 0.5, 400);
  const target = new THREE.Vector3(0, -3.2, 0);

  const parts = { extra, implant, ghost, axis, abut, crown, scan, ring, teeth, bone, gum, boneCap, dust, world, key, rim1, rim2 };

  // state -> scene
  function apply(s) {
    const st = Object.assign({ implantDrop: 0, implantOn: 1, ghost: 0, abutDrop: 0, abutOn: 1, crownDrop: 0, crownOn: 1, scanY: 99, scan: 0, glow: 0, ring: 0, ringScale: 1, az: 0, el: 0.2, dist: 70, fov: 30, tx: 0, ty: -3.2, filmOffset: 0, time: 0, explode: 0, jaw: 1, neighborsOn: 1, spin: 0 }, s);
    bone.visible = gum.visible = st.jaw > 0; teeth.visible = st.neighborsOn > 0;
    implant.visible = st.implantOn > 0;
    implant.position.y = BONE_TOP + st.implantDrop + st.explode * -2.2;
    implant.rotation.y = -(st.implantDrop / PITCH) * Math.PI * 2 + st.spin;
    abut.rotation.y = crown.rotation.y = st.spin;
    ghost.material.opacity = st.ghost * 0.32; ghost.visible = st.ghost > 0.001;
    axis.material.opacity = st.ghost * 0.9; axis.visible = st.ghost > 0.001;
    abut.visible = st.abutOn > 0; abut.position.y = BONE_TOP + st.abutDrop + st.explode * 3.0;
    crown.visible = st.crownOn > 0; crown.position.y = 0 + st.crownDrop + st.explode * 8.5;
    extra.implants.forEach(o => { o.visible = implant.visible; o.position.y = implant.position.y; o.rotation.y = implant.rotation.y; });
    extra.abuts.forEach(o => { o.visible = abut.visible; o.position.y = abut.position.y; });
    extra.crowns.forEach(o => { o.visible = crown.visible; o.position.y = crown.position.y + (o.userData.base || 0); });
    scan.position.y = st.scanY; scan.material.opacity = st.scan;
    scan.visible = st.scan > 0.001;
    boneCap.uniforms.uGlow.value = st.glow;
    ring.material.opacity = st.ring; ring.scale.setScalar(st.ringScale); ring.visible = st.ring > 0.001;
    if (dust) {
      const p = dust.geometry.attributes.position, b = dust.userData.base, sd = dust.userData.seeds;
      for (let i = 0; i < sd.length; i++) {
        p.setY(i, b[i * 3 + 1] + Math.sin(st.time * 0.35 + sd[i][0] * 20) * 1.5 + st.time * 0.25 * (0.4 + sd[i][2]));
        p.setX(i, b[i * 3] + Math.cos(st.time * 0.25 + sd[i][1] * 20) * 1.2);
      }
      p.needsUpdate = true;
    }
    camera.fov = st.fov; camera.filmOffset = st.filmOffset;
    target.set(st.tx, st.ty, 0);
    camera.position.set(target.x + st.dist * Math.sin(st.az) * Math.cos(st.el), target.y + st.dist * Math.sin(st.el), st.dist * Math.cos(st.az) * Math.cos(st.el));
    camera.lookAt(target);
    camera.updateProjectionMatrix();
  }

  return { scene, camera, apply, parts, M };
}

// ---------- hero timeline ----------
export const HERO_DURATION = 14;
export function heroState(t) {
  const seg = (a, b) => clamp((t - a) / (b - a), 0, 1);
  const s = { time: t };
  // camera: slow orbit
  const k = t / HERO_DURATION;
  s.az = lerp(-0.42, 0.34, easeInOut(k));
  s.el = lerp(0.16, 0.24, easeInOut(k));
  s.dist = lerp(74, 66, easeInOut(k));
  // scan sweep
  const sc = seg(0.5, 2.4);
  s.scanY = lerp(8, BONE_BOT + 0.6, easeInOut(sc));
  s.scan = Math.min(1, Math.sin(Math.PI * sc) * 1.6) * 0.9;
  // planning ghost
  s.ghost = seg(2.0, 2.7) * (1 - seg(3.7, 4.7));
  // implant screws in
  const im = seg(3.0, 6.2);
  s.implantDrop = lerp(16, 0, easeOut(im));
  s.implantOn = t >= 3.0 ? 1 : 0;
  // osseointegration glow
  s.glow = seg(5.6, 6.3) * (1 - seg(7.4, 8.4));
  // abutment
  const ab = seg(6.6, 7.9);
  s.abutDrop = lerp(14, 0, easeOut(ab)); s.abutOn = t >= 6.6 ? 1 : 0;
  // crown
  const cr = seg(8.2, 9.9);
  s.crownDrop = lerp(16, 0, easeOut(cr)); s.crownOn = t >= 8.2 ? 1 : 0;
  // completion ring
  const rg = seg(9.8, 11.2);
  s.ring = Math.sin(Math.PI * rg) * 0.9; s.ringScale = 1 + rg * 0.6;
  return s;
}
