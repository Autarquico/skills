# autarqui-video-gen

Mini-estudio de producción de video como Claude Code skill. **Open-source, local, cero APIs de pago.**

Composición [Remotion](https://www.remotion.dev) · assets [Pixabay](https://pixabay.com)/[Pexels](https://pexels.com)/[Unsplash](https://unsplash.com)/[Freesound](https://freesound.org) · voz local [Piper](https://github.com/rhasspy/piper) o [Coqui XTTS](https://github.com/coqui-ai/TTS) · subtítulos [Whisper.cpp](https://github.com/ggml-org/whisper.cpp) · motion expandido GSAP / Three.js / Lottie / Manim.

> Parte del monorepo [`Autarquico/skills`](https://github.com/Autarquico/skills) — junto con `autarqui-skillfactory` y `autarqui-dockerfiledoc`.

## Instalación en una línea

```bash
curl -sSL https://raw.githubusercontent.com/Autarquico/skills/main/autarqui-video-gen/scripts/quickstart.sh | bash
```

Eso hace:
1. Verifica system tools (git/node/npm/ffmpeg/python3)
2. Sparse-clone del subfolder `autarqui-video-gen/` del monorepo a `~/.claude/skills/autarqui-video-gen/`
3. Crea `.venv/` skill-local + instala Python deps
4. `npm install` en `compositions/` (Remotion + GSAP + Three.js + Lottie)
5. Bootstrap de `config/api-keys.yaml`
6. (Opcional, interactivo) añade `avg` a tu PATH
7. Corre `avg doctor`

Tiempo total: 3-5 min. Tras eso ya puedes:

```bash
avg render delta-launch-demo            # render del demo incluido
avg new mi-video --aspect 9:16 --duration 30
```

### Si prefieres clonar a mano

```bash
# Clone the whole monorepo and copy this skill
git clone https://github.com/Autarquico/skills.git /tmp/aq-skills
mkdir -p ~/.claude/skills
cp -r /tmp/aq-skills/autarqui-video-gen ~/.claude/skills/
rm -rf /tmp/aq-skills
~/.claude/skills/autarqui-video-gen/scripts/install.sh
```

Lo que hace `install.sh`:
- Verifica `node`, `npm`, `ffmpeg`, `python3` (te dice qué falta y dónde instalarlo)
- Crea `.venv/` skill-local con `pyyaml` y otros deps Python (sin tocar tu Python del sistema)
- `npm install` en `compositions/` (Remotion + GSAP + Three.js + Lottie)
- Crea `config/api-keys.yaml` desde template (ediar con tus keys gratis si quieres Pixabay/Pexels/etc.)

Para añadirlo al PATH (recomendado):
```bash
echo 'export PATH="$HOME/.claude/skills/autarqui-video-gen/scripts:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Verifica:
```bash
avg doctor
```

Para instalar tools opcionales (Piper, Whisper, Manim, Coqui, etc.):
```bash
avg install --all              # todo de golpe
avg install --tool piper       # uno a uno
avg install --tier-c           # opt-in: SD local, AnimateDiff (requiere GPU)
```

## CLI — `avg`

```bash
avg new <id> --style autarqui-co --aspect 9:16 --duration 60
  Crea proyecto: scripts/script.json + tokens.ts + Composition.tsx + auto-registro en Root.tsx

avg render <id>
  Renderiza compositions/out/<id>.mp4

avg list [styles|scenes|projects|all]
  Inventario

avg style validate <slug>
  Comprueba que un visual-style.md parsea

avg style resolve <slug> --to <file>
  YAML → tokens.ts (lo usa internamente avg new)

avg doctor
  Health check completo

avg install [--all | --tool <name> | --tier-c]
  Instala dependencias

avg open
  Abre la carpeta del skill
```

## Workflow de un video nuevo

```bash
# 1. Crear esqueleto
avg new mi-launch-30s --style autarqui-co --duration 30 --music ~/Downloads/track.mp3

# 2. Editar el copy
$EDITOR ~/.claude/skills/autarqui-video-gen/compositions/src/projects/mi-launch-30s/script.json

# 3. Reflejar el script en Composition.tsx (añadir/quitar scenes según necesites)
$EDITOR ~/.claude/skills/autarqui-video-gen/compositions/src/projects/mi-launch-30s/Composition.tsx

# 4. Drop logos/imágenes en public/
cp logo.png ~/.claude/skills/autarqui-video-gen/compositions/public/mi-launch-30s/

# 5. Render
avg render mi-launch-30s
```

## Uso desde Claude Code

Habla en natural. Claude detecta la fase y enruta al director correcto (`directors/`).

```
"Configura una marca nueva desde https://miempresa.com"
→ skill setup phase

"Quiero un video de 30s para Instagram sobre nuestro lanzamiento"
→ skill script phase + render

"Renderiza el video con estilo swiss en lugar de autarqui"
→ skill render phase con --style mueller-brockmann-swiss
```

## Arquitectura

```
visual-style.md (design tokens)  +  script.json (declarative scenes)
                              ↓
              Remotion + scene library (token-driven)
                              ↓
                            MP4
```

Los mismos `script.json` con visual-styles distintos producen videos visualmente totalmente diferentes — sin tocar código.

Ver `SKILL.md` para detalles operativos y `directors/` para las instrucciones por fase.

## Stack incluido

| Categoría | Tools |
|---|---|
| **Composición** | Remotion 4.x |
| **Encoding** | ffmpeg |
| **Asset libraries** | Pixabay (search/download/link) · Pexels (search/download/link) · Unsplash (search/download/link) · Freesound (search/download/link) · LottieFiles |
| **Voz** | Piper TTS · Coqui XTTS-v2 (con voice cloning) |
| **Subtítulos** | Whisper.cpp + ASS karaoke generator |
| **Motion** | GSAP plugins (libres desde 2024) · Three.js · Lottie · Manim |
| **Audio** | DemucS (stem separation) · ffmpeg-mix presets (editorial / punchy / cinematic / voice-over-music ducking / trim-tail-to) |
| **Source** | yt-dlp |
| **Imagen** | ImageMagick · rsvg-convert (SVG→PNG) |

## Scenes incluidas (15)

Editorial typography:
- `hero-title` · `text-card` · `list-item` · `dialogue-beat` · `master-quote` · `mark-reveal` · `closing-card` · `stat-reveal` · `kpi-row`

Motion expandido:
- `kinetic-type` · `three-scene` · `lottie-play`

UI mocks:
- `ui-mock-mobile` · `ui-mock-desktop` · `chat-overlay`

Todas tokenizadas — leen design tokens del `visual-style.md` activo, ninguna hardcodea fuentes/colores/tamaños.

## Visual styles incluidos (6)

- `autarqui-co` — premium minimalist editorial monocromo
- `mueller-brockmann-swiss` — Swiss International Style (Akzidenz uppercase + acento rojo único)
- `saul-bass-cinematic` — mid-century kinetic title sequence
- `lo-fi-handdrawn` — Cormorant Garamond + cream paper warmth
- `brutalist` — JetBrains Mono raw, zero polish
- `flat-corporate` — Inter + brand-blue (Stripe/Linear caliber)

Para crear uno nuevo: copia `styles/autarqui-co.visual-style.md`, edita los tokens, y usa con `--style <slug>`.

## Licencia

MIT. Cero contaminación AGPL. Forkea y licencia como quieras.
