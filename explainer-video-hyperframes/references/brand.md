# Brand

The film should look like it came from the client. All of that lives in one place: the brand block in the
`<style>` of `index.html`. Change the values there and every scene follows, because scenes only use the
variables (`var(--accent)`, `var(--font-display)`).

## What to collect

1. **Colours.** The primary brand colour, a secondary one if they use it, and their neutrals (page
   background, text). Take exact hex values from the website's CSS, a brand guide or the logo file. Do not
   eyeball them from a screenshot if the real values are available.
2. **Typefaces.** The headline and body faces. See "Fonts" below. If they are proprietary and you have no
   file, pick the closest Google Font and tell the user which one you used and why.
3. **Logo.** Ask for an SVG or a large PNG. Put the file in `assets/img/` and show it with an `<img>` in
   the closing scene. Only redraw a logo in vector when it is very simple and no file is available, and
   say that it is a redraw so the user can replace it.
4. **A brand device.** One shape or habit that recurs in their identity: a label, a rounded block, a
   blob, a line weight, a corner. Use it as the film's own motif (for emphasis, for transitions, for the
   quiet shape that moves during holds). This is what makes the film feel designed rather than themed.
5. **Tone.** How they talk: formal or plain, "you" or "we". The script follows it.

## Where to find it

- The user's own files first: a brand guide, a logo, an existing deck.
- The website: fetch the homepage and its stylesheet, look for CSS variables and font declarations, and
  for the logo in the header. `npx hyperframes capture <url> --json` collects a site's colours, fonts and
  assets into a folder you can read from; take values from it, do not build the film on its scaffold.
- If you cannot find something, ask one short question. Do not make up a brand colour.

## The brand block

| Variable | Use |
| --- | --- |
| `--bg` | The page the film sits on. Usually the brand's lightest neutral, not pure white. |
| `--surface` | Cards and panels on top of `--bg`. |
| `--ink`, `--ink-soft` | Text and outlines; secondary text. |
| `--line` | Hairlines and empty tracks. |
| `--accent` | The one colour that carries emphasis. Usually the primary brand colour. |
| `--accent-2` | A second brand colour, used sparingly (a different kind of thing, a second voice). |
| `--accent-soft` | A light tint of the accent for large quiet shapes. |
| `--on-accent` | Text on the accent. Check that it is readable. |
| `--font-display`, `--font-body` | Font stacks, each with real fallbacks. |

Add more named colours if the brand has them. Keep the existing names: the building blocks (`.label`,
`.panel`, `.sweep`) read them.

## Fonts

HyperFrames resolves only its bundled families by name: Inter, Montserrat, Outfit, Nunito, Oswald,
League Gothic, Archivo Black, Space Mono, IBM Plex Mono, JetBrains Mono, EB Garamond, Playfair Display,
Source Code Pro, Noto Sans JP, Roboto, Open Sans, Lato, Poppins. Any other family needs a font file in
the project and an `@font-face` rule, or it silently renders in a fallback.

```sh
python3 tools/font.py "Space Grotesk"            # downloads it from Google Fonts and declares it
python3 tools/font.py "Fraunces" 400,700 --italic
```

The tool saves the files in `assets/fonts/` and writes the rules between `/* fonts:start */` and
`/* fonts:end */` in `index.html`. Then name the family in `--font-display` or `--font-body`.

A brand font that is not on Google Fonts: put its `.woff2` in `assets/fonts/` and write the `@font-face`
rule in that block by hand. Only use a font the client is licensed to use.

Text is laid out by a real browser, so labels and panels fit their text without guessing widths. A long
line still has to fit the frame: look at a snapshot.

## Check

- Text on `--bg`, on `--surface` and on `--accent` is all clearly readable. `npx hyperframes check`
  measures contrast and suggests a colour when it fails.
- The accent appears a few times per scene at most.
- The first and last scenes would be recognised as this client's without the logo.
