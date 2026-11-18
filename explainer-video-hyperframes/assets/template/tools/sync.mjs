#!/usr/bin/env node
// Writes the voice's times into the HTML. HyperFrames reads plain numbers from `data-start` and
// `data-duration`; this tool computes them from the spoken words, so nobody types a time.
//
//   node tools/sync.mjs           update assets/vo/data.js, index.html and compositions/*.html
//   node tools/sync.mjs --check   change nothing; exit 1 when the HTML is behind the voice
//
// What it reads in the HTML:
//   data-at="<expression>"      film time at which the element starts      -> data-start
//   data-until="<expression>"   film time at which it ends                 -> data-duration
//   data-db="<number>"          level in decibels                          -> data-volume
//   <!-- voice:start --> ... <!-- voice:end -->   replaced by one <audio> per spoken part
//
// An expression is JavaScript with S, T, at and END in scope, for example:
//   data-at="T.picture"   data-until="T.close + 0.05"   data-at="at('First the voice') - 0.1"
// Use single quotes inside it. In a scene file the result is converted to that scene's own clock.
import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const ROOT = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const p = (...a) => path.join(ROOT, ...a);
const CHECK = process.argv.includes("--check");
const fail = (msg) => {
  console.error("FAILED: " + msg);
  process.exit(1);
};
const r3 = (n) => String(Math.round(n * 1000) / 1000);
const PY = process.platform === "win32" ? "python" : "python3";
// a text file as UTF-8, without the byte order mark some Windows editors put in front
const read = (file) => fs.readFileSync(file, "utf8").replace(/^\uFEFF/, "");

// ---- 1. script.json + words.json -> assets/vo/data.js (the browser may not fetch, so the data is a script)
const script = JSON.parse(read(p("script.json")));
const wordsFile = p("assets", "vo", "words.json");
if (!fs.existsSync(wordsFile)) fail(`No voice yet. Run: ${PY} tools/voice.py`);
const words = JSON.parse(read(wordsFile));
const dataJs =
  "// Written by tools/sync.mjs from script.json and assets/vo/words.json. Do not edit.\n" +
  "window.FILM_DATA = " + JSON.stringify({ script, words }) + ";\n";

// ---- 2. the same clock the scenes use
const ctx = vm.createContext({ console });
ctx.window = ctx;
try {
  vm.runInContext(dataJs, ctx);
  vm.runInContext(fs.readFileSync(p("lib", "clock.js"), "utf8"), ctx, { filename: "lib/clock.js" });
  vm.runInContext(fs.readFileSync(p("timeline.js"), "utf8"), ctx, { filename: "timeline.js" });
} catch (e) {
  fail(e.message);
}
const FILM = ctx.FILM;
const evalExpr = (expr, where) => {
  try {
    const v = vm.runInContext(`(function(){ const { S, T, at, END } = FILM; return (${expr}); })()`, ctx);
    if (typeof v !== "number" || !isFinite(v)) throw new Error("it does not give a number");
    return v;
  } catch (e) {
    fail(`${where}: "${expr}": ${e.message}`);
  }
};

// ---- 3. rewrite the attributes
const getAttr = (tag, name) => {
  const m = tag.match(new RegExp(`\\s${name}="([^"]*)"`));
  return m ? m[1] : null;
};
const setAttr = (tag, name, value, after) => {
  const re = new RegExp(`(\\s${name}=")[^"]*(")`);
  if (re.test(tag)) return tag.replace(re, `$1${value}$2`);
  const anchor = new RegExp(`(\\s${after}="[^"]*")`);
  return tag.replace(anchor, `$1 ${name}="${value}"`);
};
const lengths = {};
function mediaLength(file) {
  if (!(file in lengths)) {
    try {
      lengths[file] = Number(execFileSync("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file], { encoding: "utf8" }).trim()) || null;
    } catch {
      lengths[file] = null;
    }
  }
  return lengths[file];
}
const TAG = /<[a-zA-Z][\w-]*\s[^<>]*?\bdata-(?:at|until|db)="[^"]*"[^<>]*>/g;

function syncHtml(file, html) {
  const rel = path.relative(ROOT, file);
  let offset = 0;
  if (rel !== "index.html") {
    const id = (html.match(/data-composition-id="([^"]+)"/) || [])[1];
    if (!id) fail(`${rel}: no data-composition-id`);
    if (!(id in FILM.T)) fail(`${rel}: timeline.js has no T.${id}. Add the scene's start there.`);
    offset = FILM.T[id];
  }
  let n = 0;
  html = html.replace(TAG, (tag) => {
    let out = tag;
    const at = getAttr(tag, "data-at"), until = getAttr(tag, "data-until"), db = getAttr(tag, "data-db");
    let start = null;
    if (at !== null) {
      start = evalExpr(at, rel);
      if (start - offset < -0.0005) fail(`${rel}: data-at="${at}" is ${r3(start)} s, before its scene starts (${r3(offset)} s)`);
      out = setAttr(out, "data-start", r3(Math.max(0, start - offset)), "data-at");
    }
    if (until !== null) {
      if (start === null) start = Number(getAttr(tag, "data-start") || 0) + offset;
      const end = evalExpr(until, rel);
      if (end <= start) fail(`${rel}: data-until="${until}" (${r3(end)} s) is not after the start (${r3(start)} s)`);
      out = setAttr(out, "data-duration", r3(end - start), "data-until");
    }
    if (db !== null) out = setAttr(out, "data-volume", r3(FILM.db(Number(db))), "data-db");
    // a sound without an end plays its whole file: write that length, so lanes and checks see where it stops
    const src = getAttr(tag, "src");
    if (/^<audio\b/.test(tag) && at !== null && until === null && src) {
      const len = mediaLength(p(src));
      if (len) out = setAttr(out, "data-duration", r3(Math.min(len, Math.max(0.05, FILM.END - start))), "data-start");
    }
    if (out !== tag) n++;
    return out;
  });
  // the voice: one <audio> per spoken part
  const block = /([ \t]*)<!-- voice:start -->[\s\S]*?<!-- voice:end -->/;
  if (rel === "index.html" && block.test(html)) {
    html = html.replace(block, (_, ind) => {
      const lines = [];
      for (const v of FILM.VOICES) {
        const len = mediaLength(p(v.clips[0].src));
        v.clips.forEach((c, i) => {
          const dur = len ? Math.min(c.duration, len - c.mediaStart) : c.duration;
          lines.push(
            `${ind}<audio id="vo-${v.id}-${i + 1}" class="clip" src="${c.src}" data-start="${r3(c.start)}" data-duration="${r3(dur)}" data-media-start="${r3(c.mediaStart)}" data-volume="1" data-track-index="10"></audio>`,
          );
        });
      }
      return `${ind}<!-- voice:start -->\n${lines.join("\n")}\n${ind}<!-- voice:end -->`;
    });
  }
  return { html, n };
}

const files = [p("index.html")];
if (fs.existsSync(p("compositions"))) {
  for (const f of fs.readdirSync(p("compositions")).sort()) if (f.endsWith(".html")) files.push(p("compositions", f));
}
let changed = [];
const write = (file, next) => {
  const prev = fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "";
  if (prev === next) return;
  changed.push(path.relative(ROOT, file));
  if (!CHECK) fs.writeFileSync(file, next);
};
write(p("assets", "vo", "data.js"), dataJs);
for (const f of files) write(f, syncHtml(f, fs.readFileSync(f, "utf8")).html);

const mmss = (t) => `${Math.floor(t / 60)}:${(t % 60).toFixed(2).padStart(5, "0")}`;
console.log(`Film length ${mmss(FILM.END)} (${r3(FILM.END)} s)`);
for (const [k, v] of Object.entries(FILM.T)) console.log(`  scene ${k.padEnd(12)} starts ${mmss(v)}`);
if (CHECK) {
  if (changed.length) {
    console.error("Behind the voice: " + changed.join(", ") + ". Run: node tools/sync.mjs");
    process.exit(1);
  }
  console.log("ok  the HTML matches the voice");
} else {
  console.log(changed.length ? "Updated: " + changed.join(", ") : "Nothing to update.");
}
