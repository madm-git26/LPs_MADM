// Marketing hero render: exploded single-tooth implant (ceramic crown / abutment with brand-blue collar /
// threaded titanium fixture) floating on black, white key light + brand-blue rim lights, glowing ring.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { implantGeometry } from './pnw3d.js';
import { molarGeometry } from './realistic.js';

const BLUE = 0x0397d6, BLUE_LIGHT = 0x2fb2ec;

export function buildHero(renderer, { W = 1400, H = 1500 } = {}) {
  renderer.toneMapping = THREE.NeutralToneMapping; renderer.toneMappingExposure = 1.0;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.setClearColor(0x000000, 1);
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000000);
  const pm = new THREE.PMREMGenerator(renderer);
  scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture; scene.environmentIntensity = 0.32;

  const M = {
    enamel: new THREE.MeshPhysicalMaterial({ vertexColors: true, color: 0xffffff, roughness: 0.2, clearcoat: 1, clearcoatRoughness: 0.06, sheen: 0.25, sheenColor: new THREE.Color(0xeaf6ff), specularIntensity: 0.9 }),
    titanium: new THREE.MeshPhysicalMaterial({ color: 0xcfd6de, metalness: 1, roughness: 0.24, envMapIntensity: 3.2 }),
    blue: new THREE.MeshPhysicalMaterial({ color: BLUE, metalness: 0.75, roughness: 0.22, clearcoat: 0.8, clearcoatRoughness: 0.1, envMapIntensity: 1.4 }),
    ring: new THREE.MeshBasicMaterial({ color: new THREE.Color(BLUE_LIGHT).multiplyScalar(2.2), toneMapped: false }),
    ringSoft: new THREE.MeshBasicMaterial({ color: new THREE.Color(BLUE_LIGHT).multiplyScalar(1.2), toneMapped: false, transparent: true, opacity: 0.55 }),
  };

  const key = new THREE.DirectionalLight(0xffffff, 1.35); key.position.set(-18, 22, 30); scene.add(key);
  const fill = new THREE.DirectionalLight(0xdfefff, 0.85); fill.position.set(24, 6, 26); scene.add(fill);
  const rimL = new THREE.DirectionalLight(BLUE_LIGHT, 5.5); rimL.position.set(-26, 8, -24); scene.add(rimL);
  const rimR = new THREE.DirectionalLight(BLUE_LIGHT, 6.5); rimR.position.set(28, 12, -22); scene.add(rimR);
  const top = new THREE.DirectionalLight(0xffffff, 0.55); top.position.set(0, 40, -4); scene.add(top);

  const asm = new THREE.Group(); scene.add(asm);
  // fixture: platform at y = 0, apex at y = -10
  const fixture = new THREE.Mesh(implantGeometry({ L: 10, segU: 160, segV: 620 }), M.titanium); asm.add(fixture);
  const cap = new THREE.Mesh(new THREE.CircleGeometry(1.8, 64).rotateX(-Math.PI / 2), M.titanium); asm.add(cap);
  const hex = new THREE.Mesh(new THREE.CylinderGeometry(0.75, 0.75, 0.12, 6), new THREE.MeshStandardMaterial({ color: 0x20262c, metalness: 0.7, roughness: 0.5 })); hex.position.y = 0.02; asm.add(hex);

  // abutment, lifted above the fixture
  const ab = new THREE.Group(); asm.add(ab);
  const conn = new THREE.Mesh(new THREE.CylinderGeometry(0.72, 0.72, 1.3, 6), M.titanium); conn.position.y = -0.55;
  const collar = new THREE.Mesh(new THREE.CylinderGeometry(1.95, 1.75, 1.4, 64), M.blue); collar.position.y = 0.7;
  const bevel = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.95, 0.45, 64), M.titanium); bevel.position.y = 1.62;
  const post = new THREE.Mesh(new THREE.CylinderGeometry(1.05, 1.45, 4.0, 64), M.titanium); post.position.y = 3.85;
  const flat = new THREE.Mesh(new THREE.BoxGeometry(0.9, 3.4, 0.25), M.titanium); flat.position.set(0, 3.8, 1.18);
  [conn, collar, bevel, post].forEach(o => ab.add(o));
  ab.position.y = 3.2;

  // crown, lifted above the abutment
  const cg = molarGeometry({ seed: 3, scale: 1.04 });
  cg.computeBoundingBox();
  const crown = new THREE.Mesh(cg, M.enamel);
  const cb = cg.boundingBox;
  crown.position.set(-(cb.min.x + cb.max.x) / 2, 0, -(cb.min.z + cb.max.z) / 2);
  const crownG = new THREE.Group(); crownG.add(crown); asm.add(crownG);
  crownG.position.y = 3.2 + 5.85 + 2.9 - cb.min.y;
  crownG.rotation.y = 0.5;

  // glowing orbit rings
  const ringA = new THREE.Mesh(new THREE.TorusGeometry(4.6, 0.045, 12, 240), M.ring);
  ringA.rotation.x = Math.PI / 2 - 0.28; ringA.position.y = 0.4; asm.add(ringA);
  const ringB = new THREE.Mesh(new THREE.TorusGeometry(6.4, 0.025, 10, 240, Math.PI * 1.25), M.ringSoft);
  ringB.rotation.x = Math.PI / 2 - 0.28; ringB.rotation.z = 0.9; ringB.position.y = 0.4; asm.add(ringB);

  const box = new THREE.Box3(), center = new THREE.Vector3();
  const camera = new THREE.PerspectiveCamera(22, W / H, 1, 800);
  const view = { az: 0.25, el: 0.3, dist: 96, fov: 22, tilt: -0.1, dy: 0 };
  const target = new THREE.Vector3();

  const composer = new EffectComposer(renderer);
  composer.setSize(W, H);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(W, H), 0.32, 0.35, 0.96); composer.addPass(bloom);
  composer.addPass(new OutputPass());

  function apply(st = {}) {
    const v = Object.assign({}, view, st);
    asm.rotation.z = v.tilt; asm.updateMatrixWorld(true);
    box.setFromObject(asm).getCenter(center); v.ty = center.y + v.dy;
    camera.fov = v.fov; target.set(center.x, v.ty, 0);
    camera.position.set(center.x + v.dist * Math.sin(v.az) * Math.cos(v.el), v.ty + v.dist * Math.sin(v.el), v.dist * Math.cos(v.az) * Math.cos(v.el));
    camera.lookAt(target); camera.updateProjectionMatrix();
    if (st.bloom != null) bloom.strength = st.bloom;
  }
  apply();
  return { scene, camera, apply, render: () => composer.render() };
}
