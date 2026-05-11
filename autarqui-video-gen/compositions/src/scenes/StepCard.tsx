/**
 * StepCard — numbered step with optional icon/screenshot.
 *
 * Use for: "how it works in 5 steps", tutorial, onboarding.
 */

import * as React from "react";
import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface StepCardProps {
  step_number: number | string;
  /** Total steps for "X de Y" */
  total_steps?: number;
  title: string;
  body?: string;
  /** Optional image (icon or screenshot) shown above title */
  image_src?: string;
  image_aspect?: "square" | "16:9" | "9:16";
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const StepCard: React.FC<StepCardProps> = ({
  step_number,
  total_steps,
  title,
  body,
  image_src,
  image_aspect = "16:9",
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);
  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);

  const numOp = fadeIn(frame, 0, inFrames * 0.5);
  const imgOp = fadeIn(frame, Math.round(inFrames * 0.4), inFrames * 0.8);
  const titleOp = fadeIn(frame, Math.round(inFrames * 0.7), inFrames);
  const bodyOp = fadeIn(frame, Math.round(inFrames * 1.1), inFrames);

  const aspectStyle =
    image_aspect === "square" ? { width: 700, height: 700 } :
    image_aspect === "9:16" ? { width: 540, height: 960 } :
    { width: 900, height: 506 };

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: "center",
        padding: "8%",
        opacity: op,
      }}
    >
      <div
        style={{
          fontFamily: fonts.body,
          fontWeight: 500,
          fontSize: 24,
          letterSpacing: "0.22em",
          textTransform: "uppercase",
          color: t.colors.muted,
          marginBottom: image_src ? 28 : 22,
          opacity: numOp,
        }}
      >
        Paso {step_number}{total_steps ? ` de ${total_steps}` : ""}
      </div>

      {image_src && (
        <div
          style={{
            ...aspectStyle,
            maxWidth: "92%",
            marginBottom: 36,
            opacity: imgOp,
            border: `1px solid ${t.colors.ruleSoft}`,
            overflow: "hidden",
            backgroundColor: t.colors.surface,
          }}
        >
          <Img
            src={image_src}
            style={{ width: "100%", height: "100%", objectFit: "cover" }}
          />
        </div>
      )}

      <div
        style={{
          fontFamily: fonts.display,
          fontWeight: 500,
          fontSize: 72,
          lineHeight: 1.12,
          letterSpacing: "-0.018em",
          color: t.colors.heading,
          textAlign: "center",
          maxWidth: "92%",
          opacity: titleOp,
        }}
      >
        {title}
      </div>

      {body && (
        <div
          style={{
            marginTop: 26,
            fontFamily: fonts.body,
            fontWeight: 400,
            fontSize: 28,
            lineHeight: 1.5,
            color: t.colors.muted,
            textAlign: "center",
            maxWidth: "84%",
            opacity: bodyOp,
          }}
        >
          {body}
        </div>
      )}
    </AbsoluteFill>
  );
};

export const StepCardSchema = {
  step_number: { type: "string", required: true },
  total_steps: { type: "number", required: false },
  title: { type: "string", required: true },
  body: { type: "string", required: false },
  image_src: { type: "string", required: false },
  image_aspect: { type: "enum", values: ["square", "16:9", "9:16"], required: false },
} as const;
