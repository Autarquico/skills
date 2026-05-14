/**
 * Auto-generated from styles/autarqui-co.visual-style.md
 * via scripts/lib/resolve_style.py — do not edit by hand.
 */

import type { StyleTokens } from "../../lib/tokens";

export const TOKENS: StyleTokens = {
  "meta": {
    "name": "autarqui.co",
    "slug": "autarqui-co",
    "version": "1.0",
    "source_url": "https://autarqui.co",
    "style_prompt_short": "Premium minimalist editorial. Pure monochrome (#ffffff bg, #1a1a1a body, #000000 headings). Lora serif italic for display, Poppins light/regular for body, generous whitespace, hairline rules, no decoration. Apple/Stripe/Linear caliber of restraint with editorial-print soul.\n",
    "style_prompt_full": "Visual identity for autarqui.co — an umbrella brand for AI, integrations and business automation products (sigma: labor/fiscal advisory; delta: conversational BI; alpha: core). The aesthetic is editorial print rendered for screen: a printed monograph or a New Yorker spread, not a SaaS landing page.\nPALETTE — strict monochrome. Background pure white #ffffff. Body text #1a1a1a (near-black, never pure black). Headings pure black #000000 for maximum weight contrast. Muted secondary #6e6e6e for labels and metadata. Faint #9a9a9a for fine print and citations. Hairline rules #d4d4d4 (structural) and #ebebeb (soft separators). Subtle surface tint #fafafa for the rare card or quote block. NO color accents at all in the default treatment. If a single accent is ever required for a CTA or data highlight, treat it as functional (one accent, one use), never decorative — never gradients, never multi-color palettes, never brand-blue/purple/teal SaaS tropes.\nTYPOGRAPHY — two families, used with discipline. Display: Lora (serif), weight 400-500, italic for emphasis and pull-quotes, tight tracking (-0.02em on large sizes, -0.01em on mid). Body: Poppins (sans), weight 350 default for body, 500-600 only for labels and bold inline. Mono: DejaVu Sans Mono / Menlo for any code or technical readouts. UPPERCASE + wide tracking (0.08em-0.18em) is reserved for eyebrows, section labels, and metadata only — never for headings or body. Hierarchy comes from size, weight contrast, and italic — not color, not boxes. Numbered sections use a small italic Lora numeral (e.g. \"01\") above the heading. Lowercase product names (sigma, delta, alpha — Greek letters σ δ α as symbols when at small sizes).\nLAYOUT — generous whitespace as primary structural element. Flush-left default, centered only for hero / pull-quote / closing moments. Hairline horizontal rules (#d4d4d4) separate top-level sections; soft rules (#ebebeb) inside groups. No cards, no shadows, no rounded corners (or 2px max if absolutely needed). Page margins generous (~20mm-equivalent). Two-column grids for principles or comparison tables; otherwise single column with max-width ~150-155mm-equivalent. Logo system: Greek lowercase letters inscribed in circles, B&W (σ sigma, δ delta, α alpha). Wordmark is \"autarqui.co\" — lowercase, \".co\" extension in muted gray, never all-caps.\nMOTION (for video/animation contexts) — slow, considered, editorial. Long hold beats. Fades over cuts. Type sets with restraint — letterspacing or weight transitions rather than bouncy springs. No kinetic typography stunts, no whoosh transitions, no zoom-and-pop. Think a documentary title sequence or a printed page being turned, not a TikTok edit. Pacing tolerates silence and stillness — let frames breathe. When numbers or stats appear they count up calmly, never with confetti.\nTONE / VOICE (for narration, captions, on-screen copy) — Spanish first, but the discipline ports to English. Direct, sober, competent. Anti-marketing. Real verbatim brand lines: \"La gestión de tu negocio en otro plano de realidad.\" / \"No vendemos software. Vendemos autonomía y eficiencia operativa.\" / \"autarqui.co hace empresas más autosuficientes.\" Sharp diagnostic phrases when describing the problem (\"Demos brillantes, integraciones que no llegan, equipos que no la adoptan.\" / \"Genérica por fuera, frágil por dentro, sin contexto del negocio.\"). Never grandiose, never vague-promise, never \"revolutionary.\" Plain words. Useful sentences. If a sentence does not help a decision, cut it.\nEXPLICITLY FORBIDDEN: gradients, glassmorphism, neon, gloss, drop shadows, rounded card stacks, emoji, AI-generated decorative imagery, stock-photo hero shots of \"diverse team smiling at laptop\", purple-blue SaaS gradients, bouncy spring animations, kinetic-typography stunts, \"✨ AI-powered ✨\" copy, exclamation marks, marketing superlatives.\n"
  },
  "typography": {
    "display": {
      "family": "Lora",
      "fallback": "Bitstream Charter, Georgia, serif",
      "weights": [
        400,
        500
      ],
      "italic_available": true
    },
    "body": {
      "family": "Poppins",
      "fallback": "Helvetica Neue, Arial, sans-serif",
      "weights": [
        400,
        500
      ],
      "italic_available": false
    },
    "mono": {
      "family": "DejaVu Sans Mono",
      "fallback": "Menlo, monospace",
      "weights": [
        400
      ],
      "italic_available": false
    }
  },
  "colors": {
    "primary": [
      {
        "name": "Paper white",
        "hex": "#ffffff",
        "role": "dominant background, negative space — almost everything sits on this"
      },
      {
        "name": "Ink",
        "hex": "#1a1a1a",
        "role": "primary body text, near-black; never use pure #000000 here"
      },
      {
        "name": "Heading black",
        "hex": "#000000",
        "role": "headings, strong inline emphasis, structural rules where weight matters"
      }
    ],
    "accent": [],
    "neutral": [
      {
        "name": "Muted",
        "hex": "#6e6e6e",
        "role": "secondary text, labels, metadata, italic captions"
      },
      {
        "name": "Faint",
        "hex": "#9a9a9a",
        "role": "tertiary text, citations, footer, fine print"
      },
      {
        "name": "Rule",
        "hex": "#d4d4d4",
        "role": "primary hairline separators between sections"
      },
      {
        "name": "Rule soft",
        "hex": "#ebebeb",
        "role": "subtle separators inside groups, table row dividers"
      },
      {
        "name": "Surface",
        "hex": "#fafafa",
        "role": "rare card or quote-block tint; use sparingly"
      }
    ],
    "bg": "#ffffff",
    "ink": "#1a1a1a",
    "heading": "#000000",
    "muted": "#6e6e6e",
    "faint": "#9a9a9a",
    "rule": "#d4d4d4",
    "ruleSoft": "#ebebeb",
    "surface": "#fafafa"
  },
  "layout": {
    "hero": {
      "font_size_px": 96,
      "line_height": 1.1,
      "letter_spacing_em": -0.02,
      "alignment": "flush-left",
      "max_width_pct": 92
    },
    "body": {
      "font_size_px": 28,
      "line_height": 1.55
    },
    "list_item": {
      "numeral_font_size_px": 38,
      "main_font_size_px": 78,
      "indent_pct": 8
    },
    "master_quote": {
      "font_size_px": 56,
      "alignment": "center",
      "has_rules": true
    },
    "closing": {
      "logo_size_px": 320,
      "spacing_px": 30
    }
  },
  "motion": {
    "in": {
      "type": "fade",
      "duration_ms": 900,
      "easing": "ease-out-cubic"
    },
    "out": {
      "type": "fade",
      "duration_ms": 700,
      "easing": "ease-out-cubic"
    },
    "pacing": "Considered. Long holds (1.5-3s on key frames). Tolerates silence and stillness. A 30s spot has 6-10 cuts max, not 25.",
    "transitions": [
      "fade",
      "hold",
      "slow type-on (letterspacing or opacity, never bounce)",
      "soft cross-dissolve"
    ],
    "forbidden": []
  },
  "audio": {
    "music_curve": "editorial",
    "prefer_voice": "piper",
    "voice_language": "es"
  },
  "ios_chrome": false,
  "forbidden": [],
  "verbatim_lines": {
    "master": "autarqui.co hace empresas más autosuficientes.",
    "tagline": "La gestión de tu negocio en otro plano de realidad.",
    "anti_positioning": "No vendemos software. Vendemos autonomía y eficiencia operativa.",
    "diagnostic_phrases": [
      "Demos brillantes, integraciones que no llegan, equipos que no la adoptan.",
      "Genérica por fuera, frágil por dentro, sin contexto del negocio.",
      "La tecnología avanza más rápido que la organización que la asume."
    ],
    "closing_quote": "El mayor fruto de la autosuficiencia es la libertad. — Epicuro"
  }
} as StyleTokens;
