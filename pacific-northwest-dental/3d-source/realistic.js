// Realistic "medical render" scenes for the pricing cards: frosted translucent jaw bone with the
// titanium implants visible inside, opaque gum with scalloped margins, anatomical teeth with natural
// colour, dark studio lighting. Kinds: single, bridge, allon4, snap2, snap4.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';
import { implantGeometry, crownGeometry, rootGeometry } from './pnw3d.js';
import { archCurve, sweep } from './arch3d.js';

const ss = THREE.MathUtils.smoothstep, clamp = THREE.MathUtils.clamp, lerp = THREE.MathUtils.lerp;
const Y = new THREE.Vector3(0, 1, 0);
const sgnpow = (x, p) => Math.sign(x) * Math.pow(Math.abs(x), p);

function frame(curve, t) {
  const C = curve.getPointAt(t), T = curve.getTangentAt(t).setY(0).normalize();
  return { C, T, O: new THREE.Vector3(-T.z, 0, T.x) };
}

// ---------- teeth ----------
const CERV = new THREE.Color(globalThis.TOOTH_CERV ?? 0xc4a878), BODY = new THREE.Color(globalThis.TOOTH_BODY ?? 0xe6dac3), EDGE = new THREE.Color(globalThis.TOOTH_EDGE ?? 0xd3dbe0);
export function paintEnamel(g, incisalBlue = true) {
  g.computeBoundingBox(); const y0 = g.boundingBox.min.y, y1 = g.boundingBox.max.y;
  const p = g.attributes.position, col = new Float32Array(p.count * 3), c = new THREE.Color();
  for (let i = 0; i < p.count; i++) {
    const s = (p.getY(i) - y0) / (y1 - y0);
    c.copy(CERV).lerp(BODY, ss(s, 0.02, 0.38));
    if (incisalBlue) c.lerp(EDGE, ss(s, 0.78, 1.0) * 0.8);
    col.set([c.r, c.g, c.b], i * 3);
  }
  g.setAttribute('color', new THREE.BufferAttribute(col, 3));
  return g;
}

export function incisorGeometry({ w = 7, h = 9.5, t = 5.6, canine = false } = {}) {
  let g = new THREE.CapsuleGeometry(0.5, 1, 18, 40);
  g.deleteAttribute('normal'); g.deleteAttribute('uv'); g = mergeVertices(g, 1e-5);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    const x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const s = (y + 1) / 2, ax = Math.abs(2 * x);
    let X = x * w * (0.74 + 0.26 * ss(s, 0, 0.55));
    let Z = z * t * (1 - 0.68 * ss(s, 0.3, 1.0));
    if (Z < 0) Z *= 0.82; else Z += 0.16 * t * (1 - ax * ax) * (1 - s * 0.6);
    let Yy = s * h;
    Yy = Math.min(Yy, canine ? h * (1.0 - 0.3 * Math.pow(ax, 1.25)) : h * (0.97 - 0.1 * Math.pow(ax, 6)));
    p.setXYZ(i, X, Yy, Z);
  }
  g.computeVertexNormals();
  return paintEnamel(g);
}
export function boxy(g, k = 0.9, p = 3.2) {
  g.computeBoundingBox(); const h = g.boundingBox.max.y;
  const pos = g.attributes.position;
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i), r = Math.hypot(x, z); if (r < 1e-6) continue;
    const th = Math.atan2(z, x), f = 1 / Math.pow(Math.pow(Math.abs(Math.cos(th)), p) + Math.pow(Math.abs(Math.sin(th)), p), 1 / p);
    const s = y / h, pinch = 1 - 0.07 * Math.exp(-Math.pow((s - 0.52) / 0.22, 2));
    const r2 = r * lerp(1, f, ss(s, 0.12, 0.45)) * k * pinch;
    pos.setX(i, x / r * r2); pos.setZ(i, z / r * r2);
  }
  g.computeVertexNormals(); return g;
}
export function molarGeometry({ seed = 0, scale = 0.86, wide = 1 } = {}) {
  return paintEnamel(boxy(crownGeometry({ seed, scale, wide })), false);
}
export function premolarGeometry({ seed = 0 } = {}) {
  const g = boxy(crownGeometry({ seed, scale: 0.74, wide: 0.82 }), 0.92, 2.6);
  return paintEnamel(g, false);
}

// translucent ivory bone: denser toward the silhouette (fresnel), clearer facing the camera
function ivoryGhost() {
  const m = new THREE.MeshPhysicalMaterial({ color: 0xf1e4c6, roughness: 0.45, clearcoat: 0.4, clearcoatRoughness: 0.3, transparent: true, depthWrite: false, sheen: 0.3, sheenColor: new THREE.Color(0xfff3dc) });
  m.onBeforeCompile = (sh) => {
    sh.fragmentShader = sh.fragmentShader.replace('#include <dithering_fragment>', `#include <dithering_fragment>
      float fr = pow(1.0 - abs(dot(normalize(normal), normalize(vViewPosition))), 1.6);
      gl_FragColor.a = mix(0.42, 0.96, fr);`);
  };
  return m;
}

// gingiva: fine stippled surface (perturbed normals) instead of smooth plastic
function stippled(m, amt = 0.16, freq = 2.6) {
  m.onBeforeCompile = (sh) => {
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', `#include <common>
      float h3(vec3 p){ return fract(sin(dot(p, vec3(127.1,311.7,74.7))) * 43758.5453); }
      float vn(vec3 p){ vec3 i=floor(p), f=fract(p); f=f*f*(3.0-2.0*f);
        return mix(mix(mix(h3(i),h3(i+vec3(1,0,0)),f.x),mix(h3(i+vec3(0,1,0)),h3(i+vec3(1,1,0)),f.x),f.y),
                   mix(mix(h3(i+vec3(0,0,1)),h3(i+vec3(1,0,1)),f.x),mix(h3(i+vec3(0,1,1)),h3(i+vec3(1,1,1)),f.x),f.y),f.z); }`)
      .replace('#include <normal_fragment_maps>', `#include <normal_fragment_maps>
      { vec3 q = vViewPosition * ${freq.toFixed(2)};
        normal = normalize(normal + ${amt.toFixed(2)} * (vec3(vn(q), vn(q + 17.0), vn(q + 41.0)) - 0.5)); }`);
  };
  return m;
}

// ---------- materials ----------
function materials() {
  return {
    bone: ivoryGhost(),
    gum: stippled(new THREE.MeshPhysicalMaterial({ color: 0x8c2f3e, roughness: 0.5, clearcoat: 0.45, clearcoatRoughness: 0.35, sheen: 0.2, sheenColor: new THREE.Color(0xff8f9e), sheenRoughness: 0.6, envMapIntensity: 0.55 })),
    flange: new THREE.MeshPhysicalMaterial({ envMapIntensity: 0.7, color: 0xb04656, roughness: 0.26, clearcoat: 1, clearcoatRoughness: 0.07, sheen: 0.45, sheenColor: new THREE.Color(0xffb7c0) }),
    enamel: new THREE.MeshPhysicalMaterial({ vertexColors: true, color: 0xffffff, roughness: 0.3, clearcoat: 0.8, clearcoatRoughness: 0.1, sheen: 0.2, sheenColor: new THREE.Color(0xffffff), specularIntensity: 0.85 }),
    root: new THREE.MeshPhysicalMaterial({ color: 0xe3d0a8, roughness: 0.55, clearcoat: 0.2 }),
    titanium: new THREE.MeshPhysicalMaterial({ color: 0xc9d0d7, metalness: 1, roughness: 0.22, envMapIntensity: 1.8 }),
    abutment: new THREE.MeshPhysicalMaterial({ color: 0xe6e9ec, metalness: 0.85, roughness: 0.34, envMapIntensity: 1.6 }),
    dark: new THREE.MeshStandardMaterial({ color: 0x2b3036, metalness: 0.6, roughness: 0.5 }),
  };
}

// jaw ridge sections (n = buccal offset, u = height); crest of the gum at u = 0.4
const boneSection = (s) => { const a = s * Math.PI * 2, sn = Math.sin(a); return [4.9 * sgnpow(Math.cos(a), 0.6), sn > 0 ? -8 + 6.4 * Math.pow(sn, 0.7) : -8 + 6.6 * sgnpow(sn, 0.35)]; };
const gumSection = (s) => { const a = s * Math.PI * 2, sn = Math.sin(a), cs = Math.cos(a); return sn > 0 ? [5.1 * sgnpow(cs, 0.6), -2.4 + 2.8 * Math.pow(sn, 0.66)] : [Math.sign(cs) * lerp(5.1, 4.86, Math.pow(-sn, 0.5)) * Math.pow(Math.abs(cs), 0.6), -2.4 - 1.4 * Math.pow(-sn, 0.8)]; };

function implantPost(M, L = 10) {
  const g = new THREE.Group();
  const post = new THREE.Mesh(implantGeometry({ L, segU: 120, segV: 420 }), M.titanium); post.castShadow = true;
  const cap = new THREE.Mesh(new THREE.CircleGeometry(1.95, 48).rotateX(-Math.PI / 2), M.titanium);
  const hex = new THREE.Mesh(new THREE.CylinderGeometry(0.85, 0.85, 0.04, 6), M.dark); hex.position.y = 0.01;
  g.add(post, cap, hex); return g;
}
function abutment(M, kind) {
  const g = new THREE.Group();
  if (kind === 'ball') {
    const neck = new THREE.Mesh(new THREE.CylinderGeometry(1.05, 1.75, 2.6, 48), M.abutment); neck.position.y = 1.3;
    const ball = new THREE.Mesh(new THREE.SphereGeometry(1.25, 48, 32), M.abutment); ball.position.y = 3.2;
    neck.castShadow = ball.castShadow = true; g.add(neck, ball);
  } else if (kind === 'mua') {
    const cyl = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.8, 2.8, 48), M.abutment); cyl.position.y = 1.4;
    const cone = new THREE.Mesh(new THREE.CylinderGeometry(0.95, 1.5, 1.1, 48), M.abutment); cone.position.y = 3.35;
    cyl.castShadow = true; g.add(cyl, cone);
  } else { // standard tapered abutment for a crown
    const p = [[0, 0], [1.55, 0], [1.95, 0.9], [2.05, 1.6], [1.5, 1.8], [1.3, 5.2], [1.1, 5.6], [0, 5.65]];
    const curve = new THREE.SplineCurve(p.map(q => new THREE.Vector2(q[0], q[1])));
    const m = new THREE.Mesh(new THREE.LatheGeometry(curve.getPoints(70).map(v => new THREE.Vector2(Math.max(0, v.x), v.y)), 96), M.abutment);
    m.castShadow = true; g.add(m);
  }
  return g;
}

export function buildReal(renderer, { kind = 'allon4', W = 1200, H = 900 } = {}) {
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.0;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.setClearColor(0x0b1116, 1);
  const scene = new THREE.Scene();
  const pm = new THREE.PMREMGenerator(renderer);
  scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; scene.environmentIntensity = 0.7;
  // studio backdrop
  const c = document.createElement('canvas'); c.width = 512; c.height = 384; const x = c.getContext('2d');
  const g = x.createRadialGradient(256, 150, 10, 256, 200, 380);
  g.addColorStop(0, '#26323d'); g.addColorStop(0.45, '#121a21'); g.addColorStop(1, '#030507');
  x.fillStyle = g; x.fillRect(0, 0, 512, 384);
  scene.background = new THREE.CanvasTexture(c); scene.background.colorSpace = THREE.SRGBColorSpace;

  const M = materials();
  const key = new THREE.DirectionalLight(0xfff3e4, 2.6); key.position.set(14, 34, 26); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 6; key.shadow.bias = -0.0003; key.shadow.normalBias = 0.02;
  Object.assign(key.shadow.camera, { left: -40, right: 40, top: 40, bottom: -40, near: 1, far: 120 });
  scene.add(key);
  const rimL = new THREE.DirectionalLight(0x9fd4ff, 2.2); rimL.position.set(-26, 16, -26); scene.add(rimL);
  const rimR = new THREE.DirectionalLight(0xffffff, 1.2); rimR.position.set(28, 10, -20); scene.add(rimR);
  scene.add(new THREE.HemisphereLight(0xe6eef8, 0x1a1f26, 0.45));

  const isArch = kind === 'allon4' || kind === 'snap2' || kind === 'snap4';
  const curve = isArch ? archCurve(1.3) : new THREE.CatmullRomCurve3([new THREE.Vector3(-18.5, 0, -1.4), new THREE.Vector3(0, 0, 0.9), new THREE.Vector3(18.5, 0, -1.4)]);
  const bone = new THREE.Mesh(sweep(curve, boneSection, { segs: isArch ? 240 : 120 }), M.bone); bone.renderOrder = 10; scene.add(bone);
  const gumMesh = new THREE.Mesh(sweep(curve, gumSection, { segs: isArch ? 240 : 120 }), M.gum); gumMesh.receiveShadow = true; gumMesh.castShadow = true; scene.add(gumMesh);

  // soft floor shadow
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(220, 220).rotateX(-Math.PI / 2), new THREE.ShadowMaterial({ opacity: 0.45 }));
  floor.position.y = -14.9; floor.receiveShadow = true; scene.add(floor);

  const parts = new THREE.Group(); scene.add(parts);
  const L = curve.getLength();
  function placeImplant(t, tilt, top, lift = 0) {
    const { C, T } = frame(curve, t);
    const post = implantPost(M); post.position.set(C.x, -1.6, C.z);
    if (tilt) { const back = t < 0.5 ? T.clone().negate() : T.clone(); post.quaternion.setFromUnitVectors(Y, Y.clone().multiplyScalar(Math.cos(tilt)).addScaledVector(back, Math.sin(tilt)).normalize()); }
    parts.add(post);
    const ab = abutment(M, top); ab.position.set(C.x, -1.6 + lift, C.z); parts.add(ab);
    return C;
  }
  function naturalMolar(t, seed) {
    const { C, T, O } = frame(curve, t);
    const tooth = new THREE.Group();
    const crown = new THREE.Mesh(molarGeometry({ seed, scale: 1 }), M.enamel); crown.castShadow = true; tooth.add(crown);
    [-1, 1].forEach(s2 => { const r = new THREE.Mesh(rootGeometry({ len: 10.4 + s2 * 0.5 }), M.root); r.position.set(s2 * 1.35, 0.1, 0); r.rotation.z = s2 * 0.07; tooth.add(r); });
    tooth.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(T, Y, O));
    tooth.position.set(C.x, -0.2, C.z); parts.add(tooth);
  }

  // prosthesis teeth laid out along the arch, touching, with scalloped gingiva between them
  function prosthesis(yBase, list, flangeOpts) {
    const geos = list.map((k, i) => k === 'M' ? molarGeometry({ seed: i, scale: 0.86 }) : k === 'P' ? premolarGeometry({ seed: i + 20 }) : k === 'C' ? incisorGeometry({ w: 7.2, h: 9.6, t: 6.4, canine: true }) : k === 'L' ? incisorGeometry({ w: 5.9, h: 8.6, t: 5.2 }) : incisorGeometry({ w: 7.4, h: 9.6, t: 5.6 }));
    const widths = geos.map(gg => { gg.computeBoundingBox(); return (gg.boundingBox.max.x - gg.boundingBox.min.x) * 0.93; });
    const total = widths.reduce((a, b) => a + b, 0), start = 0.5 - total / L / 2;
    const bounds = []; let acc = 0;
    const grp = new THREE.Group();
    geos.forEach((gg, i) => {
      const t = clamp(start + (acc + widths[i] / 2) / L, 0.001, 0.999);
      bounds.push(start + acc / L); acc += widths[i];
      const { C, T, O } = frame(curve, t);
      const m = new THREE.Mesh(gg, M.enamel); m.castShadow = true; m.receiveShadow = true;
      m.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(T, Y, O));
      const front = 'ILC'.includes(list[i]);
      m.position.set(C.x, yBase - (front ? 0.9 : 0.3), C.z); if (front) { m.position.addScaledVector(O, 0.6); m.rotateX(-0.09); }
      grp.add(m);
    });
    bounds.push(start + acc / L);
    const inner = bounds.slice(1, -1);
    const pap = t => { let v = 0; for (const b of inner) v = Math.max(v, Math.exp(-Math.pow((t - b) * L / 1.5, 2))); return v; };
    const fl = sweep(curve, (s, t) => {
      const a = s * Math.PI * 2, sn = Math.sin(a), top = flangeOpts.top + flangeOpts.pap * pap(t);
      return [flangeOpts.w * sgnpow(Math.cos(a), 0.6) + 0.3, sn > 0 ? top * Math.pow(sn, 0.55) : -flangeOpts.bot * Math.pow(-sn, 0.75)];
    }, { segs: 420, t0: Math.max(0.01, bounds[0] - 0.012), t1: Math.min(0.99, bounds[bounds.length - 1] + 0.012) });
    const flange = new THREE.Mesh(fl, M.flange); flange.position.y = yBase; flange.castShadow = true; flange.receiveShadow = true;
    grp.add(flange);
    parts.add(grp);
    return grp;
  }

  const view = { az: 0, el: 0.3, dist: 90, ty: 0, tz: 0, fov: 24 };
  if (kind === 'allon4') {
    placeImplant(0.35, 0, 'mua'); placeImplant(0.65, 0, 'mua');
    placeImplant(0.2, 0.52, 'mua'); placeImplant(0.8, 0.52, 'mua');
    prosthesis(15, ['M', 'P', 'P', 'C', 'L', 'I', 'I', 'L', 'C', 'P', 'P', 'M'], { w: 4.6, top: 1.6, pap: 2.2, bot: 2.6 });
    Object.assign(view, { az: 0.32, el: 0.4, dist: 132, ty: 0.5, tz: -3 });
  } else if (kind === 'snap2' || kind === 'snap4') {
    (kind === 'snap2' ? [0.36, 0.64] : [0.24, 0.41, 0.59, 0.76]).forEach(t => placeImplant(t, 0, 'ball'));
    prosthesis(15.5, ['M', 'P', 'P', 'C', 'L', 'I', 'I', 'L', 'C', 'P', 'P', 'M'], { w: 6.2, top: 1.8, pap: 2.0, bot: 4.2 });
    Object.assign(view, { az: 0.32, el: 0.4, dist: 134, ty: 0.5, tz: -3 });
  } else if (kind === 'single') {
    naturalMolar(0.23, 3); naturalMolar(0.77, 5);
    placeImplant(0.5, 0, 'std');
    const crown = new THREE.Mesh(molarGeometry({ seed: 11, scale: 0.98 }), M.enamel); crown.castShadow = true;
    const { C, T, O } = frame(curve, 0.5); crown.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(T, Y, O));
    crown.position.set(C.x, 5.2, C.z); parts.add(crown);
    Object.assign(view, { az: 0.42, el: 0.22, dist: 80, ty: -2.5, tz: 0 });
  } else if (kind === 'bridge') {
    [0.29, 0.71].forEach(t => placeImplant(t, 0, 'std'));
    const br = new THREE.Group();
    [0.29, 0.5, 0.71].forEach((t, i) => { const { C, T, O } = frame(curve, t); const m = new THREE.Mesh(molarGeometry({ seed: 30 + i, scale: 0.9 }), M.enamel); m.castShadow = true; m.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(T, Y, O)); m.position.set(C.x, 0, C.z); br.add(m); });
    [0.395, 0.605].forEach(t => { const { C } = frame(curve, t); const j = new THREE.Mesh(new THREE.SphereGeometry(2.1, 32, 24), M.enamel.clone()); j.material.vertexColors = false; j.material.color.set(0xeee6d6); j.scale.set(1.3, 1.1, 1.35); j.position.set(C.x, 2.8, C.z); br.add(j); });
    br.position.y = 5.0; parts.add(br);
    Object.assign(view, { az: 0.42, el: 0.22, dist: 80, ty: -2.5, tz: 0 });
  }

  const camera = new THREE.PerspectiveCamera(view.fov, W / H, 1, 600);
  const target = new THREE.Vector3();
  function apply(st = {}) {
    const v = Object.assign({}, view, st);
    camera.fov = v.fov; target.set(0, v.ty, v.tz);
    camera.position.set(v.dist * Math.sin(v.az) * Math.cos(v.el), v.ty + v.dist * Math.sin(v.el), v.tz + v.dist * Math.cos(v.az) * Math.cos(v.el));
    camera.lookAt(target); camera.updateProjectionMatrix();
  }
  apply();
  return { scene, camera, apply };
}
