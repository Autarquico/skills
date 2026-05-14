/**
 * ListItem — Numbered editorial list item.
 *
 * Pattern: italic numeral above main text in italic display font.
 * From the delta launch "Lo que tu negocio sabe" pattern.
 */

import * as React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface ListItemProps {
  numeral: string;
  /** Main text — single string OR two-part for staggered reveal. */
  text?: string;
  parts?: [string, string];
  part2_delay_frames?: number;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const ListItem: React.FC<ListItemProps> = ({
  numeral,
  text,
  parts,
  part2_delay_frames,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);

  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);
  const numeralOp = fadeIn(frame, 0, Math.round(inFrames * 0.5));
  const mainOp = fadeIn(frame, Math.round(inFrames * 0.4), inFrames);
  const part2Op = parts && part2_delay_frames !== undefined
    ? fadeIn(frame, part2_delay_frames, inFrames)
    : 1;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: "flex-start",
        paddingLeft: `${t.layout.list_item.indent_pct}%`,
        paddingRight: `${t.layout.list_item.indent_pct}%`,
        opacity: op,
      }}
    >
      <div
        style={{
          fontFamily: fonts.displayItalic,
          fontStyle: "italic",
          fontWeight: 400,
          fontSize: t.layout.list_item.numeral_font_size_px,
          color: t.colors.faint,
          marginBottom: 18,
          letterSpacing: "0.04em",
          opacity: numeralOp,
        }}
      >
        {numeral}
      </div>

      {parts ? (
        <div
          style={{
            fontFamily: fonts.displayItalic,
            fontStyle: "italic",
            fontWeight: 400,
            fontSize: t.layout.list_item.main_font_size_px,
            lineHeight: 1.18,
            letterSpacing: "-0.012em",
            color: t.colors.heading,
            maxWidth: "92%",
          }}
        >
          <span style={{ opacity: mainOp }}>{parts[0]}</span>
          <span style={{ opacity: part2Op }}>{parts[1]}</span>
        </div>
      ) : (
        <div
          style={{
            fontFamily: fonts.displayItalic,
            fontStyle: "italic",
            fontWeight: 400,
            fontSize: t.layout.list_item.main_font_size_px,
            lineHeight: 1.18,
            letterSpacing: "-0.012em",
            color: t.colors.heading,
            maxWidth: "92%",
            opacity: mainOp,
          }}
        >
          {text}
        </div>
      )}
    </AbsoluteFill>
  );
};

export const ListItemSchema = {
  numeral: { type: "string", required: true },
  text: { type: "string", required: false },
  parts: { type: "array", required: false, of: "string", length: 2 },
  part2_delay_frames: { type: "number", required: false },
} as const;
