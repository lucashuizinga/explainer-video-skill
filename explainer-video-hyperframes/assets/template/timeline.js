// The timeline. The voice is the clock: every time in the film is looked up from a spoken word.
// FILM_DATA (assets/vo/data.js) is script.json plus the word times, written by tools/sync.mjs.
window.FILM = Clock.build(FILM_DATA.script, FILM_DATA.words);

// ---------------------------------------------------------------------------------------------
// Where each scene starts. A scene starts a little before its first word, so the picture is there
// when the voice begins. One entry per scene file, named after its id. Edit this block for your
// film, then run: node tools/sync.mjs
// ---------------------------------------------------------------------------------------------
(function () {
  const { S, T } = FILM;
  T.hook = 0;
  T.picture = S.s2.t0 - 0.5;
  T.close = S.s3.t0 - 0.5;
})();
