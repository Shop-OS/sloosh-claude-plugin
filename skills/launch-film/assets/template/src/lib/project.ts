import type { Cam } from "../components/Stage3D";

const rad = (d: number) => (d * Math.PI) / 180;

/** Projects a page-space point through <Plane3D cam> under <Stage3D perspective>. */
export const project = (cam: Cam, px: number, py: number, pz = 0, perspective = 1500) => {
  // translate target to origin
  let x = px - cam.tx;
  let y = py - cam.ty;
  let z = pz;
  // rotateZ
  const rz = rad(cam.rz);
  const x1 = x * Math.cos(rz) - y * Math.sin(rz);
  const y1 = x * Math.sin(rz) + y * Math.cos(rz);
  x = x1;
  y = y1;
  // rotateY
  const ry = rad(cam.ry ?? 0);
  const x2 = x * Math.cos(ry) + z * Math.sin(ry);
  const z2 = -x * Math.sin(ry) + z * Math.cos(ry);
  x = x2;
  z = z2;
  // rotateX
  const rx = rad(cam.rx);
  const y3 = y * Math.cos(rx) - z * Math.sin(rx);
  const z3 = y * Math.sin(rx) + z * Math.cos(rx);
  y = y3;
  z = z3;
  // translate3d
  const X = x + 960 + (cam.sx ?? 0);
  const Y = y + 540 + (cam.sy ?? 0);
  const Z = z + cam.z;
  const s = perspective / (perspective - Z);
  return { x: 960 + (X - 960) * s, y: 540 + (Y - 540) * s, scale: s };
};
