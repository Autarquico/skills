/**
 * ClosingCard — Final logo + product wordmark + brand wordmark stacked.
 *
 * Pattern: large logo (subtle scale-in) + uppercase product wordmark +
 * lowercase brand wordmark with .ext muted. Lands in silence.
 */

import * as React from "react";
import { AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface ClosingCardProps {
  /** Path to logo under public/. If empty/omitted, only wordmark renders. */
  logo_path?: string;
  /** Product wordmark — usually uppercase short word like "DELTA" or "SIGMA". */
  product_wordmark?: string;
  /** Brand wordmark — e.g. "autarqui". */
  brand_wordmark: string;
  /** Extension of brand wordmark in muted color — e.g. ".co". */
  brand_wordmark_ext?: string;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const ClosingCard: React.FC<ClosingCardProps> = ({
  logo_path,
  product_wordmark,
  brand_wordmark,
  brand_wordmark_ext,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames } = defaultPacing(t, fps);

  // Closing card: only fade in, no fade out (let it land and stay)
  const op = fadeIn(frame, 0, inFrames);
  const logoOp = fadeIn(frame, 0, inFrames);
  const logoScale = interpolate(frame, [0, Math.round(inFrames * 2)], [0.94, 1.0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const productOp = fadeIn(frame, Math.round(inFrames), Math.round(inFrames * 0.7));
  const brandOp = fadeIn(frame, Math.round(inFrames * 1.5), Math.round(inFrames * 0.7));

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: "center",
        opacity: op,
      }}
    >
      {logo_path && (
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
      )}
      {product_wordmark && (
        <div
          style={{
            marginTop: t.layout.closing.spacing_px,
            fontFamily: fonts.body,
            fontWeight: 500,
            fontSize: 64,
            color: t.colors.heading,
            letterSpacing: "0.18em",
            textTransform: "uppercase",
            opacity: productOp,
          }}
        >
          {product_wordmark}
        </div>
      )}
      <div
        style={{
          marginTop: product_wordmark ? 32 : t.layout.closing.spacing_px,
          fontFamily: fonts.body,
          fontWeight: 500,
          fontSize: 34,
          color: t.colors.heading,
          letterSpacing: "-0.005em",
          opacity: brandOp,
        }}
      >
        {brand_wordmark}
        {brand_wordmark_ext && (
          <span style={{ color: t.colors.muted, fontWeight: 400 }}>{brand_wordmark_ext}</span>
        )}
      </div>
    </AbsoluteFill>
  );
};

export const ClosingCardSchema = {
  logo_path: { type: "string", required: true },
  product_wordmark: { type: "string", required: false },
  brand_wordmark: { type: "string", required: true },
  brand_wordmark_ext: { type: "string", required: false },
} as const;
