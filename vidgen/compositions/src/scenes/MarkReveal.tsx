/**
 * MarkReveal — Logo + wordmark + tagline reveal (mid-video product reveal).
 *
 * Pattern: scaled logo entrance + wordmark + small italic tagline below.
 */

import * as React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface MarkRevealProps {
  logo_path: string;
  wordmark?: string;
  /** "uppercase" applies wide tracking automatically */
  wordmark_case?: "lowercase" | "uppercase";
  tagline?: string;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const MarkReveal: React.FC<MarkRevealProps> = ({
  logo_path,
  wordmark,
  wordmark_case = "uppercase",
  tagline,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);

  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);
  const logoOp = fadeIn(frame, 0, inFrames);
  const logoScale = interpolate(frame, [0, Math.round(inFrames * 1.5)], [0.94, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const wordOp = fadeIn(frame, Math.round(inFrames * 1.0), Math.round(inFrames * 0.7));
  const taglineOp = fadeIn(frame, Math.round(inFrames * 1.4), Math.round(inFrames * 0.7));

  const isUpper = wordmark_case === "uppercase";

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: "center",
        opacity: op,
      }}
    >
      <Img
        src={staticFile(logo_path)}
        style={{
          width: t.layout.closing.logo_size_px,
          height: t.layout.closing.logo_size_px,
          transform: `scale(${logoScale})`,
          opacity: logoOp,
          display: "block",
        }}
      />
      {wordmark && (
        <div
          style={{
            marginTop: t.layout.closing.spacing_px,
            fontFamily: fonts.body,
            fontWeight: 500,
            fontSize: 56,
            color: t.colors.heading,
            letterSpacing: isUpper ? "0.18em" : "0.04em",
            textTransform: isUpper ? "uppercase" : "lowercase",
            opacity: wordOp,
          }}
        >
          {wordmark}
        </div>
      )}
      {tagline && (
        <div
          style={{
            marginTop: 18,
            fontFamily: fonts.displayItalic,
            fontStyle: "italic",
            fontWeight: 400,
            fontSize: 38,
            color: t.colors.muted,
            opacity: taglineOp,
          }}
        >
          {tagline}
        </div>
      )}
    </AbsoluteFill>
  );
};

export const MarkRevealSchema = {
  logo_path: { type: "string", required: true },
  wordmark: { type: "string", required: false },
  wordmark_case: { type: "enum", values: ["lowercase", "uppercase"], required: false },
  tagline: { type: "string", required: false },
} as const;
