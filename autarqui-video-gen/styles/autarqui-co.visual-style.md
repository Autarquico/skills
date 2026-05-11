---
name: "autarqui.co"
version: "1.0"
tags:
  - editorial
  - minimalist
  - serif-italic
  - monochrome
  - premium-restraint
  - swiss-leaning
author: "autarqui.co"
source_url: "https://autarqui.co"
created: "2026-05-09"

style_prompt_short: >
  Premium minimalist editorial. Pure monochrome (#ffffff bg, #1a1a1a body,
  #000000 headings). Lora serif italic for display, Poppins light/regular for
  body, generous whitespace, hairline rules, no decoration. Apple/Stripe/Linear
  caliber of restraint with editorial-print soul.

style_prompt_full: >
  Visual identity for autarqui.co — an umbrella brand for AI, integrations and
  business automation products (sigma: labor/fiscal advisory; delta: conversational
  BI; alpha: core). The aesthetic is editorial print rendered for screen: a printed
  monograph or a New Yorker spread, not a SaaS landing page.

  PALETTE — strict monochrome. Background pure white #ffffff. Body text #1a1a1a
  (near-black, never pure black). Headings pure black #000000 for maximum weight
  contrast. Muted secondary #6e6e6e for labels and metadata. Faint #9a9a9a for
  fine print and citations. Hairline rules #d4d4d4 (structural) and #ebebeb (soft
  separators). Subtle surface tint #fafafa for the rare card or quote block. NO
  color accents at all in the default treatment. If a single accent is ever
  required for a CTA or data highlight, treat it as functional (one accent, one
  use), never decorative — never gradients, never multi-color palettes, never
  brand-blue/purple/teal SaaS tropes.

  TYPOGRAPHY — two families, used with discipline. Display: Lora (serif), weight
  400-500, italic for emphasis and pull-quotes, tight tracking (-0.02em on large
  sizes, -0.01em on mid). Body: Poppins (sans), weight 350 default for body,
  500-600 only for labels and bold inline. Mono: DejaVu Sans Mono / Menlo for
  any code or technical readouts. UPPERCASE + wide tracking (0.08em-0.18em) is
  reserved for eyebrows, section labels, and metadata only — never for headings
  or body. Hierarchy comes from size, weight contrast, and italic — not color,
  not boxes. Numbered sections use a small italic Lora numeral (e.g. "01")
  above the heading. Lowercase product names (sigma, delta, alpha — Greek letters
  σ δ α as symbols when at small sizes).

  LAYOUT — generous whitespace as primary structural element. Flush-left default,
  centered only for hero / pull-quote / closing moments. Hairline horizontal rules
  (#d4d4d4) separate top-level sections; soft rules (#ebebeb) inside groups. No
  cards, no shadows, no rounded corners (or 2px max if absolutely needed). Page
  margins generous (~20mm-equivalent). Two-column grids for principles or
  comparison tables; otherwise single column with max-width ~150-155mm-equivalent.
  Logo system: Greek lowercase letters inscribed in circles, B&W (σ sigma,
  δ delta, α alpha). Wordmark is "autarqui.co" — lowercase, ".co" extension in
  muted gray, never all-caps.

  MOTION (for video/animation contexts) — slow, considered, editorial. Long
  hold beats. Fades over cuts. Type sets with restraint — letterspacing or
  weight transitions rather than bouncy springs. No kinetic typography stunts,
  no whoosh transitions, no zoom-and-pop. Think a documentary title sequence
  or a printed page being turned, not a TikTok edit. Pacing tolerates silence
  and stillness — let frames breathe. When numbers or stats appear they count
  up calmly, never with confetti.

  TONE / VOICE (for narration, captions, on-screen copy) — Spanish first, but
  the discipline ports to English. Direct, sober, competent. Anti-marketing.
  Real verbatim brand lines: "La gestión de tu negocio en otro plano de
  realidad." / "No vendemos software. Vendemos autonomía y eficiencia
  operativa." / "autarqui.co hace empresas más autosuficientes." Sharp
  diagnostic phrases when describing the problem ("Demos brillantes,
  integraciones que no llegan, equipos que no la adoptan." / "Genérica por
  fuera, frágil por dentro, sin contexto del negocio."). Never grandiose,
  never vague-promise, never "revolutionary." Plain words. Useful sentences.
  If a sentence does not help a decision, cut it.

  EXPLICITLY FORBIDDEN: gradients, glassmorphism, neon, gloss, drop shadows,
  rounded card stacks, emoji, AI-generated decorative imagery, stock-photo
  hero shots of "diverse team smiling at laptop", purple-blue SaaS gradients,
  bouncy spring animations, kinetic-typography stunts, "✨ AI-powered ✨" copy,
  exclamation marks, marketing superlatives.

colors:
  primary:
    - name: "Paper white"
      hex: "#ffffff"
      role: "dominant background, negative space — almost everything sits on this"
    - name: "Ink"
      hex: "#1a1a1a"
      role: "primary body text, near-black; never use pure #000000 here"
    - name: "Heading black"
      hex: "#000000"
      role: "headings, strong inline emphasis, structural rules where weight matters"
  neutral:
    - name: "Muted"
      hex: "#6e6e6e"
      role: "secondary text, labels, metadata, italic captions"
    - name: "Faint"
      hex: "#9a9a9a"
      role: "tertiary text, citations, footer, fine print"
    - name: "Rule"
      hex: "#d4d4d4"
      role: "primary hairline separators between sections"
    - name: "Rule soft"
      hex: "#ebebeb"
      role: "subtle separators inside groups, table row dividers"
    - name: "Surface"
      hex: "#fafafa"
      role: "rare card or quote-block tint; use sparingly"
  accent: []

typography:
  display:
    family: "Lora"
    fallback: "Bitstream Charter, Georgia, serif"
    weight: "400-500"
    style: "italic for emphasis and quotes; tight tracking (-0.02em)"
  body:
    family: "Poppins"
    fallback: "Helvetica Neue, Arial, sans-serif"
    weight: "350 default; 500-600 for inline strong and labels"
    style: "sentence case, comfortable line height (1.5-1.55)"
  mono:
    family: "DejaVu Sans Mono"
    fallback: "Menlo, monospace"
    weight: "400"
    style: "code, technical readouts only"
  rules:
    - "Lora italic carries display, pull-quotes, and section numerals — that italic IS the brand voice."
    - "UPPERCASE + wide tracking (0.08em / 0.18em) only for eyebrows, labels, metadata. Never for headings or body."
    - "Strong inline = Poppins 600, color shifts to #000 (heading black). No color highlights."
    - "Product names always lowercase (sigma, delta, alpha) or as Greek symbols (σ δ α) at small sizes."
    - "Wordmark: 'autarqui.co' — lowercase, '.co' extension renders in #6e6e6e muted."
    - "No font weights heavier than 600. No condensed, no display gimmicks."
    - "Hierarchy via size + weight + italic. Never via color."

layout:
  grid: "Generous whitespace primary. Single-column max ~150-155mm equivalent for prose; two-column for principles/comparison; centered only for hero, pull-quote, closing moments."
  alignment: "Flush left default. Centered for ceremony only."
  aspect_ratio: "Adaptive — vertical 9:16 for IG/social, 16:9 for landscape, 1:1 for square. Letterboxing in white #ffffff is acceptable; never black bars."
  notes:
    - "Hairline rules #d4d4d4 between top-level sections; #ebebeb soft inside groups."
    - "No cards, no shadows. 0px or max 2px border radius."
    - "Numbered sections: small italic Lora numeral above heading (e.g. '01' in #9a9a9a)."
    - "Logo placement: top-left in mark + wordmark, top-right reserved for utility (date, doc type), all in 8pt uppercase wide-tracked Poppins #6e6e6e."
    - "Footer/closing: centered mark, italic Lora pull-quote, italic citation, uppercase attribution line."

motion:
  transitions:
    - "fade"
    - "hold"
    - "slow type-on (letterspacing or opacity, never bounce)"
    - "soft cross-dissolve"
  animation_style: >
    Editorial slow. Eases like ease-out-cubic or custom long curves (1200-2000ms
    for hero text reveals). Type sets letter-by-letter via letterspacing relax
    or fades, never via stagger-bounce. Numbers count up at constant rate, no
    overshoot. Hairline rules draw left-to-right slowly. No spring physics
    unless damped to near-critical.
  pacing: "Considered. Long holds (1.5-3s on key frames). Tolerates silence and stillness. A 30s spot has 6-10 cuts max, not 25."
  audio_cues:
    - "near-silence is fine"
    - "single soft piano note or tonal mark for section change"
    - "no whooshes, no risers, no impacts"
    - "ambient/minimal piano or modern-classical bed if music is used"

mood:
  keywords:
    - "sober"
    - "editorial"
    - "calmado"
    - "premium-by-restraint"
    - "auditable"
    - "competent"
    - "modern without posturing"
  era: "Contemporary 2025+ — but rooted in printed-monograph and Swiss editorial traditions"
  cultural_reference: "Apple marketing pages (restraint), Stripe.com (typographic clarity), Linear.app (calm density), Müller-Brockmann (Swiss grid), Massimo Vignelli (rule-based system), New Yorker / Monocle / Kinfolk (editorial italic-serif voice)"
  avoid:
    - "gradients (all forms)"
    - "glassmorphism / blur effects"
    - "drop shadows / glow"
    - "emoji"
    - "exclamation marks"
    - "rounded card stacks"
    - "purple-blue SaaS hero gradients"
    - "stock photos of smiling teams"
    - "AI-generated decorative imagery (real product/people footage only — and even that, sparingly)"
    - "kinetic typography stunts / bouncy springs"
    - "whoosh / riser / impact sound effects"
    - "marketing superlatives ('revolutionary', 'next-gen', 'game-changing')"
    - "✨ ⚡ 🚀 and similar emoji-as-decoration"
    - "all-caps for headings or body"
    - "more than one accent color (currently zero)"

products:
  alpha:
    symbol: "α"
    name: "alpha"
    role: "brand core / future flagship product reservation"
  sigma:
    symbol: "σ"
    name: "sigma"
    role: "AI-assisted labor & fiscal advisory for SMEs"
  delta:
    symbol: "δ"
    name: "delta"
    role: "conversational BI / API integration layer with generative AI"

verbatim_lines:
  master: "autarqui.co hace empresas más autosuficientes."
  tagline: "La gestión de tu negocio en otro plano de realidad."
  anti_positioning: "No vendemos software. Vendemos autonomía y eficiencia operativa."
  diagnostic_phrases:
    - "Demos brillantes, integraciones que no llegan, equipos que no la adoptan."
    - "Genérica por fuera, frágil por dentro, sin contexto del negocio."
    - "La tecnología avanza más rápido que la organización que la asume."
  closing_quote: "El mayor fruto de la autosuficiencia es la libertad. — Epicuro"

assets:
  reference_images:
    - "/Users/alex/Downloads/autarquico-rebrand/dossier-branding.html (canonical brand dossier)"
    - "https://autarqui.co (live site)"
  logos:
    - "autarquico-logo.png (α / umbrella mark)"
    - "sigma-logo.png (σ)"
    - "delta-logo.png (δ)"
    - "logos.png (full system)"
  color_palette_image:
    url: ""
---

## Design Principles

1. **Restraint is the design.** Every element on screen must justify its presence. The default action is to remove, not add.
2. **Hierarchy via type, not color.** Size, weight, and italic do all the work. Color does none of it (the brand is monochrome by intent).
3. **Italic Lora is the voice.** When something needs to feel human, considered, or authored — it goes in Lora italic. That serif italic is the single most distinctive brand asset; protect it.
4. **Whitespace is structural, not leftover.** Margins and gaps are sized intentionally. Cramped layouts are off-brand.
5. **Anti-marketing tone.** No superlatives, no exclamations, no buzzwords. Lines like "No vendemos software. Vendemos autonomía y eficiencia operativa." set the register — calm, direct, slightly skeptical, never hyped.
6. **Premium by restraint** — the explicit reference is Apple / Stripe / Linear. Clarity over decoration, hierarchy over effects, space over noise. Greek letters inscribed in circles, B&W. Done.
7. **Optionality preserved.** A new product (any free Greek letter) can join the system without breaking it. Never style anything in a way that requires re-doing it later.

## Connectors

### OpenMontage / Remotion (primary use)
- Background: solid `#ffffff`, never gradients.
- Text overlays: Poppins 350 for body captions; Lora italic 400 for pull-quote moments and section numerals.
- Title cards: flush-left, generous left margin (~12% of width), Lora 400 italic for the headline, small uppercase Poppins eyebrow above (`#6e6e6e`, tracking 0.18em).
- Stat reveals: number in Lora 500 (not italic), label below in Poppins uppercase 500 wide-tracked.
- Section transitions: hairline rule draws across the frame in `#d4d4d4` over ~600ms, then fades; new section opens with italic Lora "0X" numeral.
- Caption burn (subtitles): Poppins 500, `#1a1a1a` on white with thin top/bottom rules, never colored highlight boxes.
- Closing card: centered α mark, italic Lora pull-quote, italic citation underneath, "autarqui.co" wordmark and date in small uppercase wide-tracked Poppins `#9a9a9a`.

### HeyGen / Avatar video
- Background plate: `#ffffff` solid or very subtle `#fafafa` surface tint. No virtual office, no gradients.
- Lower-third: thin `#d4d4d4` rule, presenter name in Poppins 500, role/title in Lora italic 400 muted.
- Voice direction: calm, measured, low energy floor. Spanish-first (es-ES neutral). Never enthusiastic-explainer cadence.

### HTML / Web slides / Figma
- Use the dossier CSS tokens verbatim (see `dossier-branding.html`). Lora and Poppins via Google Fonts. A4-style pages or 16:9 slides — same type system either way.

### Image generation (FLUX / Imagen / etc.)
- Generally avoid AI-generated imagery. If unavoidable: editorial black-and-white photography only, shallow depth of field, natural light, no people-as-decoration. Architectural detail, hands at work, paper documents on a desk — that register. Never illustrative, never 3D-render, never iconographic.

## Usage Quick Reference

| Need | Choice |
|------|--------|
| Background | `#ffffff` |
| Body text | Poppins 350 / `#1a1a1a` |
| Heading | Lora 400-500 / `#000000` |
| Pull quote | Lora 400 italic / `#000000` |
| Eyebrow / label | Poppins 500 UPPERCASE 0.18em tracking / `#6e6e6e` |
| Separator | 1px `#d4d4d4` hairline |
| Number / stat | Lora 500 (large) / `#000000` |
| Product mark | Greek letter in B&W circle (σ δ α) |
| Wordmark | `autarqui.co` lowercase, `.co` in `#6e6e6e` |
| Music | minimal piano / modern-classical / silence |
| Pace | slow — long holds, few cuts |
