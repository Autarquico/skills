/**
 * PhotoSlideshow — sequence of photos with Ken Burns + crossfade.
 *
 * Use for: newsletter video, trailer, foto-led narrative.
 */

import * as React from "react";
import { AbsoluteFill, Img, interpolate, useCurrentFrame, useVideoConfig } from "remotion";
import { useStyleTokens } from "../lib/tokens";
import { sceneOpacity, defaultPacing } from "../lib/animations";

export interface PhotoSlideshowProps {
  photos: Array<{ src: string; caption?: string }>;
  /** How long each photo holds (seconds), excluding crossfade */
  hold_per_photo_s?: number;
  /** Crossfade duration (seconds) */
  crossfade_s?: number;
  /** Ken Burns direction per photo: alternates if "auto" */
  ken_burns?: "auto" | "in" | "out" | "none";
  scene_duration_frames?: number;
}

export const PhotoSlideshow: React.FC<PhotoSlideshowProps> = ({
  photos,
  hold_per_photo_s = 3,
  crossfade_s = 0.6,
  ken_burns = "auto",
  scene_duration_frames,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const { inFrames, outFrames } = defaultPacing(t, fps);
  const op = sceneOpacity(frame, 0, total, inFrames, outFrames);

  const holdF = Math.round(hold_per_photo_s * fps);
  const crossF = Math.round(crossfade_s * fps);
  const stepF = holdF + crossF;

  return (
    <AbsoluteFill style={{ backgroundColor: t.colors.bg, opacity: op }}>
      {photos.map((p, i) => {
        const start = i * stepF;
        const end = start + stepF;
        // Crossfade: ramp up over crossF, hold, ramp down on next photo's start
        const localOp = (() => {
          if (frame < start - crossF) return 0;
          if (frame > end) return 0;
          if (frame < start) {
            // fading in over crossF
            return interpolate(frame, [start - crossF, start], [0, 1]);
          }
          if (frame > start + holdF) {
            // fading out over crossF
            return interpolate(frame, [start + holdF, end], [1, 0]);
          }
          return 1;
        })();

        if (localOp === 0) return null;

        // Ken Burns
        let kbScale = 1;
        if (ken_burns !== "none") {
          const dir =
            ken_burns === "auto" ? (i % 2 === 0 ? "in" : "out") : ken_burns;
          if (dir === "in") {
            kbScale = interpolate(frame, [start, end], [1.04, 1.18], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          } else {
            kbScale = interpolate(frame, [start, end], [1.18, 1.04], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
          }
        }

        return (
          <AbsoluteFill key={i} style={{ opacity: localOp }}>
            <Img
              src={p.src}
              style={{
                position: "absolute",
                inset: 0,
                width: "100%",
                height: "100%",
                objectFit: "cover",
                transform: `scale(${kbScale})`,
              }}
            />
            {p.caption && (
              <div
                style={{
                  position: "absolute",
                  bottom: 60,
                  left: 0,
                  right: 0,
                  textAlign: "center",
                  fontFamily: "Georgia, serif",
                  fontStyle: "italic",
                  fontSize: 32,
                  color: "#ffffff",
                  textShadow: "0 2px 8px rgba(0,0,0,0.6)",
                  padding: "0 8%",
                }}
              >
                {p.caption}
              </div>
            )}
          </AbsoluteFill>
        );
      })}
    </AbsoluteFill>
  );
};

export const PhotoSlideshowSchema = {
  photos: { type: "array", required: true, of: "object" },
  hold_per_photo_s: { type: "number", required: false },
  crossfade_s: { type: "number", required: false },
  ken_burns: { type: "enum", values: ["auto", "in", "out", "none"], required: false },
} as const;
