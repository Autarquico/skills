/**
 * StatReveal — Single big number with label below.
 *
 * Pattern: italic Lora-display number, calm count-up, label in muted Poppins.
 */

import * as React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface StatRevealProps {
  /** Final value to show. e.g. "8h", "< 10s", "47", "€1.840" */
  value: string;
  /** Label under the number */
  label: string;
  /** Optional eyebrow above the value */
  eyebrow?: string;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const StatReveal: React.FC<StatRevealProps> = ({
  value,
  label,
  eyebrow,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);

  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);
  const eyebrowOp = fadeIn(frame, 0, Math.round(inFrames * 0.6));
  const valueOp = fadeIn(frame, Math.round(inFrames * 0.4), inFrames);
  const labelOp = fadeIn(frame, Math.round(inFrames * 0.9), inFrames);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: "center",
        opacity: op,
      }}
    >
      {eyebrow && (
        <div
          style={{
            fontFamily: fonts.body,
            fontWeight: 500,
            fontSize: 22,
            letterSpacing: "0.18em",
            textTransform: "uppercase",
            color: t.colors.muted,
            marginBottom: 28,
            opacity: eyebrowOp,
          }}
        >
          {eyebrow}
        </div>
      )}
      <div
        style={{
          fontFamily: fonts.displayItalic,
          fontStyle: "italic",
          fontWeight: 500,
          fontSize: 220,
          lineHeight: 1,
          color: t.colors.heading,
          letterSpacing: "-0.02em",
          opacity: valueOp,
        }}
      >
        {value}
      </div>
      <div
        style={{
          marginTop: 34,
          fontFamily: fonts.body,
          fontWeight: 400,
          fontSize: 32,
          color: t.colors.muted,
          maxWidth: "80%",
          textAlign: "center",
          lineHeight: 1.3,
          opacity: labelOp,
        }}
      >
        {label}
      </div>
    </AbsoluteFill>
  );
};

export const StatRevealSchema = {
  value: { type: "string", required: true },
  label: { type: "string", required: true },
  eyebrow: { type: "string", required: false },
} as const;
