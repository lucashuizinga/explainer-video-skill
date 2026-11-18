/* The film: sound first, then the shots from back to front. Every start and end is a time from the voice. */

import { useTicker } from "@diffusionstudio/jsx";
import { VOICES, T, END } from "./timeline";
import * as C from "./lib/brand";
import { rise } from "./lib/motion";
import { Layer, Picture, Sfx, Whip, Card } from "./lib/ui";
import { HOOK, PIC, hookSvg, pictureCam, pictureSvg, closeSvg } from "./scenes/demo";

/** The music bed from tools/mix_music.py, for example "music/bed.mp3". Leave empty until it exists. */
const MUSIC = "music/bed.mp3";
// @inspect number
const VOICE_DB = 0;
// @inspect number
const MUSIC_DB = 0;

export default function Film() {
  const { time } = useTicker();
  const t = () => time();
  return (
    <>
      {/* ---------- sound ---------- */}
      {VOICES.flatMap((v) => v.clips).map((c) => (
        <audio name="Voice" src={c.src} start={c.start} sourceIn={c.sourceIn} sourceOut={c.sourceOut} volume={VOICE_DB} id="voice1" />
      ))}
      {MUSIC ? <audio name="Music" src={MUSIC} start={0} end={END} volume={MUSIC_DB} id="music1" /> : null}
      <Sounds />

      {/* a flat colour under everything, so no frame is ever empty */}
      <Card from={0} to={END} />

      {/* ---------- 1. the idea ---------- */}
      <Layer from={0} to={T.picture + 0.05} svg={() => hookSvg(t())} name="1 the idea" />

      {/* ---------- 2. a picture with a camera ---------- */}
      <Picture name="Illustration" src="img/demo.jpg" from={T.picture} to={T.close + 0.05} cam={() => pictureCam(t())}
        opacity={() => rise(t(), T.picture, 0.4)} />
      <Layer from={T.picture} to={T.close + 0.05} svg={() => pictureSvg(t())} name="2 picture" />
      <Whip t={t} at={T.picture} />

      {/* ---------- 3. the close ---------- */}
      <Layer from={T.close} to={END} svg={() => closeSvg(t())} name="3 close" />
      <Whip t={t} at={T.close} color={C.ACCENT_2} />
    </>
  );
}

/** Sound effects hang on the same word times as the picture. */
function Sounds() {
  return (
    <>
      <Sfx src="sfx/pop.mp3" at={HOOK.title} db={-13} />
      <Sfx src="sfx/tick.mp3" at={HOOK.word} db={-15} />
      <Sfx src="sfx/pluck.mp3" at={HOOK.first} db={-14} />
      <Sfx src="sfx/pluck.mp3" at={HOOK.then} db={-14} />
      <Sfx src="sfx/pluck.mp3" at={HOOK.last} db={-14} />
      <Sfx src="sfx/whoosh.mp3" at={T.picture - 0.25} db={-13} />
      <Sfx src="sfx/pop.mp3" at={PIC.illustration} db={-15} />
      <Sfx src="sfx/pop.mp3" at={PIC.camera} db={-15} />
      <Sfx src="sfx/whoosh.mp3" at={T.close - 0.25} db={-13} />
      <Sfx src="sfx/chime.mp3" at={T.close + 0.35} db={-14} />
    </>
  );
}
