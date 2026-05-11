---
name: autarqui-video-gen
description: Mini-estudio de producción de video declarativo. Composición vía Remotion, asset sourcing vía Pixabay/Pexels/Unsplash/Freesound (free APIs), voz local vía Piper/Coqui XTTS, subtítulos vía Whisper.cpp, motion expandido con GSAP/Three.js/Lottie/Manim. Cero dependencia de APIs de pago. Use when the user wants to create a video — explainer, launch, social, demo, anything — and needs the full production loop (brand setup → script → asset acquisition → composition → render).
license: MIT
---

# autarqui-video-gen

Skill de producción de video instruction-driven. La inteligencia (Claude) escribe el guion, decide qué scenes usar, invoca tools de asset y renderiza vía Remotion. Todo open-source, todo local, cero APIs de pago.

## Routing — qué leer según la fase

Cuando el usuario invoca este skill, identifica la fase y lee SOLO el director correspondiente. **No leas múltiples directors a la vez.**

| Disparador del usuario | Fase | Lee primero |
|---|---|---|
| Primera vez con una marca, "configura mi marca", URL/PDF/dossier de brand | **Setup** | `directors/setup-director.md` |
| "Crea/extrae el visual style de X" | **Style** | `directors/style-director.md` |
| "Quiero hacer un video sobre X", "ayúdame con el guion" | **Script** | `directors/script-director.md` |
| "Necesito música/imagen/sonido para esta escena" | **Asset** | `directors/asset-director.md` |
| "Renderiza", "compón el video", `script.json` listo | **Render** | `directors/render-director.md` |

Si la fase no está clara, pregunta al usuario antes de leer un director.

## Architecture en una pantalla

```
visual-style.md  ─┐
                  ├─→  scene library (token-driven)  ─→  Remotion render  →  MP4
script.json      ─┘                ↑
                                   │
                  asset tools (Pixabay/Pexels/Unsplash/Freesound/Piper/Whisper/...)
```

- **`styles/*.visual-style.md`** — design tokens por marca/estética (typography, colors, layout, motion, audio). Tokens-first: cambias el style file, cambias el video sin tocar código.
- **`compositions/src/scenes/`** — librería de scenes Remotion que LEEN tokens del visual-style.md activo. Nunca hardcodean valores.
- **`compositions/src/projects/<id>/`** — workspace por video. Contiene `script.json`, assets descargados, composición custom (si aplica).
- **`tools/`** — Python/bash wrappers sobre tools open-source. Cada uno self-contained.

## Reglas de oro

1. **Tokens, no literales.** Si una scene escribe `fontSize: 92` o `color: "#000"`, está mal. Debe leer del visual-style.md activo vía `lib/tokens.ts`.
2. **Antes de inventar scene custom, busca en la librería.** El registry está en `compositions/src/scenes/index.ts`.
3. **Antes de generar asset con tool, mira el cache** (`cache/pixabay/`, `cache/models/`) y la `music_library/` o `assets/` del proyecto.
4. **No llamar APIs de pago.** Este skill es 100% open-source / free-tier. Si surge esa necesidad, es un blocker, no un fallback silencioso.
5. **Música y voz**: por defecto Piper (voz) y Pixabay (música). Coqui XTTS solo si el usuario pide voz de mejor calidad o voice cloning.

## CLI `avg` (úsalo, no rebuilds wheels)

El skill incluye una CLI bash que automatiza las operaciones comunes. **Cuando el usuario pida hacer un video, usa `avg new` y `avg render` en lugar de editar archivos a mano:**

```bash
avg new <id> --style <slug> --aspect <9:16|16:9|1:1|4:5> --duration <s> [--music <path>]
   # Crea project workspace completo: script.json + tokens.ts + Composition.tsx
   # + auto-registra en Root.tsx + copia music a public/<id>/

avg render <id>
   # Renderiza a compositions/out/<id>.mp4

avg list [styles|scenes|projects|all]    # Inventario
avg style validate <slug>                # Verifica frontmatter
avg style resolve <slug> --to <file>     # YAML → TS tokens (lo usa avg new internamente)
avg doctor                               # Health check
avg install [--all | --tool <name>]      # Instala deps
```

**Flujo típico cuando el usuario pide "haz un video":**

1. `avg new <id> --style autarqui-co --duration 60 --music <path>`  → scaffold completo
2. Editar `script.json` con el copy (desde el script-director)
3. Editar `Composition.tsx` para reflejar las scenes elegidas (importar más scenes si hace falta)
4. `avg render <id>`  → MP4 listo

## Capability discovery

Antes de cualquier render, ejecuta:

```bash
~/.claude/skills/autarqui-video-gen/scripts/doctor.sh
```

Reporta qué tools están instalados, qué keys faltan, qué styles existen. **Lee este output antes de prometer al usuario que algo va a funcionar.**

## File locations summary

```
~/.claude/skills/autarqui-video-gen/
├── SKILL.md          ← este archivo
├── directors/        ← instrucciones por fase
├── styles/           ← galería de visual-style.md
├── compositions/     ← Remotion (scenes + projects)
├── tools/            ← asset/audio/motion/etc.
├── scripts/          ← install, doctor, helpers
├── config/           ← default.yaml, api-keys.yaml
└── cache/            ← assets descargados, models, fonts
```

## Out of scope (no hacer)

- Generación de avatar/talking-head (HeyGen, D-ID) — requiere APIs de pago
- Generación de imagen/video AI hospedada (FLUX/Veo/Kling/Runway/Sora) — APIs de pago
- Editing GUI tipo timeline — el skill es declarativo
- Distribución/upload automático

Si el usuario pide algo de la lista anterior, escala como blocker y propón el path local equivalente (Three.js scene, Lottie, animación Manim, etc.) o el plan híbrido user-genera-asset-fuera + skill-compone (ver `directors/asset-director.md`).
