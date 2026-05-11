/**
 * LineChart — animated line chart with progressive reveal.
 *
 * Line draws left-to-right via SVG strokeDashoffset.
 * Use for: trends over time, growth, comparison series.
 */

import * as React from "react";
import { AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface LineChartProps {
  title?: string;
  subtitle?: string;
  /** Data series — values normalized internally */
  points: number[];
  /** X-axis labels (one per point or every N) */
  x_labels?: string[];
  /** Highlight value at end (e.g. final number) */
  highlight_end?: string;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const LineChart: React.FC<LineChartProps> = ({
  title,
  subtitle,
  points,
  x_labels = [],
  highlight_end,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);
  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);

  const titleOp = fadeIn(frame, 0, inFrames * 0.7);
  const subtitleOp = fadeIn(frame, Math.round(inFrames * 0.4), inFrames * 0.7);

  const drawProgress = interpolate(
    frame,
    [Math.round(inFrames * 0.6), Math.round(inFrames * 0.6) + inFrames * 1.5],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
  );

  const max = Math.max(...points);
  const min = Math.min(...points);
  const accent = t.colors.accent[0]?.hex || t.colors.heading;
  const W = 100;
  const H = 50;

  // Build SVG path
  const path = points
    .map((v, i) => {
      const x = (i / (points.length - 1)) * W;
      const y = H - ((v - min) / Math.max(1, max - min)) * H;
      return `${i === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");

  // Compute path length for stroke-dasharray (rough estimate)
  const pathLength = 200; // SVG normalizes; we use a big number and dasharray controls
  const dashOffset = pathLength * (1 - drawProgress);

  // End point for highlight callout
  const endX = ((points.length - 1) / (points.length - 1)) * W;
  const endY = H - ((points[points.length - 1] - min) / Math.max(1, max - min)) * H;
  const highlightOp = fadeIn(frame, Math.round(inFrames * 1.8), inFrames);

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
      {title && (
        <div
          style={{
            fontFamily: fonts.display,
            fontWeight: 500,
            fontSize: 56,
            color: t.colors.heading,
            textAlign: "center",
            letterSpacing: "-0.018em",
            marginBottom: subtitle ? 12 : 36,
            opacity: titleOp,
          }}
        >
          {title}
        </div>
      )}
      {subtitle && (
        <div
          style={{
            fontFamily: fonts.body,
            fontWeight: 400,
            fontSize: 22,
            color: t.colors.muted,
            textAlign: "center",
            marginBottom: 48,
            opacity: subtitleOp,
            letterSpacing: "0.04em",
          }}
        >
          {subtitle}
        </div>
      )}

      <div style={{ width: "92%", height: 540, position: "relative" }}>
        <svg viewBox={`0 -4 ${W} ${H + 8}`} preserveAspectRatio="none" width="100%" height="100%">
          {/* baseline */}
          <line x1={0} y1={H} x2={W} y2={H} stroke={t.colors.rule} strokeWidth={0.3} />
          {/* main line */}
          <path
            d={path}
            fill="none"
            stroke={accent}
            strokeWidth={0.8}
            strokeDasharray={pathLength}
            strokeDashoffset={dashOffset}
            strokeLinejoin="round"
            strokeLinecap="round"
            vectorEffect="non-scaling-stroke"
          />
          {/* end dot */}
          {drawProgress > 0.95 && (
            <circle cx={endX} cy={endY} r={1.2} fill={accent} opacity={highlightOp} />
          )}
        </svg>

        {highlight_end && drawProgress > 0.95 && (
          <div
            style={{
              position: "absolute",
              right: 0,
              top: -10,
              fontFamily: fonts.display,
              fontWeight: 500,
              fontSize: 56,
              color: accent,
              letterSpacing: "-0.02em",
              opacity: highlightOp,
            }}
          >
            {highlight_end}
          </div>
        )}

        {/* X labels */}
        {x_labels.length > 0 && (
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              marginTop: 14,
              fontFamily: fonts.body,
              fontWeight: 400,
              fontSize: 18,
              color: t.colors.muted,
              letterSpacing: "0.04em",
            }}
          >
            {x_labels.map((l, i) => (
              <div key={i}>{l}</div>
            ))}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

export const LineChartSchema = {
  title: { type: "string", required: false },
  subtitle: { type: "string", required: false },
  points: { type: "array", required: true, of: "number" },
  x_labels: { type: "array", required: false, of: "string" },
  highlight_end: { type: "string", required: false },
} as const;
