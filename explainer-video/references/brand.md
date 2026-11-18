# Brand

The film should look like it came from the client. All of that lives in `lib/brand.ts`: change the values
there and every shot follows.

## What to collect

1. **Colours.** The primary brand colour, a secondary one if they use it, and their neutrals (page
   background, text). Take exact hex values from the website's CSS, a brand guide or the logo file. Do not
   eyeball them from a screenshot if the real values are available.
2. **Typefaces.** The headline and body faces. If they are on Google Fonts, put the stylesheet URL in
   `GOOGLE_FONTS`. If they are proprietary (many brand fonts are), pick the closest Google Font or a system
   font and tell the user which one you used and why.
3. **Logo.** Ask for an SVG or a large PNG. Put the file in `assets/img/` and show it with an `<image>` in
   the closing shot. Only redraw a logo in vector when it is very simple and no file is available, and say
   that it is a redraw so the user can replace it.
4. **A brand device.** One shape or habit that recurs in their identity: a label, a rounded block, a
   blob, a line weight, a corner. Use it as the film's own motif (for emphasis, for transitions, for the
   quiet shape that moves during holds). This is what makes the film feel designed rather than themed.
5. **Tone.** How they talk: formal or plain, "you" or "we". The script follows it.

## Where to find it

- The user's own files first: a brand guide, a logo, an existing deck.
- The website: fetch the homepage and its stylesheet, look for CSS variables and font declarations, and
  for the logo in the header.
- If you cannot find something, ask one short question. Do not make up a brand colour.

## Filling in `lib/brand.ts`

| Name | Use |
| --- | --- |
| `BG` | The page the film sits on. Usually the brand's lightest neutral, not pure white. |
| `SURFACE` | Cards and panels on top of `BG`. |
| `INK`, `INK_SOFT` | Text and outlines; secondary text. |
| `LINE` | Hairlines and empty tracks. |
| `ACCENT` | The one colour that carries emphasis. Usually the primary brand colour. |
| `ACCENT_2` | A second brand colour, used sparingly (a different kind of thing, a second voice). |
| `ACCENT_SOFT` | A light tint of the accent for large quiet shapes. |
| `ON_ACCENT` | Text on the accent. Check that it is readable. |
| `FONT_DISPLAY`, `FONT_BODY` | Font stacks, each with real fallbacks. |
| `GOOGLE_FONTS` | The stylesheet that loads them inside every shot, or `""`. Use `display=block`. |
| `GLYPH` | Average letter width of the display face as a fraction of its size. `tw()` uses it to size labels. |

Add more named colours if the brand has them. Keep the existing names, because `lib/draw.ts` and
`lib/ui.tsx` read them.

After changing the display face, capture a frame with a label on it. If the label's box is too wide or
too tight for its text, adjust `GLYPH` (wider faces around 0.6, condensed ones around 0.5).

## Check

- Text on `BG`, on `SURFACE` and on `ACCENT` is all clearly readable.
- The accent appears a few times per shot at most.
- The first and last shots would be recognised as this client's without the logo.
