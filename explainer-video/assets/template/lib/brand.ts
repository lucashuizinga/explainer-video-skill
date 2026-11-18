// The brand: every colour and typeface in the film comes from here.
// Replace these with the company's real values (see references/brand.md in the skill). Keep the names:
// lib/draw.ts and lib/ui.tsx read them.

export const BG = "#f6f4ef"; // the page the film sits on
export const SURFACE = "#ffffff"; // cards and panels
export const INK = "#17202a"; // text and outlines
export const INK_SOFT = "#5b6673"; // secondary text
export const LINE = "#dfe3e8"; // hairlines
export const ACCENT = "#e4572e"; // the one brand colour that carries emphasis
export const ACCENT_2 = "#2f7f6f"; // a second brand colour, used sparingly
export const ACCENT_SOFT = "#fbe1d8"; // a tint of the accent for large quiet shapes
export const ON_ACCENT = "#ffffff"; // text on the accent

/** Display face for headlines and big words, body face for labels and small text. */
export const FONT_DISPLAY = "'Space Grotesk', 'Helvetica Neue', Arial, sans-serif";
export const FONT_BODY = "'Inter', 'Helvetica Neue', Arial, sans-serif";
/** Google Fonts stylesheet that loads both faces inside every shot. Empty string for system or installed fonts. */
export const GOOGLE_FONTS =
  "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@500;600;700&display=block";
/** Average glyph width of the display face as a fraction of the font size; used by `tw()` to size labels. */
export const GLYPH = 0.56;

export const W = 1920;
export const H = 1080;
