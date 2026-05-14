/**
 * SplitScreen — two-column comparison (before/after, with/without, X vs Y).
 *
 * Each side: photo + label. Optional center divider.
 */

import * as React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface SplitScreenProps {
  left: { photo_src: string; label: string; sublabel?: string };
  right: { photo_src: string; label: string; sublabel?: string };
  /** Layout: "horizontal" splits left/right, "vertical" splits top/bottom (better for 9:16) */
  layout?: "horizontal" | "vertical";
  /** Show wipe animation that reveals right side from left */
  wipe_reveal?: boolean;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const SplitScreen: React.FC<SplitScreenProps> = ({
  left,
  right,
  layout = "vertical",
  wipe_reveal = true,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);
  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);

  const wipeProgress = wipe_reveal
    ? interpolate(frame, [Math.round(inFrames * 0.3), inFrames * 2], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 1;

  const leftLabelOp = fadeIn(frame, 0, inFrames);
  const rightLabelOp = fadeIn(frame, Math.round(inFrames * 1.5), inFrames);

  const isVertical = layout === "vertical";

  const Side: React.FC<{
    content: { photo_src: string; label: string; sublabel?: string };
    labelOp: number;
    eyebrowText: string;
    eyebrowColor: string;
  }> = ({ content, labelOp, eyebrowText, eyebrowColor }) => (
    <div style={{ position: "relative", width: "100%", height: "100%" }}>
      <Img
        src={content.photo_src}
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }}
      />
      <div style={{ position: "absolute", inset: 0, backgroundColor: "rgba(0,0,0,0.30)" }} />
      <div
        style={{
          position: "absolute",
          inset: 0,
          padding: "8%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "flex-end",
          alignItems: "flex-start",
          opacity: labelOp,
        }}
      >
        <div
          style={{
            fontFamily: fonts.body,
            fontWeight: 600,
            fontSize: 22,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: eyebrowColor,
            marginBottom: 14,
          }}
        >
          {eyebrowText}
        </div>
        <div
          style={{
            fontFamily: fonts.display,
            fontWeight: 500,
            fontSize: 72,
            lineHeight: 1.05,
            letterSpacing: "-0.02em",
            color: "#ffffff",
          }}
        >
          {content.label}
        </div>
        {content.sublabel && (
          <div
            style={{
              marginTop: 14,
              fontFamily: fonts.displayItalic,
              fontStyle: "italic",
              fontSize: 30,
              color: "rgba(255,255,255,0.85)",
              maxWidth: "92%",
            }}
          >
            {content.sublabel}
          </div>
        )}
      </div>
    </div>
  );

  const accentRed = t.colors.accent[0]?.hex || "#e8a560";
  const accentGreen = "#a3d9a5";

  return (
    <AbsoluteFill style={{ backgroundColor: t.colors.heading, opacity: op }}>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: isVertical ? "1fr" : "1fr 1fr",
          gridTemplateRows: isVertical ? "1fr 1fr" : "1fr",
          width: "100%",
          height: "100%",
        }}
      >
        <div style={{ overflow: "hidden" }}>
          <Side content={left} labelOp={leftLabelOp} eyebrowText="ANTES" eyebrowColor={accentRed} />
        </div>
        <div
          style={{
            overflow: "hidden",
            clipPath: wipe_reveal
              ? isVertical
                ? `inset(${(1 - wipeProgress) * 100}% 0 0 0)`
                : `inset(0 0 0 ${(1 - wipeProgress) * 100}%)`
              : undefined,
          }}
        >
          <Side content={right} labelOp={rightLabelOp} eyebrowText="DESPUÉS" eyebrowColor={accentGreen} />
        </div>
      </div>
      {/* Center divider line */}
      <div
        style={{
          position: "absolute",
          ...(isVertical
            ? { left: 0, right: 0, top: "50%", height: 2, transform: "translateY(-50%)" }
            : { top: 0, bottom: 0, left: "50%", width: 2, transform: "translateX(-50%)" }),
          backgroundColor: "#ffffff",
          opacity: 0.6,
        }}
      />
    </AbsoluteFill>
  );
};

export const SplitScreenSchema = {
  left: { type: "object", required: true },
  right: { type: "object", required: true },
  layout: { type: "enum", values: ["horizontal", "vertical"], required: false },
  wipe_reveal: { type: "boolean", required: false },
} as const;
