/**
 * LyricLine — single lyric line with optional next-line preview.
 *
 * Use sequenced inside a project to make a lyric video. Each LyricLine occupies
 * its own Sequence with start/end frames matching the audio timing.
 *
 * For full lyric videos: build an array of {start_s, end_s, text} entries
 * (manually transcribed or via Whisper word-level), put each in a Sequence.
 */

import * as React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface LyricLineProps {
  text: string;
  /** Optional next line preview, dimmer */
  next_text?: string;
  /** Visual mode: bold display vs italic display vs minimal */
  mode?: "bold" | "italic" | "minimal";
  /** Optional gentle pulse effect tied to beat (frames per pulse) */
  pulse_frames?: number;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const LyricLine: React.FC<LyricLineProps> = ({
  text,
  next_text,
  mode = "bold",
  pulse_frames,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;

  // Tight in/out — lyrics shouldn't fade slowly
  const op = sceneOpacity(frame, 0, total, 6, 8);

  // Pulse: gentle scale tied to beat (if pulse_frames provided)
  const pulse = pulse_frames
    ? 1 + 0.018 * Math.sin((frame / pulse_frames) * Math.PI * 2)
    : 1;

  // Cumulative reveal: text "writes" in over first 25% of scene duration
  const writeProgress = interpolate(frame, [0, total * 0.25], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const visibleChars = Math.floor(text.length * writeProgress);
  const shownText = text.slice(0, visibleChars);

  const isBold = mode === "bold";
  const isItalic = mode === "italic";

  const nextOp = fadeIn(frame, Math.round(total * 0.5), 12) * 0.45;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: "center",
        padding: "10%",
        opacity: op,
      }}
    >
      <div
        style={{
          fontFamily: isItalic ? fonts.displayItalic : fonts.display,
          fontStyle: isItalic ? "italic" : "normal",
          fontWeight: isBold ? 700 : 500,
          fontSize: mode === "minimal" ? 70 : 110,
          lineHeight: 1.06,
          letterSpacing: "-0.022em",
          color: t.colors.heading,
          textAlign: "center",
          maxWidth: "92%",
          transform: `scale(${pulse})`,
          transformOrigin: "center center",
        }}
      >
        {shownText}
      </div>

      {next_text && (
        <div
          style={{
            marginTop: 30,
            fontFamily: fonts.body,
            fontWeight: 400,
            fontSize: 26,
            color: t.colors.muted,
            textAlign: "center",
            opacity: nextOp,
          }}
        >
          {next_text}
        </div>
      )}
    </AbsoluteFill>
  );
};

export const LyricLineSchema = {
  text: { type: "string", required: true },
  next_text: { type: "string", required: false },
  mode: { type: "enum", values: ["bold", "italic", "minimal"], required: false },
  pulse_frames: { type: "number", required: false },
} as const;
