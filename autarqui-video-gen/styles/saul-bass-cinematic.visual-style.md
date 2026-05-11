---
name: "Saul Bass Cinematic"
slug: "saul-bass-cinematic"
version: "1.0"
created: "2026-05-10"

style_prompt_short: >
  Mid-century Saul Bass title sequence. Hand-cut shapes, kinetic typography,
  warm muted palette. Anatomy-of-a-Murder energy.

style_prompt_full: >
  Saul Bass-inspired title sequence aesthetic from mid-1950s to 60s film.
  Typography: condensed sans like Bebas Neue or hand-lettered feel, set
  large with energy and rhythm. Animation: kinetic — type assembles
  character-by-character, slides across the frame, masks reveal it. Color:
  warm muted palette — bone #f4ecd8, ink #1a1a1a, with ONE bold accent
  per frame (vermillion #d8412f or saffron #e8a843). Compositions are
  asymmetric and confident. Cuts are sharp; transitions are wipes or
  masks (never fades). No gradients, no photo realism. Geometric shapes
  (circles, triangles) sometimes accompany type. Background is slightly
  textured cream, never pure white.

typography:
  display:
    family: "Bebas Neue"
    fallback: "Impact, Arial Narrow, sans-serif"
    weights: [400]
    italic_available: false
  body:
    family: "Space Grotesk"
    fallback: "Helvetica Neue, sans-serif"
    weights: [400, 500, 700]
  mono:
    family: "Space Mono"
    weights: [400]

colors:
  primary:
    - { name: "Bone",   hex: "#f4ecd8", role: "background" }
    - { name: "Ink",    hex: "#1a1a1a", role: "body text" }
    - { name: "Black",  hex: "#000000", role: "headings" }
  accent:
    - { name: "Vermillion", hex: "#d8412f", role: "primary accent" }
    - { name: "Saffron",    hex: "#e8a843", role: "secondary accent" }
  neutral:
    - { name: "Muted",  hex: "#5a4f3e", role: "labels" }
    - { name: "Faint",  hex: "#8a7e6b", role: "tertiary" }
    - { name: "Rule",   hex: "#1a1a1a", role: "hairlines" }
    - { name: "Rule soft", hex: "#d4c9b0", role: "soft separators" }
    - { name: "Surface", hex: "#ebe0c8", role: "card tint" }

layout:
  hero:
    font_size_px: 200
    line_height: 0.9
    letter_spacing_em: 0.02
    alignment: flush-left
    max_width_pct: 90
  body:
    font_size_px: 28
    line_height: 1.4
  list_item:
    numeral_font_size_px: 80
    main_font_size_px: 100
    indent_pct: 10
  master_quote:
    font_size_px: 80
    alignment: center
    has_rules: false
  closing:
    logo_size_px: 280
    spacing_px: 24

motion:
  in:
    type: slide
    duration_ms: 600
    easing: ease-out-expo
  out:
    type: slide
    duration_ms: 400
    easing: ease-in-cubic
  pacing: medium
  transitions: [slide, mask, cut]
  forbidden: [fade, gradient]

audio:
  music_curve: cinematic
  prefer_voice: coqui-xtts
  voice_language: es

ios_chrome: false

forbidden:
  - photo realism
  - gradients
  - drop shadows
  - rounded soft cards
  - polite typography
  - centered everything

verbatim_lines: {}
---

## Design Principles

Saul Bass treated film titles as cinema in their own right. His work is graphic, physical, theatrical. Apply the same energy: type is a character, not decoration. Asymmetry is the rule. Negative space is loud. Movement has weight.
