---
name: "Müller-Brockmann Swiss"
slug: "mueller-brockmann-swiss"
version: "1.0"
created: "2026-05-10"

style_prompt_short: >
  Swiss International Style. Akzidenz-Grotesk bold + grid + a single red accent.
  Mathematical, objective, ruthlessly minimalist.

style_prompt_full: >
  Swiss-school typography from the 1950s-70s tradition (Müller-Brockmann, Hofmann,
  Vignelli). Headline: Akzidenz-Grotesk Bold (or its Inter/Helvetica fallbacks)
  in UPPERCASE with tight tracking. Body: Inter Regular. Layout: 12-column grid,
  flush-left or strict centered, generous margins. Color: pure black (#000000)
  on white (#ffffff), with ONE accent — red #E60012 — used sparingly for a single
  element per frame (a numeral, a rule, a punctuation mark). Motion: hard cuts,
  no fades except subtle opacity. Hairline rules everywhere. Numerals are
  protagonists (set big, bold, often vertical orientation). NO italic, NO
  decorative typography, NO gradients, NO photography (or only severely
  cropped/grid-aligned).

typography:
  display:
    family: "Inter"
    fallback: "Helvetica Neue, Arial, sans-serif"
    weights: [700, 800, 900]
    italic_available: false
  body:
    family: "Inter"
    fallback: "Helvetica Neue, Arial, sans-serif"
    weights: [400, 500, 700]
  mono:
    family: "JetBrains Mono"
    weights: [400]

colors:
  primary:
    - { name: "White", hex: "#ffffff", role: "background" }
    - { name: "Black", hex: "#000000", role: "body text, headings" }
    - { name: "Black",  hex: "#000000", role: "heading" }
  accent:
    - { name: "Swiss Red", hex: "#E60012", role: "single accent per frame" }
  neutral:
    - { name: "Muted",     hex: "#5a5a5a", role: "labels, metadata" }
    - { name: "Faint",     hex: "#9a9a9a", role: "tertiary" }
    - { name: "Rule",      hex: "#000000", role: "hairlines (always black)" }
    - { name: "Rule soft", hex: "#cccccc", role: "soft separators" }
    - { name: "Surface",   hex: "#f5f5f5", role: "subtle tint" }

layout:
  hero:
    font_size_px: 110
    line_height: 0.95
    letter_spacing_em: -0.02
    alignment: flush-left
    max_width_pct: 78
  body:
    font_size_px: 28
    line_height: 1.4
  list_item:
    numeral_font_size_px: 110
    main_font_size_px: 56
    indent_pct: 12
  master_quote:
    font_size_px: 64
    alignment: flush-left
    has_rules: true
  closing:
    logo_size_px: 200
    spacing_px: 40

motion:
  in:
    type: cut
    duration_ms: 100
    easing: linear
  out:
    type: cut
    duration_ms: 100
    easing: linear
  pacing: medium
  transitions: [cut, hold]
  forbidden: [fade, spring, bouncy, kinetic]

audio:
  music_curve: punchy
  prefer_voice: piper
  voice_language: es

ios_chrome: false

forbidden:
  - italic typography
  - gradients
  - drop shadows
  - rounded corners
  - photography (unless severely cropped to grid)
  - more than ONE accent color
  - decorative serifs
  - emoji
  - exclamation marks

verbatim_lines: {}
---

## Design Principles

Swiss International Style at its purest. Objectivity over expression. The grid is the message. Type does the work; decoration is forbidden. Red appears once per frame, never twice. White is the protagonist. Black is the speaker. Hairlines structure space.

Reference: Joseph Müller-Brockmann's *Grid Systems in Graphic Design*, Massimo Vignelli's American Airlines identity, Helvetica documentary aesthetics.
