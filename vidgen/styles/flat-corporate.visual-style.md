---
name: "Flat Corporate"
slug: "flat-corporate"
version: "1.0"
created: "2026-05-10"

style_prompt_short: >
  Modern flat SaaS aesthetic. Inter + IBM Plex with brand-blue accent.
  The "competent enterprise" look — clean, friendly, conservative.

style_prompt_full: >
  Modern flat corporate aesthetic, the look of Stripe-adjacent enterprise SaaS
  marketing in the late 2020s. Inter for everything, with IBM Plex Sans for
  data emphasis. Brand-blue accent (#2563EB) used in CTAs, KPI accents, and
  link states. White background, dark slate text (#111827), generous spacing.
  Layout: centered hero, 12-column grid, soft shadows allowed. Motion: clean
  spring physics, cubic eases, never bouncy. Photography of "real people"
  acceptable but tasteful. Geometric icons (Heroicons style).

typography:
  display:
    family: "Inter"
    fallback: "system-ui, sans-serif"
    weights: [600, 700, 800]
    italic_available: false
  body:
    family: "Inter"
    fallback: "system-ui, sans-serif"
    weights: [400, 500, 600]
  mono:
    family: "IBM Plex Mono"
    weights: [400, 500]

colors:
  primary:
    - { name: "White",       hex: "#ffffff", role: "background" }
    - { name: "Slate body",  hex: "#111827", role: "body text" }
    - { name: "Slate heading", hex: "#0a0a0a", role: "heading" }
  accent:
    - { name: "Brand blue", hex: "#2563EB", role: "CTAs, KPI accents, links" }
    - { name: "Success",    hex: "#10B981", role: "confirmations" }
  neutral:
    - { name: "Muted",       hex: "#6B7280", role: "labels, metadata" }
    - { name: "Faint",       hex: "#9CA3AF", role: "tertiary" }
    - { name: "Rule",        hex: "#D1D5DB", role: "hairlines" }
    - { name: "Rule soft",   hex: "#E5E7EB", role: "soft separators" }
    - { name: "Surface",     hex: "#F9FAFB", role: "card tint" }

layout:
  hero:
    font_size_px: 88
    line_height: 1.1
    letter_spacing_em: -0.025
    alignment: center
    max_width_pct: 80
  body:
    font_size_px: 26
    line_height: 1.5
  list_item:
    numeral_font_size_px: 32
    main_font_size_px: 60
    indent_pct: 10
  master_quote:
    font_size_px: 56
    alignment: center
    has_rules: false
  closing:
    logo_size_px: 280
    spacing_px: 28

motion:
  in:
    type: fade
    duration_ms: 500
    easing: ease-out-cubic
  out:
    type: fade
    duration_ms: 400
    easing: ease-out-cubic
  pacing: medium
  transitions: [fade, hold]
  forbidden: [bouncy-spring, glitch, kinetic-stunt]

audio:
  music_curve: cinematic
  prefer_voice: coqui-xtts
  voice_language: es

ios_chrome: true

forbidden:
  - brutalist raw type
  - hand-drawn imperfection
  - extreme italic emphasis
  - more than 2 accent colors
  - sharp/aggressive motion

verbatim_lines: {}
---

## Design Principles

The corporate flat look says "we are competent and modern". It's the visual default for B2B SaaS, fintech, and enterprise tools. Use it when the audience expects polish and trust signals. Avoid when the audience is craft/design-conscious — they'll read it as generic.
