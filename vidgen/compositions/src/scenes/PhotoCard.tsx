/**
 * PhotoCard — single photo with optional caption + eyebrow.
 *
 * Use for: foto-led IG, testimonial avatar, newsletter card.
 * Photo source: any URL (https://picsum.photos/... for placeholder, or staticFile()).
 */

import * as React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing, easings } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface PhotoCardProps {
  photo_src: string;
  /** Optional caption shown below the photo */
  caption?: string;
  /** Optional eyebrow above the photo */
  eyebrow?: string;
  /** Aspect of the photo container */
  photo_aspect?: "square" | "4:5" | "16:9" | "9:16";
  /** Apply slow Ken Burns zoom to photo */
  ken_burns?: boolean;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

const aspectMap: Record<string, [number, number]> = {
  "square": [1, 1],
  "4:5": [4, 5],
  "16:9": [16, 9],
  "9:16": [9, 16],
};

export const PhotoCard: React.FC<PhotoCardProps> = ({
  photo_src,
  caption,
  eyebrow,
  photo_aspect = "4:5",
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

  const eyebrowOp = fadeIn(frame, 0, inFrames * 0.7);
  const photoOp = fadeIn(frame, Math.round(inFrames * 0.4), inFrames);
  const captionOp = fadeIn(frame, Math.round(inFrames * 1.0), inFrames);

  const [arW, arH] = aspectMap[photo_aspect] || [1, 1];
  const photoH = 1100;
  const photoW = (photoH * arW) / arH;

  const kbScale = ken_burns
    ? interpolate(frame, [0, total], [1.04, 1.12], { extrapolateRight: "clamp" })
    : 1;

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
            letterSpacing: "0.18em",
            textTransform: "uppercase",
            color: t.colors.muted,
            marginBottom: 28,
            opacity: eyebrowOp,
          }}
        >
          {eyebrow}
        </div>
      )}
      <div
        style={{
          width: photoW,
          height: photoH,
          maxWidth: "92%",
          overflow: "hidden",
          opacity: photoOp,
        }}
      >
        <Img
          src={photo_src}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${kbScale})`,
            transformOrigin: "center center",
          }}
        />
      </div>
      {caption && (
        <div
          style={{
            marginTop: 36,
            fontFamily: fonts.displayItalic,
            fontStyle: "italic",
            fontWeight: 400,
            fontSize: 38,
            color: t.colors.muted,
            textAlign: "center",
            maxWidth: "84%",
            lineHeight: 1.4,
            opacity: captionOp,
          }}
        >
          {caption}
        </div>
      )}
    </AbsoluteFill>
  );
};

export const PhotoCardSchema = {
  photo_src: { type: "string", required: true },
  caption: { type: "string", required: false },
  eyebrow: { type: "string", required: false },
  photo_aspect: { type: "enum", values: ["square", "4:5", "16:9", "9:16"], required: false },
  ken_burns: { type: "boolean", required: false },
} as const;
