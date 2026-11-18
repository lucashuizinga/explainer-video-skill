# Skills voor uitlegvideo's

Twee skills voor Claude Code die een ingesproken, geanimeerde uitlegvideo maken in de huisstijl van een bedrijf. De werkwijze is in beide gelijk: eerst de stem, en daarna hangt elke beweging aan een gesproken woord. Ze verschillen in het programma dat de beelden maakt en in waar stem, beeld en muziek vandaan komen.

| Skill | Maakt de beelden met | Stem, beeld en muziek via | Draait op |
| --- | --- | --- | --- |
| `explainer-video` | Diffusion Studio | Een key van ElevenLabs en een key van Gemini | Een Mac met de app Diffusion Studio |
| `explainer-video-hyperframes` | HyperFrames (HTML naar video) | Eén key van OpenRouter | Mac, Windows en Linux |

## Wat je aanlevert

1. Waar de video over gaat, met het bronmateriaal waar de feiten uit komen.
2. Het merk: naam en website, en als je ze hebt een logobestand en de kleuren.
3. De keys:
   - `explainer-video`: een API key van ElevenLabs en een API key van Gemini.
   - `explainer-video-hyperframes`: één API key van OpenRouter.

De OpenRouter-key gebruikt vier modellen: `elevenlabs/eleven-v4` (stem), `elevenlabs/scribe-v2` (woordtijden), `google/gemini-nano-banana-2.1` (illustraties) en `google/lyria-3-pro-preview` (muziek). Is de key beperkt tot bepaalde modellen, dan moeten deze vier zijn toegestaan. Op het account moet minstens $0,50 staan, anders weigert OpenRouter stem en muziek.

## Wat er op de computer moet staan

Voor beide: `ffmpeg` en Python 3.9 of nieuwer.

- `explainer-video`: macOS met de app Diffusion Studio en het commando `dapi`. Deze skill werkt niet op Windows.
- `explainer-video-hyperframes`: Node.js 22 of nieuwer en de skills van HyperFrames. Geef iemand met Windows alleen deze skill.

Je hoeft dit niet vooraf te regelen. De HyperFrames-skill kijkt eerst wat er op de computer staat, vertelt wat er ontbreekt en helpt met installeren. Claude vraagt één keer of het de programma's mag installeren. De skills van HyperFrames installeert de gebruiker zelf met één opdracht. Daarna sluit je Claude Code, open je het opnieuw en ga je verder.

| Wat | Windows | Mac |
| --- | --- | --- |
| Node.js | `winget install OpenJS.NodeJS.LTS` | `brew install node` |
| Python | `winget install Python.Python.3.12` | staat er meestal al, anders `brew install python` |
| ffmpeg | `winget install Gyan.FFmpeg` | `brew install ffmpeg` |
| Skills van HyperFrames | `npx hyperframes skills` | `npx hyperframes skills` |

Op Windows heet Python `python` of `py -3`, niet `python3`. De skill weet dat. Meer staat in `references/setup.md` van de skill.

## Installeren

Zet de map van de skill in `~/.claude/skills/`:

```sh
cp -R explainer-video ~/.claude/skills/explainer-video
cp -R explainer-video-hyperframes ~/.claude/skills/explainer-video-hyperframes
```

Op Windows is dat de map `.claude\skills` in je gebruikersmap, bijvoorbeeld `C:\Users\jouwnaam\.claude\skills\explainer-video-hyperframes`.

Of installeer het bestand `explainer-video.skill` of `explainer-video-hyperframes.skill` vanuit Claude. Beide bestanden staan in deze repo.

## Gebruiken

Start Claude Code en vraag bijvoorbeeld:

> Maak een uitlegvideo van anderhalve minuut over hoe ons klantportaal werkt, voor nieuwe klanten. Merk: Voorbeeld BV, voorbeeld.nl. De uitleg staat in docs/portaal.md.

Wil je de versie op HyperFrames, zeg dat er dan bij ("met HyperFrames" of "met mijn OpenRouter-key"). Claude vraagt om de keys als ze er nog niet zijn, zet ze in het bestand `.env` van het project en begint. De keys komen nergens anders terecht.

## Wat erin zit

| Onderdeel | Inhoud |
| --- | --- |
| `SKILL.md` | De werkwijze in acht stappen en de regels die de video goed maken |
| `references/` | Naslag over installatie, merk, script en stem, beelden, scènes, geluid en valkuilen |
| `scripts/new_project.py` | Maakt een nieuw videoproject vanuit het sjabloon |
| `assets/template/` | Het sjabloon: een klein werkend filmpje, de bibliotheek voor timing, twaalf geluidseffecten en het gereedschap in `tools/` |

## Wat anders is met OpenRouter

- **Woordtijden.** De stem komt als geluid terug, zonder tijden. Het gereedschap laat de opname daarna uitschrijven door Scribe v2 en legt de gehoorde woorden naast de geschreven woorden. Waar die verschillen, meldt het dat.
- **Stemmen.** Je kiest uit 21 vaste stemmen op naam. Ze hebben geen taal of omschrijving, dus een stem beoordeel je op een korte proefopname.
- **Muziek.** Lyria bepaalt zelf de lengte en de opbouw. Het gereedschap vraagt een langer stuk en snijdt de lengte van de film eruit. Muziek die meebeweegt met de hoofdstukken van de film kan hiermee niet.
- **Geluidseffecten.** OpenRouter heeft geen model dat effecten maakt. De skill gebruikt de twaalf meegeleverde effecten.

Het sjabloon rendert direct na het aanmaken, zonder dat het iets kost. Zo zie je meteen of een nieuwe computer goed is ingericht.

## Wat is getest

Op 17 en 18 november 2026, op een Mac. Op Windows en Linux is niets getest.

`explainer-video` (dapi 0.211.0):

- Een nieuw project aanmaken, de controle draaien en het demofilmpje renderen en exporteren.
- De stem genereren met Eleven v4, met woordtijden.
- Een illustratie genereren met `gemini-3-pro-image` op 4K.
- Muziek genereren met een indeling in secties, en het volume automatisch onder de stem leggen.
- Een nieuw geluidseffect genereren.

`explainer-video-hyperframes` (HyperFrames 0.9.64, alles via OpenRouter):

- Een nieuw project aanmaken, de controle draaien, beelden bekijken en het demofilmpje renderen.
- De controle herkent de key, de vier modellen, de limiet en het saldo.
- De stem genereren met Eleven v4 en de woordtijden ophalen met Scribe v2, in het Engels en het Nederlands. In de Nederlandse test werden "30", "1" en "5" aan "dertig", "één" en "vijf" gekoppeld.
- Een illustratie genereren met Nano Banana 2.1 op 4K, ook met een beeld als voorbeeld.
- Muziek genereren met Lyria 3 Pro, op lengte snijden en onder de stem leggen.
- De demofilm in het sjabloon is zo opnieuw gemaakt: stem, woordtijden en muziek via OpenRouter. De controle van HyperFrames geeft geen fouten en geen waarschuwingen, en de film staat op -15,0 LUFS.
- De recepten uit de naslag voor een teller, een balk die vult en een onthulling door een vorm.
- Een hele video van 72 seconden in het Nederlands, van script tot render. Die kostte $0,17 aan stem en muziek.
- Het gereedschap is geschikt gemaakt voor Windows: tekst gaat overal als UTF-8, de aanwijzingen noemen het juiste Python-commando en `npx` wordt als `npx.cmd` gevonden. Dat is op de Mac getest onder een instelling zonder UTF-8, met een mapnaam met een accent en met een bestand dat met een BOM begint. Een proef op een echte Windows-computer is nog niet gedaan.

Nog niet getest: een hele video laten maken door een nieuwe Claude-sessie die alleen een van deze skills heeft. De versie voor HyperFrames op Linux. En een lange video met tien of meer illustraties in één stijl via Nano Banana 2.1.

## Licentie

MIT, zie `LICENSE`. Het lettertype Space Grotesk in het sjabloon valt onder de SIL Open Font License.
