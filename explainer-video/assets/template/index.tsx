/* An explainer video: one scene, voiced with ElevenLabs Eleven v4. Keep it to one <scene> per project. */

import Film from "./film";
import { BG } from "./lib/brand";

export default function Project() {
  return (
    <stage background="#e9e9e9" camera={[0.4, 0, 0, 0.4, 80, 120]} id="stage1">
      <scene id="film" name="Explainer video" width={1920} height={1080} fill={BG} active>
        <Film />
      </scene>
    </stage>
  );
}
