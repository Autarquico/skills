/**
 * tokens-node.ts — Node-only style loader.
 *
 * Reads `<slug>.visual-style.md` from disk, parses YAML frontmatter, returns
 * a `StyleTokens` object. Used by the render-director (Node CLI) to generate
 * the inlined tokens object that goes into a project's Composition.tsx.
 *
 * Do NOT import this from any browser-side / Remotion-rendered code — it
 * uses Node `fs`/`path` APIs that won't bundle for the browser.
 */

import matter from "gray-matter";
import * as fs from "fs";
import * as path from "path";

import type { ColorToken, FontToken, StyleTokens } from "./tokens";

const STYLES_DIR = path.join(__dirname, "..", "..", "..", "styles");

export function loadStyle(slug: string): StyleTokens {
  const filePath = path.join(STYLES_DIR, `${slug}.visual-style.md`);
  if (!fs.existsSync(filePath)) {
    throw new Error(
      `Style not found: ${slug}. Expected at ${filePath}. ` +
        `Available styles: ${listStyles().join(", ")}`,
    );
  }
  const raw = fs.readFileSync(filePath, "utf-8");
  const { data } = matter(raw);
  return parseTokens(data, slug);
}

export function listStyles(): string[] {
  if (!fs.existsSync(STYLES_DIR)) return [];
  return fs
    .readdirSync(STYLES_DIR)
    .filter((f) => f.endsWith(".visual-style.md"))
    .map((f) => f.replace(".visual-style.md", ""));
}

/**
 * Serialize tokens to a JS-literal string suitable for inlining into a TSX file.
 * Used by the render-director to embed the resolved tokens into Composition.tsx.
 */
export function serializeTokens(tokens: StyleTokens): string {
  return JSON.stringify(tokens, null, 2);
}

// ----------------------------------------------------------------------------
// Parser
// ----------------------------------------------------------------------------

function parseTokens(data: any, slug: string): StyleTokens {
  const colorByRole = (cs: ColorToken[], role: string): ColorToken | undefined =>
    cs.find((c) => c.role.toLowerCase().includes(role.toLowerCase()));

  const primary: ColorToken[] = data.colors?.primary || [];
  const neutral: ColorToken[] = data.colors?.neutral || [];
  const accent: ColorToken[] = data.colors?.accent || [];

  const bg = colorByRole(primary, "background")?.hex || "#ffffff";
  const ink = colorByRole(primary, "body text")?.hex || colorByRole(primary, "text")?.hex || "#1a1a1a";
  const heading = colorByRole(primary, "heading")?.hex || "#000000";
  const muted = colorByRole(neutral, "muted")?.hex || colorByRole(neutral, "labels")?.hex || "#6e6e6e";
  const faint = colorByRole(neutral, "faint")?.hex || colorByRole(neutral, "tertiary")?.hex || "#9a9a9a";
  const rule = colorByRole(neutral, "rule")?.hex || colorByRole(neutral, "hairline")?.hex || "#d4d4d4";
  const ruleSoft = colorByRole(neutral, "soft")?.hex || "#ebebeb";
  const surface = colorByRole(neutral, "surface")?.hex || "#fafafa";

  return {
    meta: {
      name: data.name || slug,
      slug: data.slug || slug,
      version: data.version || "1.0",
      source_url: data.source_url,
      style_prompt_short: data.style_prompt_short || "",
      style_prompt_full: data.style_prompt_full || "",
    },
    typography: {
      display: parseFont(data.typography?.display, {
        family: "Lora",
        fallback: "Georgia, serif",
        weights: [400, 500],
        italic_available: true,
      }),
      body: parseFont(data.typography?.body, {
        family: "Poppins",
        fallback: "system-ui, sans-serif",
        weights: [350, 400, 500],
      }),
      mono: parseFont(data.typography?.mono, {
        family: "Menlo",
        weights: [400],
      }),
    },
    colors: {
      primary,
      accent,
      neutral,
      bg,
      ink,
      heading,
      muted,
      faint,
      rule,
      ruleSoft,
      surface,
    },
    layout: {
      hero: {
        font_size_px: data.layout?.hero?.font_size_px || 96,
        line_height: data.layout?.hero?.line_height || 1.1,
        letter_spacing_em: data.layout?.hero?.letter_spacing_em || -0.02,
        alignment: data.layout?.hero?.alignment || "flush-left",
        max_width_pct: data.layout?.hero?.max_width_pct || 92,
      },
      body: {
        font_size_px: data.layout?.body?.font_size_px || 28,
        line_height: data.layout?.body?.line_height || 1.55,
      },
      list_item: {
        numeral_font_size_px: data.layout?.list_item?.numeral_font_size_px || 38,
        main_font_size_px: data.layout?.list_item?.main_font_size_px || 78,
        indent_pct: data.layout?.list_item?.indent_pct || 8,
      },
      master_quote: {
        font_size_px: data.layout?.master_quote?.font_size_px || 56,
        alignment: data.layout?.master_quote?.alignment || "center",
        has_rules: data.layout?.master_quote?.has_rules ?? true,
      },
      closing: {
        logo_size_px: data.layout?.closing?.logo_size_px || 320,
        spacing_px: data.layout?.closing?.spacing_px || 30,
      },
    },
    motion: {
      in: {
        type: data.motion?.in?.type || "fade",
        duration_ms: data.motion?.in?.duration_ms || 900,
        easing: data.motion?.in?.easing || "ease-out-cubic",
      },
      out: {
        type: data.motion?.out?.type || "fade",
        duration_ms: data.motion?.out?.duration_ms || 700,
        easing: data.motion?.out?.easing || "ease-out-cubic",
      },
      pacing: data.motion?.pacing || "slow",
      transitions: data.motion?.transitions || ["fade", "hold"],
      forbidden: data.motion?.forbidden || [],
    },
    audio: {
      music_curve: data.audio?.music_curve || "editorial",
      prefer_voice: data.audio?.prefer_voice || "piper",
      voice_language: data.audio?.voice_language || "es",
    },
    ios_chrome: data.ios_chrome ?? false,
    forbidden: data.forbidden || [],
    verbatim_lines: data.verbatim_lines || {},
  };
}

function parseFont(input: any, fallback: FontToken): FontToken {
  if (!input) return fallback;
  return {
    family: input.family || fallback.family,
    fallback: input.fallback || fallback.fallback,
    weights: input.weights || fallback.weights,
    italic_available: input.italic_available ?? fallback.italic_available,
  };
}
