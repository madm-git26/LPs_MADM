// Stock medical-illustration style (client reference): white background, solid satin-pink gums, bright
// white teeth, titanium implants screwed into the gum with their threads showing above it, abutments and
// the new tooth / bridge / denture floating just above. Kinds: allon4, snap2, snap4, single, bridge.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { implantGeometry, rootGeometry } from './pnw3d.js';
import { archCurve, sweep } from './arch3d.js';
import { incisorGeometry, molarGeometry, premolarGeometry } from './realistic.js';

const clamp = THREE.MathUtils.clamp, ss = THREE.MathUtils.smoothstep;
const Y = new THREE.Vector3(0, 1, 0);
const sgnpow = (x, p) => Math.sign(x) * Math.pow(Math.abs(x), p);
function frame(curve, t) {
  const C = curve.getPointAt(t), T = curve.getTangentAt(t).setY(0).normalize();
  return { C, T, O: new THREE.Vector3(-T.z, 0, T.x) };
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

function materials() {
  return {
    gum: stippled(new THREE.MeshPhysicalMaterial({ color: 0xb8566a, roughness: 0.55, clearcoat: 0.25, clearcoatRoughness: 0.4, sheen: 0.25, sheenRoughness: 0.5, sheenColor: new THREE.Color(0xf0a0b0), specularIntensity: 0.5 }), 0.12, 2.2),
    floor: stippled(new THREE.MeshPhysicalMaterial({ color: 0x96404f, roughness: 0.55, clearcoat: 0.2, clearcoatRoughness: 0.4, sheen: 0.3, sheenColor: new THREE.Color(0xe48893) }), 0.1, 2.0),
    base: new THREE.MeshPhysicalMaterial({ color: 0xbd5a6e, roughness: 0.32, clearcoat: 0.7, clearcoatRoughness: 0.15, sheen: 0.35, sheenColor: new THREE.Color(0xf4a0a9) }),
    enamel: new THREE.MeshPhysicalMaterial({ vertexColors: true, color: 0xffffff, roughness: 0.24, clearcoat: 1, clearcoatRoughness: 0.08, sheen: 0.2, sheenColor: new THREE.Color(0xffffff), specularIntensity: 0.8 }),
    root: new THREE.MeshPhysicalMaterial({ color: 0xead9b6, roughness: 0.5, clearcoat: 0.3 }),
    titanium: new THREE.MeshPhysicalMaterial({ color: 0xd2d8de, metalness: 1, roughness: 0.28, envMapIntensity: 2.6 }),
    brushed: new THREE.MeshPhysicalMaterial({ color: 0xdfe4e9, metalness: 0.85, roughness: 0.42, envMapIntensity: 2.2 }),
    blue: new THREE.MeshPhysicalMaterial({ color: 0x4f86d9, metalness: 0.85, roughness: 0.2, clearcoat: 0.6, envMapIntensity: 1.3 }),
    gold: new THREE.MeshPhysicalMaterial({ color: 0xd9b468, metalness: 1, roughness: 0.2, envMapIntensity: 1.4 }),
    dark: new THREE.MeshStandardMaterial({ color: 0x2b3036, metalness: 0.6, roughness: 0.5 }),
  };
}

// lower jaw gum: rounded crest at u = 0, flared base at u = -11
const gumSection = (s) => { const a = s * Math.PI * 2, sn = Math.sin(a), cs = Math.cos(a);
  if (sn >= 0) return [4.3 * sgnpow(cs, 0.75) + (cs > 0 ? 0.4 : 0), -5.4 + 5.4 * Math.pow(sn, 0.55)];
  return [5.5 * sgnpow(cs, 0.5) + (cs > 0 ? 0.4 : 0), -5.4 + 5.0 * sgnpow(sn, 0.6)]; };

function roundedEnds(section, t0 = 0, t1 = 1, span = 0.05, mid = -2.7) {
  return (s, t) => {
    const d = Math.min((t - t0) / span, (t1 - t) / span, 1);
    const f = Math.sqrt(Math.max(0, 1 - Math.pow(1 - Math.max(d, 0), 2)));
    const [n, u] = section(s, t); return [n * (0.15 + 0.85 * f), mid + (u - mid) * (0.15 + 0.85 * f)];
  };
}

export function buildStock(renderer, { kind = 'allon4', W = 1200, H = 900 } = {}) {
  renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 0.92;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.setClearColor(0xffffff, 1);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xffffff);
  const pm = new THREE.PMREMGenerator(renderer);
  scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; scene.environmentIntensity = 0.62;
  const M = materials();
  const key = new THREE.DirectionalLight(0xffffff, 1.5); key.position.set(4, 70, 8); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 18; key.shadow.blurSamples = 16; key.shadow.bias = -0.0003; key.shadow.normalBias = 0.03;
  Object.assign(key.shadow.camera, { left: -45, right: 45, top: 45, bottom: -45, near: 1, far: 140 });
  scene.add(key);
  const key2 = new THREE.DirectionalLight(0xffffff, 1.5); key2.position.set(-26, 34, 36); scene.add(key2);
  const fill = new THREE.DirectionalLight(0xfff4f0, 0.75); fill.position.set(34, 12, 22); scene.add(fill);
  const back = new THREE.DirectionalLight(0xffffff, 1.0); back.position.set(0, 18, -40); scene.add(back);
  scene.add(new THREE.HemisphereLight(0xffffff, 0xd8d2cc, 0.45));

  const curve = archCurve(1.3), L = curve.getLength();
  // gum ridge + floor of the mouth
  function buildRidge(ts) {
    let section = gumSection;
    if (ts) {
      const mids = ts.slice(1).map((t, i) => (t + ts[i]) / 2), w = (ts[1] - ts[0]) * 0.2;
      section = (s, t) => {
        const [n, u] = gumSection(s);
        let b = 0; for (const m of mids) b = Math.max(b, Math.exp(-Math.pow((t - m) / w, 2)));
        return [n, u + ss(u, -3.2, -0.3) * 1.6 * b];
      };
    }
    const ridge = new THREE.Mesh(sweep(curve, roundedEnds(section), { segs: ts ? 900 : 300, ring: 72 }), M.gum); ridge.castShadow = true; scene.add(ridge);
  }
  const floor = new THREE.Mesh(new THREE.SphereGeometry(1, 64, 32, 0, Math.PI * 2, 0, Math.PI / 2), M.floor);
  floor.scale.set(18.5, 3.0, 13.5); floor.position.set(0, -10.0, -4.0); floor.castShadow = true; scene.add(floor);
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(400, 400).rotateX(-Math.PI / 2), new THREE.ShadowMaterial({ opacity: 0.2 }));
  shadow.position.y = -11.3; shadow.receiveShadow = true; scene.add(shadow);

  const parts = new THREE.Group(); scene.add(parts);
  const orient = (m, T, O) => m.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(T, Y, O));

  // lower-arch tooth set; returns t (arch position) of every tooth
  const LOWER = ['M', 'M', 'P', 'P', 'C', 'L', 'I', 'I', 'L', 'C', 'P', 'P', 'M', 'M'];
  const geoFor = (k, i) => k === 'M' ? molarGeometry({ seed: i, scale: 0.88 }) : k === 'P' ? premolarGeometry({ seed: i + 20 }) : k === 'C' ? incisorGeometry({ w: 6.8, h: 9.8, t: 6.4, canine: true }) : k === 'L' ? incisorGeometry({ w: 6.0, h: 8.8, t: 5.4 }) : incisorGeometry({ w: 5.6, h: 8.6, t: 5.2 });
  function layout(list) {
    const geos = list.map(geoFor);
    const widths = geos.map(g => { g.computeBoundingBox(); return (g.boundingBox.max.x - g.boundingBox.min.x) * 0.94; });
    const total = widths.reduce((a, b) => a + b, 0), start = 0.5 - total / L / 2;
    let acc = 0; const ts = [];
    widths.forEach(w => { ts.push(clamp(start + (acc + w / 2) / L, 0.002, 0.998)); acc += w; });
    return { geos, ts };
  }
  function tooth(geo, k, t, y, withRoot) {
    const { C, T, O } = frame(curve, t);
    const g = new THREE.Group();
    const crown = new THREE.Mesh(geo, M.enamel); crown.castShadow = true; g.add(crown);
    if (withRoot) {
      if (k === 'M') [-1, 1].forEach(s2 => { const r = new THREE.Mesh(rootGeometry({ len: 9.6 + s2 * 0.4, r0: 1.45 }), M.root); r.position.set(s2 * 1.3, 0.1, 0); r.rotation.z = s2 * 0.07; g.add(r); });
      else { const r = new THREE.Mesh(rootGeometry({ len: k === 'C' ? 11 : 9.6, r0: k === 'I' || k === 'L' ? 1.15 : 1.4 }), M.root); r.scale.set(1, 1, 0.78); g.add(r); }
    }
    orient(g, T, O);
    const front = 'ILC'.includes(k);
    g.position.set(C.x, y - (front ? 0.5 : 0), C.z);
    if (front) { g.position.addScaledVector(O, 0.4); g.rotateX(-0.12); }
    parts.add(g); return g;
  }
  function implant(t, tilt, top, y = 4.2) {
    const { C, T } = frame(curve, t);
    const post = new THREE.Group();
    const m = new THREE.Mesh(implantGeometry({ L: 10, segU: 110, segV: 400 }), M.titanium); m.castShadow = true; post.add(m);
    const cap = new THREE.Mesh(new THREE.CircleGeometry(1.95, 48).rotateX(-Math.PI / 2), M.titanium); post.add(cap);
    post.position.set(C.x, y, C.z);
    if (tilt) { const backDir = t < 0.5 ? T.clone().negate() : T.clone(); post.quaternion.setFromUnitVectors(Y, Y.clone().multiplyScalar(Math.cos(tilt)).addScaledVector(backDir, Math.sin(tilt)).normalize()); }
    parts.add(post);
    const ab = new THREE.Group(); ab.position.set(C.x, y, C.z);
    if (top === 'mua') {
      const collar = new THREE.Mesh(new THREE.CylinderGeometry(1.75, 1.85, 1.6, 48), M.blue); collar.position.y = 0.8;
      const body = new THREE.Mesh(new THREE.CylinderGeometry(1.35, 1.6, 1.8, 48), M.brushed); body.position.y = 2.5;
      const cone = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 1.35, 0.9, 48), M.brushed); cone.position.y = 3.85;
      [collar, body, cone].forEach(o => { o.castShadow = true; ab.add(o); });
    } else if (top === 'ball') {
      const collar = new THREE.Mesh(new THREE.CylinderGeometry(1.7, 1.8, 1.4, 48), M.gold); collar.position.y = 0.7;
      const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.95, 1.5, 1.6, 48), M.gold); neck.position.y = 2.2;
      const ball = new THREE.Mesh(new THREE.SphereGeometry(1.2, 48, 32), M.gold); ball.position.y = 3.5;
      [collar, neck, ball].forEach(o => { o.castShadow = true; ab.add(o); });
    } else {
      const collar = new THREE.Mesh(new THREE.CylinderGeometry(1.95, 1.85, 1.3, 48), M.blue); collar.position.y = 0.65;
      const post2 = new THREE.Mesh(new THREE.CylinderGeometry(1.15, 1.45, 4.2, 48), M.brushed); post2.position.y = 3.4;
      [collar, post2].forEach(o => { o.castShadow = true; ab.add(o); });
    }
    parts.add(ab);
  }

  const view = { az: 0.18, el: 0.46, dist: 138, ty: 2, tz: -4, fov: 24 };
  if (kind === 'allon4' || kind === 'snap2' || kind === 'snap4') {
    const list = ['M', 'P', 'P', 'C', 'L', 'I', 'I', 'L', 'C', 'P', 'P', 'M'];
    const { geos, ts } = layout(list);
    const lift = kind === 'allon4' ? 19.5 : 18.5;
    buildRidge(null);
    const pros = new THREE.Group(); parts.add(pros);
    geos.forEach((g, i) => { const tt = tooth(g, list[i], ts[i], lift, false); pros.add(tt); });
    if (kind === 'allon4') {
      implant(0.35, 0, 'mua'); implant(0.65, 0, 'mua'); implant(0.2, 0.52, 'mua', 3.4); implant(0.8, 0.52, 'mua', 3.4);
    } else {
      (kind === 'snap2' ? [0.36, 0.64] : [0.24, 0.41, 0.59, 0.76]).forEach(t => implant(t, 0, 'ball'));
    }
    // denture / full-arch bridge: pink gum-coloured base under the teeth
    const t0 = ts[0] - 0.03, t1 = ts[ts.length - 1] + 0.03;
    const base = new THREE.Mesh(sweep(curve, (s) => { const a = s * Math.PI * 2, sn = Math.sin(a); return [5.4 * sgnpow(Math.cos(a), 0.55), sn > 0 ? 2.2 * Math.pow(sn, 0.6) : -3.2 * Math.pow(-sn, 0.7)]; }, { segs: 300, t0: Math.max(0.005, t0), t1: Math.min(0.995, t1) }), M.base);
    base.position.y = lift - 0.6; base.castShadow = true; pros.add(base);
  } else {
    const { geos, ts } = layout(LOWER);
    buildRidge(ts);
    const gap = kind === 'single' ? [12] : [10, 11, 12];
    geos.forEach((g, i) => { if (!gap.includes(i)) tooth(g, LOWER[i], ts[i], -0.6, false); });
    if (kind === 'single') {
      implant(ts[12], 0, 'std');
      tooth(geos[12], 'M', ts[12], 12.2, false);
    } else {
      implant(ts[10], 0, 'std'); implant(ts[12], 0, 'std');
      [10, 11, 12].forEach(i => tooth(geos[i], LOWER[i], ts[i], 12.2, false));
    }
    Object.assign(view, { az: 0.9, el: 0.4, dist: 142, ty: 1, tz: -3 });
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
