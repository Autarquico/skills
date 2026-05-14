/**
 * BarChart — animated bar chart with reveal.
 *
 * Each bar grows from 0 to its target height with a stagger.
 * Use for: data viz, "el cambio en números", monthly stats.
 */

import * as React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing, easings } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface BarChartProps {
  /** Title above chart */
  title?: string;
  /** Subtitle / unit */
  subtitle?: string;
  /** Bar data: array of {label, value} */
  bars: Array<{ label: string; value: number; highlight?: boolean }>;
  /** Y-axis max — auto if omitted */
  max_value?: number;
  /** Frames between each bar's reveal */
  stagger_frames?: number;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const BarChart: React.FC<BarChartProps> = ({
  title,
  subtitle,
  bars,
  max_value,
  stagger_frames = 6,
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

  const max = max_value ?? Math.max(...bars.map((b) => b.value));
  const accent = t.colors.accent[0]?.hex || t.colors.heading;
  const growDuration = inFrames;

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
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          gap: 20,
          width: "92%",
          height: 600,
          borderBottom: `2px solid ${t.colors.heading}`,
          padding: "0 4% 8px 4%",
        }}
      >
        {bars.map((b, i) => {
          const startF = Math.round(inFrames * 0.6) + i * stagger_frames;
          const localF = frame - startF;
          const grow =
            localF <= 0 ? 0 : localF >= growDuration ? 1 : easings.easeOutCubic(localF / growDuration);
          const h = (b.value / max) * grow * 100;
          const labelOp = fadeIn(frame, startF + Math.round(growDuration * 0.6), Math.round(growDuration * 0.5));
          const valueOp = fadeIn(frame, startF + Math.round(growDuration * 0.7), Math.round(growDuration * 0.5));
          return (
            <div
              key={i}
              style={{
                flex: 1,
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                height: "100%",
                position: "relative",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  bottom: 14,
                  fontFamily: fonts.display,
                  fontWeight: 500,
                  fontSize: 28,
                  color: t.colors.heading,
                  opacity: valueOp,
                }}
              >
                {b.value}
              </div>
              <div style={{ flex: 1, display: "flex", alignItems: "flex-end", width: "100%", justifyContent: "center" }}>
                <div
                  style={{
                    width: "70%",
                    height: `${h}%`,
                    backgroundColor: b.highlight ? accent : t.colors.heading,
                    transition: "none",
                  }}
                />
              </div>
              <div
                style={{
                  marginTop: 14,
                  fontFamily: fonts.body,
                  fontWeight: 500,
                  fontSize: 18,
                  color: t.colors.muted,
                  letterSpacing: "0.04em",
                  textAlign: "center",
                  opacity: labelOp,
                }}
              >
                {b.label}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const BarChartSchema = {
  title: { type: "string", required: false },
  subtitle: { type: "string", required: false },
  bars: { type: "array", required: true, of: "object" },
  max_value: { type: "number", required: false },
  stagger_frames: { type: "number", required: false },
} as const;
