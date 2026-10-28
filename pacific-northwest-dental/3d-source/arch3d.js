// Full-arch scenes: All-On-4, snap-in dentures (2 / 4 implants) and a 3-unit implant bridge.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';
import { mergeVertices } from 'three/addons/utils/BufferGeometryUtils.js';
import { implantGeometry, abutmentGeometry, crownGeometry, makeMaterials } from './pnw3d.js';

const Y = new THREE.Vector3(0, 1, 0);

export function archCurve(scale = 1) {
  const p = [[-20.5, -15], [-19.5, -6], [-16, 2.5], [-9.5, 9.5], [0, 12.2], [9.5, 9.5], [16, 2.5], [19.5, -6], [20.5, -15]];
  return new THREE.CatmullRomCurve3(p.map(q => new THREE.Vector3(q[0] * scale, 0, q[1] * scale)), false, 'centripetal');
}
function frame(curve, t) {
  const C = curve.getPointAt(t), T = curve.getTangentAt(t).setY(0).normalize();
  const O = new THREE.Vector3(-T.z, 0, T.x); // outward (buccal)
  return { C, T, O };
}

// sweep a closed 2D section (n = buccal offset, u = height) along the arch, capped at both ends
export function sweep(curve, section, { segs = 220, ring = 64, t0 = 0, t1 = 1, yOff = 0 } = {}) {
  const pos = [], idx = [];
  for (let i = 0; i <= segs; i++) {
    const t = t0 + (t1 - t0) * i / segs;
    const { C, O } = frame(curve, t);
    const endTaper = Math.min(1, Math.min(i, segs - i) / (segs * 0.035) + 0.55);
    for (let k = 0; k < ring; k++) {
      const [n, u] = section(k / ring, t);
      pos.push(C.x + O.x * n * endTaper, C.y + u + yOff, C.z + O.z * n * endTaper);
    }
  }
  for (let i = 0; i < segs; i++) for (let k = 0; k < ring; k++) {
    const a = i * ring + k, b = i * ring + (k + 1) % ring, c = (i + 1) * ring + k, d = (i + 1) * ring + (k + 1) % ring;
    idx.push(a, c, b, b, c, d);
  }
  // end caps
  [0, segs].forEach((i, e) => {
    const base = pos.length / 3; let cx = 0, cy = 0, cz = 0;
    for (let k = 0; k < ring; k++) { cx += pos[(i * ring + k) * 3]; cy += pos[(i * ring + k) * 3 + 1]; cz += pos[(i * ring + k) * 3 + 2]; }
    pos.push(cx / ring, cy / ring, cz / ring);
    for (let k = 0; k < ring; k++) { const a = i * ring + k, b = i * ring + (k + 1) % ring; if (e === 0) idx.push(base, a, b); else idx.push(base, b, a); }
  });
  let g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3)); g.setIndex(idx);
  g = mergeVertices(g, 1e-4); g.computeVertexNormals();
  return g;
}

const sgnpow = (x, p) => Math.sign(x) * Math.pow(Math.abs(x), p);
// healed ridge (gum over bone): flat-ish bottom, rounded crest at u = 0
const ridgeSection = (s) => { const a = s * Math.PI * 2; const sn = Math.sin(a); return [5.4 * sgnpow(Math.cos(a), 0.55), sn > 0 ? 4.6 * Math.pow(sn, 0.7) - 4.6 : 6.0 * sgnpow(sn, 0.9) - 4.6]; };
// prosthetic gum flange that wraps the tooth necks
const flangeSection = (s) => { const a = s * Math.PI * 2; const sn = Math.sin(a); return [4.4 * sgnpow(Math.cos(a), 0.6) + 0.4, sn > 0 ? 2.4 * Math.pow(sn, 0.8) : 1.8 * sgnpow(sn, 0.8)]; };
// full denture base (saddle over the ridge)
const dentureSection = (s) => { const a = s * Math.PI * 2; const sn = Math.sin(a); return [5.8 * sgnpow(Math.cos(a), 0.55) + 0.2, sn > 0 ? 2.6 * Math.pow(sn, 0.8) : 3.4 * sgnpow(sn, 0.7)]; };

function incisorGeometry({ w = 5.4, h = 7.4, d = 2.6, canine = false } = {}) {
  let g = new RoundedBoxGeometry(w, h, d, 8, Math.min(1.6, d * 0.48));
  g.deleteAttribute('normal'); g.deleteAttribute('uv'); g = mergeVertices(g, 1e-4);
  const p = g.attributes.position;
  for (let i = 0; i < p.count; i++) {
    let x = p.getX(i), y = p.getY(i), z = p.getZ(i);
    const s = (y + h / 2) / h; // 0 cervical .. 1 incisal
    x *= 0.8 + 0.2 * Math.min(1, s * 1.6); // narrow neck
    z *= 1 - 0.45 * s; // thin incisal edge
    z += 0.6 - 0.09 * x * x; // labial convexity
    if (canine) y -= Math.abs(x) * 0.55 * Math.max(0, s - 0.55) * 2.2;
    p.setXYZ(i, x, y + h / 2, z);
  }
  g.computeVertexNormals();
  return g;
}

export function buildArch(renderer, { kind = 'allon4' } = {}) {
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 0.95;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  const pm = new THREE.PMREMGenerator(renderer);
  scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; scene.environmentIntensity = 0.8;
  const M = makeMaterials(null);
  const key = new THREE.DirectionalLight(0xfff4e6, 2.1); key.position.set(12, 30, 22); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -30, right: 30, top: 30, bottom: -30, near: 1, far: 90 }); key.shadow.bias = -0.0004;
  scene.add(key);
  const rim = new THREE.DirectionalLight(0x6fbaff, 2.4); rim.position.set(-20, 14, -24); scene.add(rim);
  const rim2 = new THREE.DirectionalLight(0x9fe6ff, 1.2); rim2.position.set(22, 8, -18); scene.add(rim2);
  scene.add(new THREE.HemisphereLight(0xe3eeff, 0x2a3240, 0.55));

  const curve = archCurve(1.3);
  const gumMat = new THREE.MeshPhysicalMaterial({ color: 0xe58a95, roughness: 0.35, clearcoat: 0.6, clearcoatRoughness: 0.2, transparent: true, opacity: 0.62, depthWrite: false, sheen: 0.5, sheenColor: new THREE.Color(0xffc0c8) });
  const ridge = new THREE.Mesh(sweep(curve, ridgeSection), gumMat); ridge.renderOrder = 5; scene.add(ridge);
  const boneMat = new THREE.MeshPhysicalMaterial({ color: 0xeee2c9, roughness: 0.75, transparent: true, opacity: 0.35, depthWrite: false });
  const bone = new THREE.Mesh(sweep(curve, s => { const [n, u] = ridgeSection(s); return [n * 0.82, u * 0.86 - 1.2]; }), boneMat); bone.renderOrder = 4; scene.add(bone);

  const implants = new THREE.Group(); scene.add(implants);
  const pros = new THREE.Group(); scene.add(pros);
  const implGeo = implantGeometry({ segU: 110, segV: 380, L: 10 });
  const ballGeo = (() => { const g = new THREE.Group(); return g; })();

  function addImplant(t, tiltDeg, top) {
    const { C, T, O } = frame(curve, t);
    const post = new THREE.Group();
    const m = new THREE.Mesh(implGeo, M.titanium); m.castShadow = true; m.renderOrder = 2; post.add(m);
    post.position.set(C.x, 0.2, C.z);
    if (tiltDeg) {
      const back = t < 0.5 ? T.clone().negate() : T.clone();
      post.quaternion.setFromUnitVectors(Y, Y.clone().multiplyScalar(Math.cos(tiltDeg * Math.PI / 180)).addScaledVector(back, Math.sin(tiltDeg * Math.PI / 180)).normalize());
    }
    implants.add(post);
    // top attachment, always vertical
    const at = new THREE.Group(); at.position.set(C.x, 0.2, C.z);
    if (top === 'mua') {
      const cyl = new THREE.Mesh(new THREE.CylinderGeometry(1.45, 1.75, 2.6, 48), M.abutment); cyl.position.y = 1.3; cyl.castShadow = true;
      const cone = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 1.45, 1.0, 48), M.abutment); cone.position.y = 3.1;
      at.add(cyl, cone);
    } else if (top === 'ball') {
      const neck = new THREE.Mesh(new THREE.CylinderGeometry(1.0, 1.7, 2.4, 48), M.abutment); neck.position.y = 1.2; neck.castShadow = true;
      const ball = new THREE.Mesh(new THREE.SphereGeometry(1.25, 48, 32), M.abutment); ball.position.y = 3.0; ball.castShadow = true;
      at.add(neck, ball);
    }
    implants.add(at);
  }

  // tooth layout along the arch (incisor at centre)
  function addTeeth(group, yBase, list) {
    const widths = list.map(k => ({ M: 8.6, P: 6.6, C: 7.0, L: 5.6, I: 7.0 })[k]);
    const total = widths.reduce((a, b) => a + b, 0);
    const L = curve.getLength(), span = total / L, start = 0.5 - span / 2;
    let acc = 0;
    list.forEach((k, i) => {
      const t = THREE.MathUtils.clamp(start + (acc + widths[i] / 2) / L, 0.001, 0.999); acc += widths[i];
      const { C, T, O } = frame(curve, t);
      let g, mat = M.zirconia;
      if (k === 'M') g = crownGeometry({ seed: i, scale: 0.86 });
      else if (k === 'P') g = crownGeometry({ seed: i + 20, scale: 0.7, wide: 0.92 });
      else if (k === 'C') g = incisorGeometry({ w: 7.2, h: 8.8, d: 4.6, canine: true });
      else if (k === 'L') g = incisorGeometry({ w: 5.9, h: 7.8, d: 3.8 });
      else g = incisorGeometry({ w: 7.3, h: 8.8, d: 4.0 });
      const mesh = new THREE.Mesh(g, mat); mesh.castShadow = true; mesh.receiveShadow = true;
      const basis = new THREE.Matrix4().makeBasis(T, Y, O);
      mesh.quaternion.setFromRotationMatrix(basis);
      mesh.position.set(C.x, yBase, C.z);
      if (k === 'I' || k === 'L' || k === 'C') { mesh.position.addScaledVector(O, 0.1); mesh.rotateX(-0.1); }
      group.add(mesh);
    });
  }

  const flangeMat = new THREE.MeshPhysicalMaterial({ color: 0xe07e8a, roughness: 0.3, clearcoat: 0.8, clearcoatRoughness: 0.15, sheen: 0.5, sheenColor: new THREE.Color(0xffb8c1) });
  const lift = { allon4: 17, snap2: 17.5, snap4: 17.5 }[kind] || 17;
  if (kind === 'allon4') {
    addImplant(0.35, 0, 'mua'); addImplant(0.65, 0, 'mua');
    addImplant(0.19, 30, 'mua'); addImplant(0.81, 30, 'mua');
    const fl = new THREE.Mesh(sweep(curve, flangeSection, { t0: 0.07, t1: 0.93 }), flangeMat); fl.position.y = lift + 0.4; fl.castShadow = true; pros.add(fl);
    addTeeth(pros, lift - 0.6, ['M', 'P', 'P', 'C', 'L', 'I', 'I', 'L', 'C', 'P', 'P', 'M']);
  } else {
    const ts = kind === 'snap2' ? [0.36, 0.64] : [0.24, 0.41, 0.59, 0.76];
    ts.forEach(t => addImplant(t, 0, 'ball'));
    const db = new THREE.Mesh(sweep(curve, dentureSection, { t0: 0.04, t1: 0.96 }), flangeMat); db.position.y = lift; db.castShadow = true; pros.add(db);
    addTeeth(pros, lift - 0.4, ['M', 'P', 'P', 'C', 'L', 'I', 'I', 'L', 'C', 'P', 'P', 'M']);
  }

  const camera = new THREE.PerspectiveCamera(30, 4 / 3, 1, 500);
  const target = new THREE.Vector3(0, 3, -1);
  function apply(st) {
    const s = Object.assign({ az: 0.3, el: 0.5, dist: 122, lift: 1, ty: 7, tz: -2 }, st);
    pros.position.y = (s.lift - 1) * lift;
    target.set(0, s.ty, s.tz);
    camera.position.set(target.x + s.dist * Math.sin(s.az) * Math.cos(s.el), target.y + s.dist * Math.sin(s.el), target.z + s.dist * Math.cos(s.az) * Math.cos(s.el));
    camera.lookAt(target); camera.updateProjectionMatrix();
  }
  return { scene, camera, apply };
}
