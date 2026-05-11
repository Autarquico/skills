/**
 * HeroTitle — Brand intro card.
 *
 * Renders: optional umbrella logo (e.g. α) + wordmark + eyebrow + drawing rule
 * + optional product logo + product wordmark.
 *
 * Used as opening of most videos.
 */

import * as React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface HeroTitleProps {
  /** Path to umbrella brand logo (e.g. α) under public/. */
  umbrella_logo?: string;
  /** Wordmark text shown next to umbrella logo. */
  umbrella_wordmark?: string;
  /** Splittable wordmark: "autarqui" + ".co" with .co in muted. */
  umbrella_wordmark_ext?: string;
  /** Eyebrow text — e.g. "PRESENTA" or "PRESENTA · DELTA". */
  eyebrow?: string;
  /** Path to product logo (e.g. δ, σ) under public/. */
  product_logo?: string;
  /** Product wordmark — usually uppercase short word. */
  product_wordmark?: string;
  /** Layout: stacked vertically (vertical/IG) or inline (horizontal/web). */
  layout?: "vertical" | "horizontal";
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const HeroTitle: React.FC<HeroTitleProps> = ({
  umbrella_logo,
  umbrella_wordmark,
  umbrella_wordmark_ext,
  eyebrow,
  product_logo,
  product_wordmark,
  layout = "vertical",
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames, width } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);

  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);
  const umbrellaOp = fadeIn(frame, 0, inFrames);
  const eyebrowOp = fadeIn(frame, Math.round(inFrames * 0.7), inFrames);
  const productOp = fadeIn(frame, Math.round(inFrames * 1.3), inFrames);
  const ruleW = interpolate(frame, [Math.round(inFrames * 0.9), Math.round(inFrames * 2.5)], [0, 60], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const isVertical = layout === "vertical";

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: isVertical ? "center" : "flex-start",
        paddingLeft: isVertical ? 0 : "8%",
        paddingRight: isVertical ? 0 : "8%",
        opacity: op,
      }}
    >
      {/* Umbrella row */}
      {(umbrella_logo || umbrella_wordmark) && (
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 22,
            opacity: umbrellaOp,
            marginBottom: isVertical ? 50 : 36,
          }}
        >
          {umbrella_logo && (
            <Img src={staticFile(umbrella_logo)} style={{ width: 76, height: 76 }} />
          )}
          {umbrella_wordmark && (
            <div style={{ fontFamily: fonts.body, fontWeight: 500, fontSize: 30, color: t.colors.heading }}>
              {umbrella_wordmark}
              {umbrella_wordmark_ext && (
                <span style={{ color: t.colors.muted, fontWeight: 400 }}>{umbrella_wordmark_ext}</span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Eyebrow + rule */}
      {eyebrow && (
        <>
          <div
            style={{
              fontFamily: fonts.body,
              fontWeight: 500,
              fontSize: 22,
              letterSpacing: "0.32em",
              textTransform: "uppercase",
              color: t.colors.muted,
              marginBottom: 24,
              opacity: eyebrowOp,
            }}
          >
            {eyebrow}
          </div>
          <div
            style={{
              height: 1,
              width: `${ruleW}%`,
              maxWidth: isVertical ? 280 : 200,
              backgroundColor: t.colors.rule,
              marginBottom: isVertical ? 50 : 36,
            }}
          />
        </>
      )}

      {/* Product row */}
      {product_logo && (
        <Img
          src={staticFile(product_logo)}
          style={{
            width: isVertical ? 220 : 92,
            height: isVertical ? 220 : 92,
            opacity: productOp,
            marginBottom: isVertical ? 30 : 0,
            marginRight: isVertical ? 0 : 28,
          }}
        />
      )}
      {product_wordmark && (
        <div
          style={{
            fontFamily: fonts.body,
            fontWeight: 500,
            fontSize: isVertical ? 64 : 64,
            color: t.colors.heading,
            letterSpacing: "0.18em",
            opacity: productOp,
            display: isVertical ? undefined : "inline-block",
          }}
        >
          {product_wordmark}
        </div>
      )}
    </AbsoluteFill>
  );
};

export const HeroTitleSchema = {
  umbrella_logo: { type: "string", required: false },
  umbrella_wordmark: { type: "string", required: false },
  umbrella_wordmark_ext: { type: "string", required: false },
  eyebrow: { type: "string", required: false },
  product_logo: { type: "string", required: false },
  product_wordmark: { type: "string", required: false },
  layout: { type: "enum", values: ["vertical", "horizontal"], required: false },
} as const;
