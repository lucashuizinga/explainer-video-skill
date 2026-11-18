// Small helpers on top of GSAP for the moves an explainer uses most. Each one adds tweens to the
// timeline you pass in; nothing here keeps its own clock.
(function () {
  const F = window.FILM;
  const E = F.ease;
  const el = (x) => (typeof x === "string" ? document.querySelector(x) : x);

  /**
   * Light up the words of a line as they are spoken.
   * `line` holds one <span class="w"> per spoken word, in order; `seg` is a segment (S.s1),
   * `phrase` its first words, `L` the scene's clock from FILM.local(id).
   */
  F.speak = function (tl, line, seg, phrase, L, o) {
    o = o || {};
    const i0 = seg.find(phrase);
    el(line).querySelectorAll(".w").forEach((w, i) => {
      tl.fromTo(w, { opacity: o.dim ?? 0.16 }, { opacity: 1, duration: o.duration ?? 0.16, ease: E.snappyOut }, L(seg.starts[i0 + i] - (o.lead ?? 0.04)));
    });
  };

  /** A camera view for an element with class "cam": zoom z around the point (px, py) of the picture. */
  F.view = (z, px = 960, py = 540) => ({ "--z": z, "--px": px, "--py": py });

  /**
   * A slow sway for holds: `prop` ("x", "y", "rotation") swings between -amp and +amp, one cycle per
   * `period` seconds, for the scene's `duration`. `t0` is the film time at the scene's start, so the
   * sway does not restart at a cut; `phase` shifts it (radians), to keep neighbours out of step.
   */
  F.sway = function (tl, target, prop, amp, period, duration, o) {
    o = o || {};
    const wave = (p) => Math.sin((((o.t0 || 0) + p * duration) / period) * Math.PI * 2 + (o.phase || 0));
    tl.fromTo(target, { [prop]: amp * wave(0) }, { [prop]: amp * wave(0) + amp, duration: duration, ease: (p) => wave(p) - wave(0) }, 0);
  };

  /**
   * A cut hidden by a coloured panel that crosses the frame. The scene that ends covers itself with
   * cutOut; the scene that starts opens with cutIn in the same colour. `target` is the .sweep inside a
   * timed .cut (see compositions/hook.html); `end` is the scene's own length in seconds.
   */
  F.cutOut = function (tl, target, end, dir) {
    tl.fromTo(target, { xPercent: 100 * (dir ?? 1) }, { xPercent: 0, duration: 0.26, ease: E.snappyIn }, end - 0.26);
  };
  F.cutIn = function (tl, target, dir) {
    tl.fromTo(target, { xPercent: 0 }, { xPercent: -100 * (dir ?? 1), duration: 0.26, ease: E.snappyOut }, 0);
  };

  /** Outline of a soft organic shape around (0,0); `wob` morphs it. */
  F.blobPath = function (r, seed, wob, k) {
    seed = seed || 0; wob = wob || 0; k = k ?? 0.13;
    const n = 56;
    let d = "";
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2;
      const rad = r * (1 + k * Math.sin(2 * a + seed) + k * 0.6 * Math.sin(3 * a + seed * 1.7 + wob) + k * 0.35 * Math.sin(5 * a + seed * 2.3 - wob * 1.3));
      d += (i ? "L" : "M") + (Math.cos(a) * rad).toFixed(1) + " " + (Math.sin(a) * rad * 0.86).toFixed(1);
    }
    return d + "Z";
  };

  /** A quiet shape that keeps changing while a picture holds. `path` is an SVG <path>; `t0` is the film time at the scene's start. */
  F.blob = function (tl, path, o) {
    const p = el(path), state = { w: (o.t0 || 0) * o.speed };
    const draw = () => p.setAttribute("d", F.blobPath(o.r, o.seed, state.w));
    draw();
    tl.to(state, { w: ((o.t0 || 0) + o.duration) * o.speed, duration: o.duration, ease: "none", onUpdate: draw }, 0);
  };
})();
