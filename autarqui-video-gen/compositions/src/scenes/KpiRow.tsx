/**
 * KpiRow — Horizontal row of KPI cards. Tokenized.
 *
 * Each card has: top-border accent, icon placeholder, big number, label.
 */

import * as React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface KpiCard {
  value: string;
  label: string;
  /** Hex accent color for top border. If absent, uses neutral rule. */
  accent?: string;
}

export interface KpiRowProps {
  cards: KpiCard[];
  /** Optional eyebrow above the row (e.g. "EN LOS PRIMEROS 90 DÍAS") */
  eyebrow?: string;
  /** Layout: stacked vertically (mobile) or horizontal (desktop) */
  layout?: "horizontal" | "vertical";
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const KpiRow: React.FC<KpiRowProps> = ({
  cards,
  eyebrow,
  layout = "horizontal",
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

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: "flex-start",
        paddingLeft: "8%",
        paddingRight: "8%",
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
            marginBottom: 36,
            opacity: eyebrowOp,
          }}
        >
          {eyebrow}
        </div>
      )}
      <div
        style={{
          display: layout === "horizontal" ? "flex" : "flex",
          flexDirection: layout === "horizontal" ? "row" : "column",
          gap: 24,
          width: "100%",
        }}
      >
        {cards.map((card, i) => {
          const cardOp = fadeIn(frame, Math.round(inFrames * 0.6) + i * Math.round(inFrames * 0.5), inFrames);
          const accent = card.accent ?? t.colors.rule;
          return (
            <div
              key={i}
              style={{
                flex: 1,
                border: `1px solid ${t.colors.ruleSoft}`,
                borderTop: `3px solid ${accent}`,
                borderRadius: 8,
                padding: layout === "horizontal" ? "26px 28px" : "22px 24px",
                backgroundColor: t.colors.bg,
                opacity: cardOp,
              }}
            >
              <div
                style={{
                  fontFamily: fonts.displayItalic,
                  fontStyle: "italic",
                  fontWeight: 500,
                  fontSize: layout === "horizontal" ? 100 : 80,
                  lineHeight: 1,
                  color: t.colors.heading,
                  letterSpacing: "-0.02em",
                  marginBottom: 14,
                }}
              >
                {card.value}
              </div>
              <div
                style={{
                  fontFamily: fonts.body,
                  fontWeight: 400,
                  fontSize: 22,
                  color: t.colors.muted,
                  lineHeight: 1.35,
                }}
              >
                {card.label}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const KpiRowSchema = {
  cards: { type: "array", required: true, of: "object" },
  eyebrow: { type: "string", required: false },
  layout: { type: "enum", values: ["horizontal", "vertical"], required: false },
} as const;
