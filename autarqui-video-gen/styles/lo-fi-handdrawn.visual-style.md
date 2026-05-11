---
name: "Lo-Fi Hand-Drawn"
slug: "lo-fi-handdrawn"
version: "1.0"
created: "2026-05-10"

style_prompt_short: >
  Sketchy, warm, imperfect. Cormorant Garamond + Space Mono on cream paper
  with subtle grain. Studio Ghibli's title-card energy.

style_prompt_full: >
  Hand-made warmth aesthetic. Cream paper background (#f8f1e3), warm dark
  text (#2a1f15), with subtle paper grain texture (achievable via overlay
  in Remotion). Typography: Cormorant Garamond italic for headlines (organic
  serif), Space Mono for labels (typewriter feel). Motion: slow, slightly
  imperfect — animations have a touch of jitter, fades have grain. Color:
  warm earth palette — cream, sepia, faded ochre #c7a87a as accent. NO sharp
  geometry, NO neon, NO Helvetica. Embrace imperfection.

typography:
  display:
    family: "Cormorant Garamond"
    fallback: "Garamond, serif"
    weights: [400, 500, 600]
    italic_available: true
  body:
    family: "DM Sans"
    fallback: "Helvetica, sans-serif"
    weights: [400, 500]
  mono:
    family: "Space Mono"
    weights: [400, 700]

colors:
  primary:
    - { name: "Paper cream", hex: "#f8f1e3", role: "background" }
    - { name: "Warm ink",    hex: "#2a1f15", role: "body text" }
    - { name: "Deep sepia",  hex: "#1a1208", role: "heading" }
  accent:
    - { name: "Faded ochre", hex: "#c7a87a", role: "accent / highlights" }
  neutral:
    - { name: "Muted",     hex: "#7a6a55", role: "labels, metadata" }
    - { name: "Faint",     hex: "#a89880", role: "tertiary" }
    - { name: "Rule",      hex: "#3a2f25", role: "hairlines" }
    - { name: "Rule soft", hex: "#d4c5ad", role: "soft separators" }
    - { name: "Surface",   hex: "#efe6d0", role: "card tint" }

layout:
  hero:
    font_size_px: 100
    line_height: 1.18
    letter_spacing_em: -0.01
    alignment: flush-left
    max_width_pct: 88
  body:
    font_size_px: 30
    line_height: 1.6
  list_item:
    numeral_font_size_px: 42
    main_font_size_px: 78
    indent_pct: 9
  master_quote:
    font_size_px: 60
    alignment: center
    has_rules: true
  closing:
    logo_size_px: 300
    spacing_px: 30

motion:
  in:
    type: fade
    duration_ms: 1100
    easing: ease-out-cubic
  out:
    type: fade
    duration_ms: 900
    easing: ease-out-cubic
  pacing: slow
  transitions: [fade, hold]
  forbidden: [glitch, kinetic-stunt, harsh-cut]

audio:
  music_curve: editorial
  prefer_voice: coqui-xtts
  voice_language: es

ios_chrome: false

forbidden:
  - sharp geometric shapes
  - neon colors
  - Helvetica
  - perfect symmetry
  - hard cuts
  - glow effects
  - emoji

verbatim_lines: {}
---

## Design Principles

Imperfection is intentional. The aesthetic should feel like it could have been hand-painted. Warmth over precision. Motion breathes. Silence is allowed.
