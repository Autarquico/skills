/**
 * KineticType — Kinetic typography scene.
 *
 * Splits text into characters or words and animates each independently.
 * Frame-driven (no GSAP timeline), but uses GSAP-style easings.
 *
 * Patterns supported:
 *   - char-stagger: each char fades+slides in with delay
 *   - word-stagger: each word fades in
 *   - mask-reveal: text scrolls up behind a mask
 *   - line-by-line: lines drop in one after another
 */

import * as React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, easings } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface KineticTypeProps {
  text: string;
  pattern?: "char-stagger" | "word-stagger" | "line-by-line" | "mask-reveal";
  /** Stagger interval in frames between units */
  stagger_frames?: number;
  /** Duration of each unit's animation in frames */
  unit_duration_frames?: number;
  /** Use display-italic font (default: display roman) */
  italic?: boolean;
  /** Override font size; default uses hero size from tokens */
  font_size_px?: number;
  alignment?: "flush-left" | "center";
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const KineticType: React.FC<KineticTypeProps> = ({
  text,
  pattern = "word-stagger",
  stagger_frames = 3,
  unit_duration_frames = 18,
  italic = false,
  font_size_px,
  alignment,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const op = sceneOpacity(frame, 0, total, 12, 24);
  const align = alignment ?? t.layout.hero.alignment;
  const size = font_size_px ?? t.layout.hero.font_size_px;

  const baseStyle: React.CSSProperties = {
    fontFamily: italic ? fonts.displayItalic : fonts.display,
    fontStyle: italic ? "italic" : "normal",
    fontWeight: italic ? 400 : 500,
    fontSize: size,
    lineHeight: t.layout.hero.line_height,
    letterSpacing: `${t.layout.hero.letter_spacing_em}em`,
    color: t.colors.heading,
  };

  // Render based on pattern
  const renderUnits = () => {
    if (pattern === "char-stagger") {
      const chars = Array.from(text);
      return chars.map((c, i) => {
        const delay = i * stagger_frames;
        const localFrame = frame - delay;
        const op = fadeIn(localFrame, 0, unit_duration_frames);
        const ty = (1 - easings.easeOutCubic(Math.min(1, Math.max(0, localFrame / unit_duration_frames)))) * 24;
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              opacity: op,
              transform: `translateY(${ty}px)`,
              whiteSpace: c === " " ? "pre" : undefined,
            }}
          >
            {c}
          </span>
        );
      });
    }

    if (pattern === "word-stagger") {
      const words = text.split(/(\s+)/);
      return words.map((w, i) => {
        if (/^\s+$/.test(w)) return <span key={i} style={{ whiteSpace: "pre" }}>{w}</span>;
        const delay = (i / 2) * stagger_frames;
        const localFrame = frame - delay;
        const op = fadeIn(localFrame, 0, unit_duration_frames);
        const ty = (1 - easings.easeOutCubic(Math.min(1, Math.max(0, localFrame / unit_duration_frames)))) * 18;
        return (
          <span
            key={i}
            style={{
              display: "inline-block",
              opacity: op,
              transform: `translateY(${ty}px)`,
            }}
          >
            {w}
          </span>
        );
      });
    }

    if (pattern === "line-by-line") {
      const lines = text.split("\n");
      return (
        <>
          {lines.map((line, i) => {
            const delay = i * stagger_frames * 4;
            const localFrame = frame - delay;
            const op = fadeIn(localFrame, 0, unit_duration_frames);
            const ty = (1 - easings.easeOutCubic(Math.min(1, Math.max(0, localFrame / unit_duration_frames)))) * 28;
            return (
              <div
                key={i}
                style={{
                  opacity: op,
                  transform: `translateY(${ty}px)`,
                  marginBottom: i < lines.length - 1 ? size * 0.18 : 0,
                }}
              >
                {line}
              </div>
            );
          })}
        </>
      );
    }

    if (pattern === "mask-reveal") {
      // Whole text rises up behind a mask
      const localFrame = frame;
      const progress = easings.easeOutQuart(Math.min(1, localFrame / unit_duration_frames / 2));
      return (
        <div
          style={{
            overflow: "hidden",
            display: "inline-block",
          }}
        >
          <div
            style={{
              transform: `translateY(${(1 - progress) * 100}%)`,
            }}
          >
            {text}
          </div>
        </div>
      );
    }

    return text;
  };

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
      <div
        style={{
          ...baseStyle,
          maxWidth: `${t.layout.hero.max_width_pct}%`,
          textAlign: align === "center" ? "center" : "left",
        }}
      >
        {renderUnits()}
      </div>
    </AbsoluteFill>
  );
};

export const KineticTypeSchema = {
  text: { type: "string", required: true },
  pattern: {
    type: "enum",
    values: ["char-stagger", "word-stagger", "line-by-line", "mask-reveal"],
    required: false,
  },
  stagger_frames: { type: "number", required: false },
  unit_duration_frames: { type: "number", required: false },
  italic: { type: "boolean", required: false },
  font_size_px: { type: "number", required: false },
  alignment: { type: "enum", values: ["flush-left", "center"], required: false },
} as const;
