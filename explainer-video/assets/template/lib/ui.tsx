// Small JSX building blocks. JSX files must live inside the project folder.

import { W, H, ACCENT, BG, GOOGLE_FONTS } from "./brand";
import { prog, lerp, snappyIn, snappyOut } from "./motion";
import { imgBox } from "./draw";
import type { Cam } from "./draw";

/** One shot: an SVG string, recomputed every frame from the playhead. */
export function Layer(props: { from: number; to: number; svg: () => string; name?: string }) {
  return (
    <html start={props.from} end={props.to} x={0} y={0} width={W} height={H} name={props.name} id="lyr001">
      {GOOGLE_FONTS ? <link rel="stylesheet" href={GOOGLE_FONTS} /> : null}
      <div style="width:1920px;height:1080px;" innerHTML={props.svg()} />
    </html>
  );
}

/** A full-frame illustration seen through a camera. Give its overlay Layer the same camera. */
export function Picture(props: { src: string; from: number; to: number; cam: () => Cam; opacity?: () => number; name?: string }) {
  return (
    <image name={props.name} src={props.src} start={props.from} end={props.to}
      x={imgBox(props.cam()).x} y={imgBox(props.cam()).y} width={imgBox(props.cam()).width} height={imgBox(props.cam()).height}
      opacity={props.opacity ? props.opacity() : 1} id="pic001" />
  );
}

/** A sound effect at a moment in the film, level in dB. */
export function Sfx(props: { src: string; at: number; db: number }) {
  return <audio src={props.src} start={Math.max(0, props.at)} volume={props.db} id="sfx001" />;
}

/** A coloured panel that sweeps across the frame to hide a cut at `at`. */
export function Whip(props: { t: () => number; at: number; color?: string; dir?: 1 | -1 }) {
  const a = props.at - 0.26;
  const d = props.dir ?? 1;
  const p = () => prog(props.t(), a, 0.52);
  const x = () => d * (p() < 0.5 ? lerp(W, 0, snappyIn(p() * 2)) : lerp(0, -W, snappyOut((p() - 0.5) * 2)));
  return <rect start={a} end={a + 0.52} x={x()} y={0} width={W} height={H} fill={props.color ?? ACCENT} id="whp001" />;
}

/** A flat colour behind a stretch of time, so no frame is ever empty. */
export function Card(props: { from: number; to: number; fill?: string }) {
  return <rect start={props.from} end={props.to} width={W} height={H} fill={props.fill ?? BG} id="crd001" />;
}
