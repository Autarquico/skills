/**
 * ScreenAnnotation — screenshot with arrows/circles/callouts overlaid.
 *
 * Use for: tutorial, explainer with screen captures.
 */

import * as React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export type Annotation =
  | { type: "circle"; x_pct: number; y_pct: number; size_pct: number; appear_at_s?: number; color?: string }
  | { type: "arrow"; from_x_pct: number; from_y_pct: number; to_x_pct: number; to_y_pct: number; appear_at_s?: number; color?: string }
  | { type: "callout"; x_pct: number; y_pct: number; text: string; appear_at_s?: number; color?: string };

export interface ScreenAnnotationProps {
  screenshot_src: string;
  annotations: Annotation[];
  /** Optional caption/eyebrow at top */
  caption?: string;
  /** Background bar color when image doesn't fill (default: tokens.surface) */
  letterbox_color?: string;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const ScreenAnnotation: React.FC<ScreenAnnotationProps> = ({
  screenshot_src,
  annotations,
  caption,
  letterbox_color,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);
  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);

  const captionOp = fadeIn(frame, 0, inFrames * 0.7);
  const screenOp = fadeIn(frame, Math.round(inFrames * 0.4), inFrames * 0.8);

  const accent = t.colors.accent[0]?.hex || "#e8a560";

  return (
    <AbsoluteFill
      style={{
        backgroundColor: letterbox_color || t.colors.surface,
        justifyContent: "center",
        alignItems: "center",
        padding: caption ? "120px 6% 6% 6%" : "6%",
        opacity: op,
      }}
    >
      {caption && (
        <div
          style={{
            position: "absolute",
            top: 50,
            left: 0,
            right: 0,
            textAlign: "center",
            fontFamily: fonts.body,
            fontWeight: 500,
            fontSize: 30,
            color: t.colors.heading,
            letterSpacing: "-0.005em",
            opacity: captionOp,
          }}
        >
          {caption}
        </div>
      )}

      <div
        style={{
          position: "relative",
          width: "100%",
          maxWidth: "94%",
          maxHeight: "100%",
          opacity: screenOp,
        }}
      >
        <Img
          src={screenshot_src}
          style={{ width: "100%", height: "auto", display: "block", border: `1px solid ${t.colors.rule}` }}
        />

        {/* Annotations overlaid in absolute coords (% of image) */}
        <svg
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }}
        >
          {annotations.map((ann, i) => {
            const appearF = Math.round((ann.appear_at_s || 0) * fps);
            const annOp = fadeIn(frame, appearF, 12);
            if (annOp === 0) return null;
            const color = ann.color || accent;

            if (ann.type === "circle") {
              return (
                <circle
                  key={i}
                  cx={ann.x_pct}
                  cy={ann.y_pct}
                  r={ann.size_pct / 2}
                  fill="none"
                  stroke={color}
                  strokeWidth={0.4}
                  opacity={annOp}
                />
              );
            }
            if (ann.type === "arrow") {
              const dx = ann.to_x_pct - ann.from_x_pct;
              const dy = ann.to_y_pct - ann.from_y_pct;
              const len = Math.sqrt(dx * dx + dy * dy);
              const ux = dx / len;
              const uy = dy / len;
              const headSize = 1.5;
              const px = -uy;
              const py = ux;
              const tipX = ann.to_x_pct;
              const tipY = ann.to_y_pct;
              return (
                <g key={i} opacity={annOp}>
                  <line
                    x1={ann.from_x_pct}
                    y1={ann.from_y_pct}
                    x2={tipX - ux * headSize}
                    y2={tipY - uy * headSize}
                    stroke={color}
                    strokeWidth={0.4}
                  />
                  <polygon
                    points={`${tipX},${tipY} ${tipX - ux * headSize - px * headSize / 2},${tipY - uy * headSize - py * headSize / 2} ${tipX - ux * headSize + px * headSize / 2},${tipY - uy * headSize + py * headSize / 2}`}
                    fill={color}
                  />
                </g>
              );
            }
            return null;
          })}
        </svg>

        {/* Callouts as DOM (text rendering inside SVG is finicky) */}
        {annotations.map((ann, i) => {
          if (ann.type !== "callout") return null;
          const appearF = Math.round((ann.appear_at_s || 0) * fps);
          const annOp = fadeIn(frame, appearF, 12);
          if (annOp === 0) return null;
          const color = ann.color || accent;
          return (
            <div
              key={i}
              style={{
                position: "absolute",
                left: `${ann.x_pct}%`,
                top: `${ann.y_pct}%`,
                transform: "translate(-50%, -120%)",
                backgroundColor: color,
                color: "#000",
                fontFamily: fonts.body,
                fontWeight: 500,
                fontSize: 22,
                padding: "8px 16px",
                opacity: annOp,
                whiteSpace: "nowrap",
              }}
            >
              {ann.text}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const ScreenAnnotationSchema = {
  screenshot_src: { type: "string", required: true },
  annotations: { type: "array", required: true, of: "object" },
  caption: { type: "string", required: false },
  letterbox_color: { type: "string", required: false },
} as const;
