---
name: "Brutalist"
slug: "brutalist"
version: "1.0"
created: "2026-05-10"

style_prompt_short: >
  Raw, monospace, no decoration. Concrete-architecture-as-typography.
  Confident in its ugliness.

style_prompt_full: >
  Brutalist web aesthetic — JetBrains Mono everywhere, system colors only,
  zero polish. Layout: misaligned on purpose, raw padding, hairline borders
  with full strength (#000000), zero rounded corners, zero shadows. Black
  on white or white on black inversions for impact. Numerals get capital
  letter spacing. Buttons look like underlined links. The aesthetic
  intentionally rejects soft corporate UX. Motion: instant cuts, no fades,
  glitch acceptable.

typography:
  display:
    family: "JetBrains Mono"
    fallback: "Courier, monospace"
    weights: [400, 700, 800]
    italic_available: true
  body:
    family: "JetBrains Mono"
    fallback: "Courier, monospace"
    weights: [400, 500]
  mono:
    family: "JetBrains Mono"
    weights: [400, 700]

colors:
  primary:
    - { name: "White", hex: "#ffffff", role: "background" }
    - { name: "Black", hex: "#000000", role: "body text" }
    - { name: "Black", hex: "#000000", role: "heading" }
  accent: []
  neutral:
    - { name: "Muted", hex: "#000000", role: "labels (also black, never gray)" }
    - { name: "Faint", hex: "#666666", role: "tertiary" }
    - { name: "Rule",  hex: "#000000", role: "hairlines (always pure black, never light)" }
    - { name: "Rule soft", hex: "#000000", role: "no soft separators in brutalism" }
    - { name: "Surface", hex: "#ffffff", role: "no surface tint" }

layout:
  hero:
    font_size_px: 130
    line_height: 1.0
    letter_spacing_em: -0.04
    alignment: flush-left
    max_width_pct: 95
  body:
    font_size_px: 24
    line_height: 1.5
  list_item:
    numeral_font_size_px: 130
    main_font_size_px: 56
    indent_pct: 5
  master_quote:
    font_size_px: 80
    alignment: flush-left
    has_rules: true
  closing:
    logo_size_px: 240
    spacing_px: 16

motion:
  in:
    type: cut
    duration_ms: 60
    easing: linear
  out:
    type: cut
    duration_ms: 60
    easing: linear
  pacing: fast
  transitions: [cut]
  forbidden: [fade, spring, ease, polish]

audio:
  music_curve: punchy
  prefer_voice: piper
  voice_language: es

ios_chrome: false

forbidden:
  - rounded corners
  - drop shadows
  - gradients
  - soft transitions
  - photography
  - decorative type
  - centered alignment for body
  - emoji
  - more than 2 colors total

verbatim_lines: {}
---

## Design Principles

Brutalism is honest. It doesn't pretend. The grid is visible. The default browser styles are visible. The typography is the system. There is no marketing gloss. The aesthetic is the message: "we're real, we're functional, we don't need polish to be valuable."
