/**
 * WaveformOverlay — animated audio waveform visualization.
 *
 * Two modes:
 *   - "static": static waveform PNG (pre-rendered by tools/audio/waveform-render.sh)
 *               with an animated playhead crossing it
 *   - "synthetic": procedurally drawn waveform (deterministic, no asset needed)
 *
 * Optional quote text above the waveform — for podcast resumen / podcast highlight.
 */

import * as React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface WaveformOverlayProps {
  mode?: "static" | "synthetic";
  /** Path to waveform PNG (when mode=static). Generate via tools/audio/waveform-render.sh */
  waveform_src?: string;
  /** Quote / pull-text shown above waveform */
  quote?: string;
  /** Attribution */
  attribution?: string;
  /** Eyebrow */
  eyebrow?: string;
  /** Whether playhead animates across (visualizes audio playback) */
  show_playhead?: boolean;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const WaveformOverlay: React.FC<WaveformOverlayProps> = ({
  mode = "synthetic",
  waveform_src,
  quote,
  attribution,
  eyebrow,
  show_playhead = true,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);
  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);

  const eyebrowOp = fadeIn(frame, 0, inFrames * 0.6);
  const quoteOp = fadeIn(frame, Math.round(inFrames * 0.4), inFrames);
  const waveOp = fadeIn(frame, Math.round(inFrames * 0.8), inFrames);
  const attribOp = fadeIn(frame, Math.round(inFrames * 1.4), inFrames);

  const playheadX = show_playhead
    ? interpolate(frame, [0, total], [0, 100], { extrapolateRight: "clamp" })
    : 0;

  const accent = t.colors.accent[0]?.hex || t.colors.heading;

  // Synthetic waveform: generate stable bar heights from a hash function
  const syntheticBars = React.useMemo(() => {
    const bars = 80;
    return Array.from({ length: bars }, (_, i) => {
      const a = Math.sin(i * 0.31) * 0.4 + Math.sin(i * 0.83) * 0.3 + Math.sin(i * 1.7) * 0.15;
      return Math.max(0.08, Math.abs(a));
    });
  }, []);

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
      {eyebrow && (
        <div
          style={{
            fontFamily: fonts.body,
            fontWeight: 500,
            fontSize: 22,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: t.colors.muted,
            marginBottom: 32,
            opacity: eyebrowOp,
            textAlign: "center",
          }}
        >
          {eyebrow}
        </div>
      )}

      {quote && (
        <div
          style={{
            fontFamily: fonts.displayItalic,
            fontStyle: "italic",
            fontWeight: 500,
            fontSize: 56,
            lineHeight: 1.28,
            letterSpacing: "-0.012em",
            color: t.colors.heading,
            textAlign: "center",
            maxWidth: "92%",
            marginBottom: 60,
            opacity: quoteOp,
          }}
        >
          “{quote}”
        </div>
      )}

      {/* Waveform */}
      <div style={{ width: "84%", height: 240, position: "relative", opacity: waveOp }}>
        {mode === "static" && waveform_src ? (
          <Img
            src={waveform_src}
            style={{ width: "100%", height: "100%", objectFit: "fill" }}
          />
        ) : (
          <svg viewBox="0 0 100 50" preserveAspectRatio="none" width="100%" height="100%">
            {syntheticBars.map((h, i) => {
              const x = (i / syntheticBars.length) * 100;
              const w = 100 / syntheticBars.length - 0.3;
              const barH = h * 50;
              const passed = playheadX > x;
              return (
                <rect
                  key={i}
                  x={x}
                  y={(50 - barH) / 2}
                  width={w}
                  height={barH}
                  fill={passed ? accent : t.colors.faint}
                />
              );
            })}
          </svg>
        )}
        {show_playhead && (
          <div
            style={{
              position: "absolute",
              top: -10,
              bottom: -10,
              left: `${playheadX}%`,
              width: 2,
              backgroundColor: t.colors.heading,
            }}
          />
        )}
      </div>

      {attribution && (
        <div
          style={{
            marginTop: 38,
            fontFamily: fonts.body,
            fontWeight: 500,
            fontSize: 22,
            color: t.colors.muted,
            letterSpacing: "0.04em",
            textAlign: "center",
            opacity: attribOp,
          }}
        >
          {attribution}
        </div>
      )}
    </AbsoluteFill>
  );
};

export const WaveformOverlaySchema = {
  mode: { type: "enum", values: ["static", "synthetic"], required: false },
  waveform_src: { type: "string", required: false },
  quote: { type: "string", required: false },
  attribution: { type: "string", required: false },
  eyebrow: { type: "string", required: false },
  show_playhead: { type: "boolean", required: false },
} as const;
