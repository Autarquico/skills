/**
 * Pre-resolved tokens for delta-launch-demo, derived from
 * styles/autarqui-co.visual-style.md.
 *
 * In production, the render-director generates this file from the visual-style.md
 * via lib/tokens-node.ts. For this demo it's hand-written to match.
 */

import type { StyleTokens } from "../../lib/tokens";

export const TOKENS: StyleTokens = {
  meta: {
    name: "autarqui.co",
    slug: "autarqui-co",
    version: "1.0",
    style_prompt_short: "Premium minimalist editorial. Pure monochrome.",
    style_prompt_full: "",
  },
  typography: {
    display: {
      family: "Lora",
      fallback: "Bitstream Charter, Georgia, serif",
      weights: [400, 500],
      italic_available: true,
    },
    body: {
      family: "Poppins",
      fallback: "Helvetica Neue, Arial, sans-serif",
      weights: [300, 400, 500, 600],
    },
    mono: {
      family: "Menlo",
      weights: [400],
    },
  },
  colors: {
    primary: [
      { name: "Paper white", hex: "#ffffff", role: "background" },
      { name: "Ink", hex: "#1a1a1a", role: "body text" },
      { name: "Heading black", hex: "#000000", role: "heading" },
    ],
    accent: [],
    neutral: [
      { name: "Muted", hex: "#6e6e6e", role: "labels, metadata" },
      { name: "Faint", hex: "#9a9a9a", role: "tertiary" },
      { name: "Rule", hex: "#d4d4d4", role: "hairlines" },
      { name: "Rule soft", hex: "#ebebeb", role: "soft separators" },
      { name: "Surface", hex: "#fafafa", role: "subtle tint" },
    ],
    bg: "#ffffff",
    ink: "#1a1a1a",
    heading: "#000000",
    muted: "#6e6e6e",
    faint: "#9a9a9a",
    rule: "#d4d4d4",
    ruleSoft: "#ebebeb",
    surface: "#fafafa",
  },
  layout: {
    hero: {
      font_size_px: 96,
      line_height: 1.12,
      letter_spacing_em: -0.02,
      alignment: "flush-left",
      max_width_pct: 92,
    },
    body: {
      font_size_px: 28,
      line_height: 1.55,
    },
    list_item: {
      numeral_font_size_px: 38,
      main_font_size_px: 78,
      indent_pct: 8,
    },
    master_quote: {
      font_size_px: 56,
      alignment: "center",
      has_rules: true,
    },
    closing: {
      logo_size_px: 340,
      spacing_px: 30,
    },
  },
  motion: {
    in: { type: "fade", duration_ms: 900, easing: "ease-out-cubic" },
    out: { type: "fade", duration_ms: 700, easing: "ease-out-cubic" },
    pacing: "slow",
    transitions: ["fade", "hold"],
    forbidden: ["bouncy-spring", "kinetic-stunt", "glitch"],
  },
  audio: {
    music_curve: "editorial",
    prefer_voice: "piper",
    voice_language: "es",
  },
  ios_chrome: false,
  forbidden: [
    "gradients",
    "glassmorphism",
    "drop shadows",
    "rounded card stacks",
    "emoji",
    "exclamation marks",
  ],
  verbatim_lines: {
    master: "autarqui.co hace empresas más autosuficientes.",
  },
};
