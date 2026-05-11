/**
 * QuoteCard — testimonial: avatar + italic quote + attribution.
 *
 * Avatar: either a photo URL OR initials in a circle.
 */

import * as React from "react";
import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface QuoteCardProps {
  quote: string;
  /** Person name */
  attribution_name: string;
  /** Role / company / etc */
  attribution_role?: string;
  /** Avatar: either a URL to a photo, or null/empty (uses initials) */
  avatar_src?: string;
  /** Initials shown in circle when avatar_src missing */
  initials?: string;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const QuoteCard: React.FC<QuoteCardProps> = ({
  quote,
  attribution_name,
  attribution_role,
  avatar_src,
  initials,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);
  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);

  const avatarOp = fadeIn(frame, 0, inFrames * 0.7);
  const quoteOp = fadeIn(frame, Math.round(inFrames * 0.4), inFrames);
  const attribOp = fadeIn(frame, Math.round(inFrames * 1.0), inFrames * 0.7);

  const inits = initials || attribution_name.split(" ").map((s) => s[0]).join("").slice(0, 2).toUpperCase();

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
      {/* Avatar */}
      <div style={{ marginBottom: 36, opacity: avatarOp }}>
        {avatar_src ? (
          <Img
            src={avatar_src}
            style={{
              width: 200,
              height: 200,
              borderRadius: "50%",
              objectFit: "cover",
            }}
          />
        ) : (
          <div
            style={{
              width: 200,
              height: 200,
              borderRadius: "50%",
              backgroundColor: t.colors.surface,
              border: `2px solid ${t.colors.rule}`,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontFamily: fonts.body,
              fontWeight: 500,
              fontSize: 64,
              color: t.colors.heading,
              letterSpacing: "0.04em",
            }}
          >
            {inits}
          </div>
        )}
      </div>

      {/* Quote */}
      <div
        style={{
          fontFamily: fonts.displayItalic,
          fontStyle: "italic",
          fontWeight: 400,
          fontSize: 60,
          lineHeight: 1.32,
          letterSpacing: "-0.012em",
          color: t.colors.heading,
          textAlign: "center",
          maxWidth: "92%",
          marginBottom: 40,
          opacity: quoteOp,
        }}
      >
        “{quote}”
      </div>

      {/* Attribution */}
      <div style={{ opacity: attribOp, textAlign: "center" }}>
        <div
          style={{
            fontFamily: fonts.body,
            fontWeight: 600,
            fontSize: 30,
            color: t.colors.heading,
          }}
        >
          {attribution_name}
        </div>
        {attribution_role && (
          <div
            style={{
              marginTop: 8,
              fontFamily: fonts.body,
              fontWeight: 400,
              fontSize: 22,
              color: t.colors.muted,
              letterSpacing: "0.02em",
            }}
          >
            {attribution_role}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

export const QuoteCardSchema = {
  quote: { type: "string", required: true },
  attribution_name: { type: "string", required: true },
  attribution_role: { type: "string", required: false },
  avatar_src: { type: "string", required: false },
  initials: { type: "string", required: false },
} as const;
