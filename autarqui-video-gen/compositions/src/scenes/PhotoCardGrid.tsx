/**
 * PhotoCardGrid — 2-6 photos in grid with stagger reveal + optional captions.
 *
 * Use for: newsletter video (3-5 noticias), product collection, team grid.
 */

import * as React from "react";
import { AbsoluteFill, Img, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { fadeIn, sceneOpacity, defaultPacing } from "../lib/animations";
import type { LoadedFonts } from "../lib/fonts";

export interface PhotoCardGridProps {
  /** 2-6 items. Layout adapts: 2→1col, 3-4→2col, 5-6→2col 3rows */
  items: Array<{ photo_src: string; headline?: string; caption?: string }>;
  /** Optional eyebrow above the grid (e.g. "ESTA SEMANA EN AUTARQUI") */
  eyebrow?: string;
  /** Frames between each item's reveal */
  stagger_frames?: number;
  scene_duration_frames?: number;
  fonts: LoadedFonts;
}

export const PhotoCardGrid: React.FC<PhotoCardGridProps> = ({
  items,
  eyebrow,
  stagger_frames = 12,
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
  const cols = items.length === 2 ? 1 : 2;

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: "center",
        padding: "8% 6%",
        opacity: op,
      }}
    >
      {eyebrow && (
        <div
          style={{
            fontFamily: fonts.body,
            fontWeight: 500,
            fontSize: 24,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: t.colors.muted,
            marginBottom: 36,
            opacity: eyebrowOp,
            textAlign: "center",
          }}
        >
          {eyebrow}
        </div>
      )}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: `repeat(${cols}, 1fr)`,
          gap: 28,
          width: "100%",
          maxWidth: 1200,
        }}
      >
        {items.map((item, i) => {
          const itemOp = fadeIn(frame, Math.round(inFrames * 0.5) + i * stagger_frames, inFrames);
          return (
            <div key={i} style={{ opacity: itemOp }}>
              <div
                style={{
                  aspectRatio: "4/3",
                  width: "100%",
                  overflow: "hidden",
                  marginBottom: 14,
                  border: `1px solid ${t.colors.ruleSoft}`,
                }}
              >
                <Img
                  src={item.photo_src}
                  style={{ width: "100%", height: "100%", objectFit: "cover" }}
                />
              </div>
              {item.headline && (
                <div
                  style={{
                    fontFamily: fonts.display,
                    fontWeight: 500,
                    fontSize: 30,
                    color: t.colors.heading,
                    lineHeight: 1.2,
                    marginBottom: 6,
                    letterSpacing: "-0.012em",
                  }}
                >
                  {item.headline}
                </div>
              )}
              {item.caption && (
                <div
                  style={{
                    fontFamily: fonts.body,
                    fontWeight: 400,
                    fontSize: 18,
                    color: t.colors.muted,
                    lineHeight: 1.45,
                  }}
                >
                  {item.caption}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const PhotoCardGridSchema = {
  items: { type: "array", required: true, of: "object" },
  eyebrow: { type: "string", required: false },
  stagger_frames: { type: "number", required: false },
} as const;
