# Pictures

Illustrations are generated with Google's Gemini image model through `tools/image.py`, on the user's own
`GEMINI_API_KEY`. Do not use `dapi generate`: that bills someone else's Diffusion Studio credits.

## Vector or illustration?

| Draw it in vector (`lib/draw.ts`) | Generate an illustration |
| --- | --- |
| Words, numbers, counters | People and faces |
| Charts, scales, bars, timelines | Places: a room, a street, a city |
| Simple icons, dots, arrows, labels | Bodies, organs, anything anatomical |
| Diagrams of steps and flows | Objects that should feel real |
| The brand device and the logo | Atmosphere for an opening or a close |

The rule behind the table: things from the real world drawn as SVG with thick outlines look amateurish.
A client said it of hand-drawn lungs: either really good, or zoomed out so the odd strokes are not
visible. So a real thing is either a proper illustration or small and far away. Vector stays for what is
abstract.

The two work together: the illustration is the world, and vector labels, arrows and highlights ride on
top of it with the same camera (`Picture` plus a `Layer`, see `references/shots.md`).

## One style for the whole film

Write a style paragraph once and paste it in front of every prompt, unchanged:

> Flat editorial illustration, soft daylight, gentle shadows, a limited palette of warm coral, deep teal
> and cream, clean simple shapes, calm composition with open space. No text, no letters, no numbers, no
> logos.

Take the palette words from the brand. Then generate the first picture, look at it, and when it is right
use it as a reference for all the others so they share a hand:

```sh
python3 tools/image.py assets/img/01-office.png "<style> A quiet office at dusk, one person at a desk on the phone, seen from the doorway."
python3 tools/image.py assets/img/02-classroom.png "<style> A classroom, a teacher talking with one student at a desk. Same style as the reference." --ref assets/img/01-office.jpg
```

`image.py` saves in the format the API returns (usually `.jpg`) and prints the final path and pixel size.
Use that path afterwards.

## Prompts that work for film

- **Say where the camera will go.** "Wide view, the desk in the lower left, empty wall on the right."
  Leave calm, empty areas where labels will sit.
- **Keep the subject away from the edges.** A push-in crops the frame.
- **Always end with** "No text, no letters, no numbers, no logos." Generated lettering is garbled, and
  real text belongs in vector on top.
- **Describe an ordinary situation plainly.** Who, where, doing what, in what light.
- **People:** natural, varied, unposed. Never a real, named person.

## Size and the camera

The default is 4K, which comes back around 5500 pixels wide. That is what lets you zoom.

- A picture can be zoomed until `zoom x 1920` reaches its pixel width. A 3840 wide picture is sharp up to
  zoom 2.
- `image.py` scales every picture down to 3840 wide, which keeps the project light. Pass `--full` to keep
  the full size for a shot that zooms further than 2.
- Check the size `image.py` prints. If a picture is narrower than expected, lower the zoom on it or
  generate it again. Never upscale by stretching.

## Look at every picture

Open each one at full size (the Read tool shows images) before it goes into a shot. Look for:

- Garbled text, signs, screens, book spines.
- Clocks, calendars and dials showing something wrong for the story.
- Hands, faces, eyes; extra or missing limbs.
- Anything that could read as harm or distress: something around a neck, a threatening shape, a body in
  an odd position.

Fix by regenerating, by editing the picture with itself as the reference ("the same image, but the clock
on the wall is removed"), or by framing the camera so the problem is out of shot.

## Dignity

Keep pictures calm and literal. No metaphors that show a person being harmed, tied, pulled or pressed. A
film that opened with threads around people's throats to show "pressure" was rejected by the client as
bizarre and unusable. If you want to show stress, show the situation: a full inbox, a late evening, a
phone that keeps ringing.

## A thing that changes state

For healthy and ill, before and after, day and night: generate the first state, then make the second by
editing the first with itself as the reference.

```sh
python3 tools/image.py assets/img/liver-fatty.png "The same illustration, same outline and position, but the liver is pale and yellowish with fat." --ref assets/img/liver-healthy.jpg
```

The outlines then match, and a cross-fade between the two (two `Picture`s with opposite opacity) reads as
one thing changing rather than two pictures.

## A round lens

To show a detail as a circular inset, place an `<image>` with a corner radius of half its size. Read the
radius inside the JSX expression if it animates (see `references/pitfalls.md`).

## Moving clips

This skill does not generate video clips. Stills with a camera move, an overlay and good sound carry an
explainer. If the user supplies a clip, a `<video>` tag plays it; it has no playback rate, so slow a clip
down with ffmpeg before you use it.
