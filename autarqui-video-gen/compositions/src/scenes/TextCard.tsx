/**
 * TextCard — One or two large lines of editorial typography.
 *
 * Use for: hero headlines, thesis lines, promises, closing copy.
 * Reads tokens for font, color, layout. NEVER hardcode.
 */

import * as React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, defaultPacing, sceneOpacity } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface TextCardProps {
  /** 1-3 lines. Each line renders on its own visual row. */
  lines: string[];
  /**
   * Index of the line to render with display-italic emphasis.
   * If omitted, all lines are roman.
   */
  emphasis_line?: number;
  /** Override layout alignment from tokens. */
  alignment?: "flush-left" | "center";
  /** Frame range for fade-in/out (relative to scene start). */
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const TextCard: React.FC<TextCardProps> = ({
  lines,
  emphasis_line,
  alignment,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const totalFrames = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);

  const op = sceneOpacity(frame, 0, totalFrames, inFrames, outFrames);
  const align = alignment ?? t.layout.hero.alignment;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: align === "center" ? "center" : "flex-start",
        paddingLeft: align === "center" ? "8%" : `${100 - t.layout.hero.max_width_pct - 8}%`,
        paddingRight: "8%",
        opacity: op,
      }}
    >
      {lines.map((line, i) => {
        const isItalic = emphasis_line === i;
        const lineDelay = i * Math.round(inFrames * 0.6);
        const lineOp = fadeIn(frame, lineDelay, inFrames);
        return (
          <div
            key={i}
            style={{
              fontFamily: isItalic ? fonts.displayItalic : fonts.display,
              fontStyle: isItalic ? "italic" : "normal",
              fontWeight: isItalic ? 400 : 500,
              fontSize: t.layout.hero.font_size_px,
              lineHeight: t.layout.hero.line_height,
              letterSpacing: `${t.layout.hero.letter_spacing_em}em`,
              color: t.colors.heading,
              maxWidth: `${t.layout.hero.max_width_pct}%`,
              opacity: lineOp,
              marginTop: i === 0 ? 0 : Math.round(t.layout.hero.font_size_px * 0.18),
              textAlign: align === "center" ? "center" : "left",
            }}
          >
            {line}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

export const TextCardSchema = {
  lines: { type: "array", required: true, of: "string" },
  emphasis_line: { type: "number", required: false },
  alignment: { type: "enum", values: ["flush-left", "center"], required: false },
} as const;
