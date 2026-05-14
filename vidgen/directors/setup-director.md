# Setup Director

Esta fase se ejecuta **una vez por marca** (no por video). Sale el `visual-style.md` y la config local del usuario.

## Cuándo entrar a esta fase

- El usuario menciona una marca por primera vez ("configura mi marca", "crear estilo para X")
- Da una URL/PDF/dossier de brand
- No existe `styles/<brand>.visual-style.md`

## Flujo

### 1. Discovery del brand input

Pregunta al usuario qué tiene:
- URL de su sitio web
- PDF/HTML del brand dossier
- Descripción libre ("monocromo editorial italic-serif tipo Monocle")
- Imagen de referencia
- Nada — quiere generar uno desde cero con tus preguntas

### 2. Extracción

| Input | Cómo extraer |
|---|---|
| **URL** | WebFetch con prompt: "extract: hex colors, font families, headline copy, tagline, tone samples, navigation labels, layout vibe, motion patterns" |
| **PDF/HTML local** | Read del archivo. Si es HTML con CSS, extrae los CSS variables como tokens directos |
| **Imagen** | Describe colors visibles, type style aproximado, layout vibe |
| **Descripción libre** | Asistente conversacional: pregunta colores hex, fuentes, mood, motion preference |

### 3. Generación de `visual-style.md`

Output a `~/.claude/skills/autarqui-video-gen/styles/<slug>.visual-style.md`.

**Estructura completa requerida** (las scenes la leen vía `lib/tokens.ts`):

```yaml
---
name: "<Brand Name>"
slug: "<kebab-case>"
version: "1.0"
source_url: "<URL or file path>"
created: "<YYYY-MM-DD>"

style_prompt_short: >
  Una o dos frases capturando la esencia visual.

style_prompt_full: >
  Prompt detallado de generación. Incluye hex codes inline,
  font names, layout structure, motion patterns, mood. Be specific
  about what TO do and what NOT to do.

# === DESIGN TOKENS (consumidos por scene library) ===

typography:
  display:
    family: "Lora"
    fallback: "Bitstream Charter, Georgia, serif"
    weights: [400, 500]
    italic_available: true
  body:
    family: "Poppins"
    fallback: "Helvetica Neue, Arial, sans-serif"
    weights: [350, 400, 500, 600]
  mono:
    family: "DejaVu Sans Mono"
    fallback: "Menlo, monospace"
    weights: [400]

colors:
  primary:
    - { name: "Paper white", hex: "#ffffff", role: "background" }
    - { name: "Ink",         hex: "#1a1a1a", role: "body text" }
    - { name: "Heading",     hex: "#000000", role: "headings, strong" }
  accent: []
  neutral:
    - { name: "Muted",     hex: "#6e6e6e", role: "labels, metadata" }
    - { name: "Faint",     hex: "#9a9a9a", role: "tertiary" }
    - { name: "Rule",      hex: "#d4d4d4", role: "hairlines" }
    - { name: "Rule soft", hex: "#ebebeb", role: "soft separators" }
    - { name: "Surface",   hex: "#fafafa", role: "subtle tint" }

layout:
  hero:
    font_size_px: 96
    line_height: 1.1
    letter_spacing_em: -0.022
    alignment: flush-left      # flush-left | center | flush-right
    max_width_pct: 92
  body:
    font_size_px: 28
    line_height: 1.55
  list_item:
    numeral_font_size_px: 38
    main_font_size_px: 78
    indent_pct: 8
  master_quote:
    font_size_px: 56
    alignment: center
    has_rules: true
  closing:
    logo_size_px: 340
    spacing_px: 30

motion:
  in:
    type: fade                  # fade | slide | cut | glitch | spring
    duration_ms: 900
    easing: ease-out-cubic
  out:
    type: fade
    duration_ms: 700
    easing: ease-out-cubic
  pacing: slow                  # slow | medium | fast
  transitions: [fade, hold]
  forbidden: [bouncy-spring, kinetic-stunt, glitch]

audio:
  music_curve: editorial        # editorial | punchy | cinematic | silent
  prefer_voice: piper           # piper | coqui-xtts | none
  voice_language: es

# Whether UI mock scenes should render iOS chrome (status bar, home indicator)
ios_chrome: true

# Optional: whitelist scenes for this brand (default: all available)
allowed_scenes: []

# Things explicitly NOT to do (carried into Remotion as constraints)
forbidden:
  - gradients
  - glassmorphism
  - drop shadows beyond 2px
  - rounded radii > 12px
  - emoji
  - exclamation marks in headlines
  - all-caps body
  - bouncy springs

verbatim_lines:
  master: "..."
  tagline: "..."
  diagnostic_phrases: []
---

## Design Principles

(Texto libre con la filosofía. Para humanos, no consumido por código.)

## Connectors

### Remotion / autarqui-video-gen
(Notas específicas de cómo este style se aplica al renderer.)
```

### 4. Configuración local

Si el usuario no tiene `config/local.yaml`, créalo:

```yaml
# Override de default.yaml
output_folder: <ask user — default ~/videos>
default_style: <slug recién creado>
```

### 5. Verificación

Imprime un resumen y pregunta:
- ¿Los colores extraídos son correctos?
- ¿Las fuentes son las que quieres?
- ¿El tono y "forbidden" capturan lo que evitas?

Si confirma, fase setup terminada.

## Brand sources de referencia

- `/Users/alex/src/OpenMontage/brand/autarqui-co.visual-style.md` — ejemplo canónico (autarqui-co), sirve como template y como caso testeo.
- OpenMontage también tiene una galería en `.agents/skills/visual-style/references/gallery/` con Müller-Brockmann Swiss, Saul Bass cinematic, etc. Consultable como referencia pero NO se importa código (AGPL).

## Nota técnica

El `visual-style.md` es leído por `compositions/src/lib/tokens.ts` cuando se renderiza. El parser usa frontmatter YAML estricto — si añades campos nuevos, actualiza también `lib/tokens.ts` y los TypeScript types.
