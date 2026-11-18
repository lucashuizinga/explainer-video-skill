# Skill voor uitlegvideo's

Een skill voor Claude Code die een ingesproken, geanimeerde uitlegvideo maakt in de huisstijl van een bedrijf. Eerst komt de stem. Daarna hangt elke beweging aan een gesproken woord, zodat beeld en stem gelijk lopen.

De skill heet `explainer-video-hyperframes`. De beelden maakt hij met HyperFrames (HTML naar video). Stem, illustraties en muziek komen via één API key van OpenRouter. Hij draait op Mac, Windows en Linux.

## Wat je aanlevert

1. Waar de video over gaat, met het bronmateriaal waar de feiten uit komen.
2. Het merk: naam en website, en als je ze hebt een logobestand en de kleuren.
3. Eén API key van OpenRouter (openrouter.ai).

## De OpenRouter-key

De key gebruikt vier modellen:

| Voor | Model |
| --- | --- |
| De stem | `elevenlabs/eleven-v4` |
| De tijd van elk woord | `elevenlabs/scribe-v2` |
| Illustraties | `google/gemini-nano-banana-2.1` |
| Muziek | `google/lyria-3-pro-preview` |

Zo stel je de key veilig in op openrouter.ai:

- **Guardrails.** Sta alleen deze vier modellen toe. Een ander model zet je er later met één klik bij.
- **Limiet.** Zet een limiet op de key, bijvoorbeeld 50 of 100 dollar. Dat kan ook per dag.
- **Einddatum.** Laat de key verlopen, bijvoorbeeld na vier of zeven dagen. Daarna werkt hij niet meer.
- **Saldo.** Op het account moet minstens $0,50 staan, anders weigert OpenRouter stem en muziek.

Een video van ruim een minuut kostte in onze test $0,17 aan stem en muziek. Een illustratie op 4K kost ongeveer $0,12.

## Installeren

Download `explainer-video-hyperframes.skill` uit deze repo en installeer het bestand vanuit Claude. Of zet de map van de skill in `~/.claude/skills/`:

```sh
cp -R explainer-video-hyperframes ~/.claude/skills/explainer-video-hyperframes
```

Op Windows is dat de map `.claude\skills` in je gebruikersmap, bijvoorbeeld `C:\Users\jouwnaam\.claude\skills\explainer-video-hyperframes`.

## Wat er op de computer moet staan

Node.js 22 of nieuwer, Python 3.9 of nieuwer, `ffmpeg` en de skills van HyperFrames.

Je hoeft dit niet vooraf te regelen. De skill kijkt eerst wat er op de computer staat, vertelt wat er ontbreekt en helpt met installeren. Claude vraagt één keer of het de programma's mag installeren. De skills van HyperFrames installeer je zelf met één opdracht. Daarna sluit je Claude Code, open je het opnieuw en ga je verder.

| Wat | Windows | Mac |
| --- | --- | --- |
| Node.js | `winget install OpenJS.NodeJS.LTS` | `brew install node` |
| Python | `winget install Python.Python.3.12` | staat er meestal al, anders `brew install python` |
| ffmpeg | `winget install Gyan.FFmpeg` | `brew install ffmpeg` |
| Skills van HyperFrames | `npx hyperframes skills` | `npx hyperframes skills` |

Op Windows heet Python `python` of `py -3`, niet `python3`. De skill weet dat. Meer staat in `references/setup.md` van de skill.

## Gebruiken

Start Claude Code en vraag bijvoorbeeld:

> Maak een uitlegvideo van anderhalve minuut over hoe ons klantportaal werkt, voor nieuwe klanten. Merk: Voorbeeld BV, voorbeeld.nl. De uitleg staat in docs/portaal.md.

Claude vraagt om de key als die er nog niet is, zet hem in het bestand `.env` van het project en begint. De key komt nergens anders terecht. Je krijgt een mp4 en een projectmap die je kunt openen en aanpassen.

## Wat erin zit

| Onderdeel | Inhoud |
| --- | --- |
| `SKILL.md` | De werkwijze in stappen en de regels die de video goed maken |
| `references/` | Naslag over installatie, merk, script en stem, beelden, scènes, geluid en valkuilen |
| `scripts/new_project.py` | Maakt een nieuw videoproject vanuit het sjabloon |
| `assets/template/` | Het sjabloon: een klein werkend filmpje, de bibliotheek voor timing, twaalf geluidseffecten en het gereedschap in `tools/` |

Het sjabloon rendert direct na het aanmaken, zonder dat het iets kost. Zo zie je meteen of een nieuwe computer goed is ingericht.

## Goed om te weten

- **Woordtijden.** De stem komt als geluid terug, zonder tijden. Het gereedschap laat de opname daarna uitschrijven door Scribe v2 en legt de gehoorde woorden naast de geschreven woorden. Waar die verschillen, meldt het dat.
- **Stemmen.** Je kiest uit 21 vaste stemmen op naam. Ze hebben geen taal of omschrijving, dus een stem beoordeel je op een korte proefopname.
- **Muziek.** Lyria bepaalt zelf de lengte en de opbouw. Het gereedschap vraagt een langer stuk en snijdt de lengte van de film eruit. Muziek die meebeweegt met de hoofdstukken van de film kan hiermee niet.
- **Geluidseffecten.** OpenRouter heeft geen model dat effecten maakt. De skill gebruikt de twaalf meegeleverde effecten.

## Wat is getest

Op 17 en 18 november 2026, op een Mac, met HyperFrames 0.9.64 en 0.9.65. Op Windows en Linux is niets getest.

- Een nieuw project aanmaken, de controle draaien, beelden bekijken en het demofilmpje renderen.
- De controle herkent de key, de vier modellen, de limiet en het saldo.
- De stem genereren met Eleven v4 en de woordtijden ophalen met Scribe v2, in het Engels en het Nederlands.
- Een illustratie genereren met Nano Banana 2.1 op 4K, ook met een beeld als voorbeeld.
- Muziek genereren met Lyria 3 Pro, op lengte snijden en onder de stem leggen.
- Een hele video van 72 seconden in het Nederlands, van script tot render.
- Het gereedschap is geschikt gemaakt voor Windows: tekst gaat overal als UTF-8, de aanwijzingen noemen het juiste Python-commando en `npx` wordt als `npx.cmd` gevonden. Dat is op de Mac getest onder een instelling zonder UTF-8. Een proef op een echte Windows-computer is nog niet gedaan.

Nog niet getest: een hele video laten maken door een nieuwe Claude-sessie die alleen deze skill heeft, de skill op Linux, en een lange video met tien of meer illustraties in één stijl.

## Licentie

MIT, zie `LICENSE`. Het lettertype Space Grotesk in het sjabloon valt onder de SIL Open Font License.
