/**
 * fonts.ts — Dynamic Google Fonts loader.
 *
 * Reads the `typography` tokens from the active style and loads the right
 * @remotion/google-fonts modules at composition time. Returns a record of
 * loaded font family names (which include the hash suffix Remotion uses).
 *
 * Note: @remotion/google-fonts uses dynamic imports per family. We can't
 * statically know which families a style requires, so we maintain a registry
 * of supported fonts. Adding a new font requires adding it here.
 */

import type { StyleTokens } from "./tokens";

// Statically-imported font modules. Add more here as needed for new styles.
// Each import is tree-shaken to only load the families actually used by a render.
import { loadFont as loadLora } from "@remotion/google-fonts/Lora";
import { loadFont as loadPoppins } from "@remotion/google-fonts/Poppins";
import { loadFont as loadInter } from "@remotion/google-fonts/Inter";
import { loadFont as loadPlayfairDisplay } from "@remotion/google-fonts/PlayfairDisplay";
import { loadFont as loadBebasNeue } from "@remotion/google-fonts/BebasNeue";
import { loadFont as loadSpaceMono } from "@remotion/google-fonts/SpaceMono";
import { loadFont as loadSpaceGrotesk } from "@remotion/google-fonts/SpaceGrotesk";
import { loadFont as loadIBMPlexSans } from "@remotion/google-fonts/IBMPlexSans";
import { loadFont as loadIBMPlexMono } from "@remotion/google-fonts/IBMPlexMono";
import { loadFont as loadJetBrainsMono } from "@remotion/google-fonts/JetBrainsMono";
import { loadFont as loadDMSans } from "@remotion/google-fonts/DMSans";
import { loadFont as loadDMSerifDisplay } from "@remotion/google-fonts/DMSerifDisplay";
import { loadFont as loadCormorantGaramond } from "@remotion/google-fonts/CormorantGaramond";

type LoaderFn = (
  style: "normal",
  options?: { weights?: string[]; subsets?: string[]; style?: "normal" | "italic" },
) => { fontFamily: string; waitUntilDone?: () => Promise<void> };

const REGISTRY: Record<string, LoaderFn> = {
  Lora: loadLora as LoaderFn,
  Poppins: loadPoppins as LoaderFn,
  Inter: loadInter as LoaderFn,
  "Playfair Display": loadPlayfairDisplay as LoaderFn,
  PlayfairDisplay: loadPlayfairDisplay as LoaderFn,
  "Bebas Neue": loadBebasNeue as LoaderFn,
  BebasNeue: loadBebasNeue as LoaderFn,
  "Space Mono": loadSpaceMono as LoaderFn,
  SpaceMono: loadSpaceMono as LoaderFn,
  "Space Grotesk": loadSpaceGrotesk as LoaderFn,
  SpaceGrotesk: loadSpaceGrotesk as LoaderFn,
  "IBM Plex Sans": loadIBMPlexSans as LoaderFn,
  IBMPlexSans: loadIBMPlexSans as LoaderFn,
  "IBM Plex Mono": loadIBMPlexMono as LoaderFn,
  IBMPlexMono: loadIBMPlexMono as LoaderFn,
  "JetBrains Mono": loadJetBrainsMono as LoaderFn,
  JetBrainsMono: loadJetBrainsMono as LoaderFn,
  "DM Sans": loadDMSans as LoaderFn,
  DMSans: loadDMSans as LoaderFn,
  "DM Serif Display": loadDMSerifDisplay as LoaderFn,
  DMSerifDisplay: loadDMSerifDisplay as LoaderFn,
  "Cormorant Garamond": loadCormorantGaramond as LoaderFn,
  CormorantGaramond: loadCormorantGaramond as LoaderFn,
};

export interface LoadedFonts {
  display: string;
  displayItalic: string;
  body: string;
  mono: string;
}

/**
 * Load all fonts required by a style. Returns the canonical fontFamily strings
 * to use in CSS (these include the Remotion hash suffix).
 *
 * If a font isn't in REGISTRY, falls back to the system fallback string.
 */
export function loadFontsForStyle(tokens: StyleTokens): LoadedFonts {
  const display = loadOne(tokens.typography.display.family, tokens.typography.display.weights);
  const displayItalic = tokens.typography.display.italic_available
    ? loadOneItalic(tokens.typography.display.family, tokens.typography.display.weights)
    : display;
  const body = loadOne(tokens.typography.body.family, tokens.typography.body.weights);
  const mono = loadOne(tokens.typography.mono.family, tokens.typography.mono.weights);

  return {
    display: display || systemFallback(tokens.typography.display.fallback, "serif"),
    displayItalic: displayItalic || systemFallback(tokens.typography.display.fallback, "serif"),
    body: body || systemFallback(tokens.typography.body.fallback, "sans-serif"),
    mono: mono || systemFallback(tokens.typography.mono.fallback, "monospace"),
  };
}

function loadOne(family: string, weights: number[]): string | null {
  const loader = REGISTRY[family];
  if (!loader) {
    console.warn(
      `[autarqui-video-gen] Font "${family}" not in REGISTRY (lib/fonts.ts). ` +
        `Add it via \`import { loadFont } from "@remotion/google-fonts/${family.replace(/\s+/g, "")}"\`. ` +
        `Falling back to system font.`,
    );
    return null;
  }
  const result = loader("normal", {
    weights: weights.map(String),
    subsets: ["latin"],
  });
  return result.fontFamily;
}

function loadOneItalic(family: string, weights: number[]): string | null {
  const loader = REGISTRY[family];
  if (!loader) return null;
  const result = loader("normal", {
    weights: weights.map(String),
    subsets: ["latin"],
    style: "italic",
  });
  return result.fontFamily;
}

function systemFallback(fallback: string | undefined, category: string): string {
  return fallback || `system-ui, ${category}`;
}
