/**
 * PhotoBackground — full-frame photo with optional dark overlay + text overlay.
 *
 * Use for: trailer, anuncio de oferta, hero shots.
 */

import * as React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface PhotoBackgroundProps {
  photo_src: string;
  /** Headline text overlay */
  headline?: string;
  /** Eyebrow above headline */
  eyebrow?: string;
  /** Subline below headline */
  subline?: string;
  /** Position of text overlay */
  text_position?: "center" | "bottom-left" | "bottom-center" | "top-left";
  /** Darken photo for text legibility (0-1) */
  overlay_opacity?: number;
  /** Apply Ken Burns zoom */
  ken_burns?: boolean;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const PhotoBackground: React.FC<PhotoBackgroundProps> = ({
  photo_src,
  headline,
  eyebrow,
  subline,
  text_position = "bottom-left",
  overlay_opacity = 0.35,
  ken_burns = true,
  scene_duration_frames,
  fonts,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);
  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);

  const eyebrowOp = fadeIn(frame, Math.round(inFrames * 0.4), inFrames * 0.7);
  const headlineOp = fadeIn(frame, Math.round(inFrames * 0.7), inFrames);
  const sublineOp = fadeIn(frame, Math.round(inFrames * 1.2), inFrames);

  const kbScale = ken_burns
    ? interpolate(frame, [0, total], [1.05, 1.18], { extrapolateRight: "clamp" })
    : 1;

  const justify =
    text_position.startsWith("top") ? "flex-start" :
    text_position.startsWith("bottom") ? "flex-end" :
    "center";
  const align =
    text_position.endsWith("left") ? "flex-start" :
    text_position.endsWith("center") ? "center" :
    "flex-end";

  return (
    <AbsoluteFill style={{ backgroundColor: t.colors.heading, opacity: op }}>
      {/* Photo */}
      <Img
        src={photo_src}
        style={{
          position: "absolute",
          inset: 0,
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${kbScale})`,
          transformOrigin: "center center",
        }}
      />
      {/* Dark overlay */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          backgroundColor: t.colors.heading,
          opacity: overlay_opacity,
        }}
      />
      {/* Text */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          padding: "10%",
          display: "flex",
          flexDirection: "column",
          justifyContent: justify,
          alignItems: align,
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
              color: "#ffffff",
              marginBottom: 22,
              opacity: eyebrowOp,
              textAlign: align === "center" ? "center" : "left",
            }}
          >
            {eyebrow}
          </div>
        )}
        {headline && (
          <div
            style={{
              fontFamily: fonts.display,
              fontWeight: 500,
              fontSize: t.layout.hero.font_size_px,
              lineHeight: t.layout.hero.line_height,
              letterSpacing: `${t.layout.hero.letter_spacing_em}em`,
              color: "#ffffff",
              maxWidth: "92%",
              opacity: headlineOp,
              textAlign: align === "center" ? "center" : "left",
            }}
          >
            {headline}
          </div>
        )}
        {subline && (
          <div
            style={{
              marginTop: 20,
              fontFamily: fonts.displayItalic,
              fontStyle: "italic",
              fontSize: 38,
              color: "rgba(255,255,255,0.85)",
              maxWidth: "88%",
              lineHeight: 1.35,
              opacity: sublineOp,
              textAlign: align === "center" ? "center" : "left",
            }}
          >
            {subline}
          </div>
        )}
      </div>
    </AbsoluteFill>
  );
};

export const PhotoBackgroundSchema = {
  photo_src: { type: "string", required: true },
  headline: { type: "string", required: false },
  eyebrow: { type: "string", required: false },
  subline: { type: "string", required: false },
  text_position: {
    type: "enum",
    values: ["center", "bottom-left", "bottom-center", "top-left"],
    required: false,
  },
  overlay_opacity: { type: "number", required: false },
  ken_burns: { type: "boolean", required: false },
} as const;
