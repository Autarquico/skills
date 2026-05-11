/**
 * PriceCard — offer/product card with price prominent.
 *
 * Use for: anuncio de oferta, product launch with price, sale.
 */

import * as React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface PriceCardProps {
  product_name: string;
  price: string;
  /** Optional struck-through old price (e.g. "€199") */
  was_price?: string;
  /** Eyebrow (e.g. "OFERTA · ÚLTIMOS 3 DÍAS") */
  eyebrow?: string;
  /** Short tagline below price */
  tagline?: string;
  /** CTA text (e.g. "autarqui.co/oferta") */
  cta?: string;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const PriceCard: React.FC<PriceCardProps> = ({
  product_name,
  price,
  was_price,
  eyebrow,
  tagline,
  cta,
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
  const productOp = fadeIn(frame, Math.round(inFrames * 0.5), inFrames * 0.8);
  const priceOp = fadeIn(frame, Math.round(inFrames * 0.9), inFrames);
  const taglineOp = fadeIn(frame, Math.round(inFrames * 1.4), inFrames);
  const ctaOp = fadeIn(frame, Math.round(inFrames * 1.8), inFrames);

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
            color: t.colors.accent[0]?.hex || t.colors.muted,
            marginBottom: 26,
            opacity: eyebrowOp,
          }}
        >
          {eyebrow}
        </div>
      )}

      <div
        style={{
          fontFamily: fonts.display,
          fontWeight: 500,
          fontSize: 64,
          lineHeight: 1.1,
          color: t.colors.heading,
          marginBottom: 30,
          textAlign: "center",
          maxWidth: "92%",
          opacity: productOp,
        }}
      >
        {product_name}
      </div>

      {/* Price block */}
      <div style={{ display: "flex", alignItems: "baseline", gap: 28, marginBottom: tagline ? 26 : 40, opacity: priceOp }}>
        {was_price && (
          <div
            style={{
              fontFamily: fonts.display,
              fontWeight: 400,
              fontSize: 56,
              color: t.colors.faint,
              textDecoration: "line-through",
            }}
          >
            {was_price}
          </div>
        )}
        <div
          style={{
            fontFamily: fonts.displayItalic,
            fontStyle: "italic",
            fontWeight: 500,
            fontSize: 200,
            lineHeight: 1,
            color: t.colors.heading,
            letterSpacing: "-0.02em",
          }}
        >
          {price}
        </div>
      </div>

      {tagline && (
        <div
          style={{
            fontFamily: fonts.body,
            fontWeight: 400,
            fontSize: 28,
            color: t.colors.muted,
            textAlign: "center",
            maxWidth: "84%",
            marginBottom: 50,
            opacity: taglineOp,
          }}
        >
          {tagline}
        </div>
      )}

      {cta && (
        <div
          style={{
            padding: "20px 40px",
            backgroundColor: t.colors.heading,
            color: t.colors.bg,
            fontFamily: fonts.body,
            fontWeight: 500,
            fontSize: 26,
            letterSpacing: "0.04em",
            opacity: ctaOp,
          }}
        >
          {cta}
        </div>
      )}
    </AbsoluteFill>
  );
};

export const PriceCardSchema = {
  product_name: { type: "string", required: true },
  price: { type: "string", required: true },
  was_price: { type: "string", required: false },
  eyebrow: { type: "string", required: false },
  tagline: { type: "string", required: false },
  cta: { type: "string", required: false },
} as const;
