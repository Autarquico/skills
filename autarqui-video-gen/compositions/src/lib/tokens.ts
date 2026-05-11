/**
 * tokens.ts — Browser-safe types + React context for design tokens.
 *
 * Scenes consume tokens via `useStyleTokens()`. Tokens themselves are passed
 * from the project's Composition.tsx (rendered server-side, inlined into the
 * bundle). The render-director generates the inlined object using lib/tokens-node.ts
 * (which reads visual-style.md from disk).
 *
 * Why split? Remotion bundles via webpack for browser execution. Reading .md
 * files at runtime requires Node fs APIs that don't bundle to browser. So:
 *   - Browser side (this file): types + provider/consumer hook only.
 *   - Node side (tokens-node.ts): the YAML parser that reads disk.
 */

import * as React from "react";

// ============================================================================
// TYPES
// ============================================================================

export interface ColorToken {
  name: string;
  hex: string;
  role: string;
}

export interface FontToken {
  family: string;
  fallback?: string;
  weights: number[];
  italic_available?: boolean;
}

export interface LayoutSection {
  font_size_px: number;
  line_height?: number;
  letter_spacing_em?: number;
  alignment?: "flush-left" | "center" | "flush-right";
  max_width_pct?: number;
}

export interface MotionConfig {
  type: "fade" | "slide" | "cut" | "glitch" | "spring";
  duration_ms: number;
  easing: string;
}

export interface StyleTokens {
  meta: {
    name: string;
    slug: string;
    version: string;
    source_url?: string;
    style_prompt_short: string;
    style_prompt_full: string;
  };
  typography: {
    display: FontToken;
    body: FontToken;
    mono: FontToken;
  };
  colors: {
    primary: ColorToken[];
    accent: ColorToken[];
    neutral: ColorToken[];
    bg: string;
    ink: string;
    heading: string;
    muted: string;
    faint: string;
    rule: string;
    ruleSoft: string;
    surface: string;
  };
  layout: {
    hero: LayoutSection;
    body: LayoutSection;
    list_item: {
      numeral_font_size_px: number;
      main_font_size_px: number;
      indent_pct: number;
    };
    master_quote: {
      font_size_px: number;
      alignment: "center" | "flush-left";
      has_rules: boolean;
    };
    closing: {
      logo_size_px: number;
      spacing_px: number;
    };
  };
  motion: {
    in: MotionConfig;
    out: MotionConfig;
    pacing: "slow" | "medium" | "fast";
    transitions: string[];
    forbidden: string[];
  };
  audio: {
    music_curve: "editorial" | "punchy" | "cinematic" | "silent";
    prefer_voice: "piper" | "coqui-xtts" | "none";
    voice_language: string;
  };
  ios_chrome: boolean;
  forbidden: string[];
  verbatim_lines: Record<string, string | string[]>;
}

// ============================================================================
// REACT CONTEXT — used by all scenes via useStyleTokens()
// ============================================================================

const StyleContext = React.createContext<StyleTokens | null>(null);

export const StyleProvider: React.FC<{
  tokens: StyleTokens;
  children: React.ReactNode;
}> = ({ tokens, children }) =>
  React.createElement(StyleContext.Provider, { value: tokens }, children);

export function useStyleTokens(): StyleTokens {
  const tokens = React.useContext(StyleContext);
  if (!tokens) {
    throw new Error(
      "useStyleTokens must be used within a <StyleProvider>. " +
        "Wrap your composition root with <StyleProvider tokens={...}>.",
    );
  }
  return tokens;
}
