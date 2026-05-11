/**
 * LottiePlay — Render a Lottie JSON animation, frame-driven.
 *
 * Reads a Lottie JSON from public/ (downloaded via tools/assets/lottiefiles or
 * tools/motion/lottie-fetch.py). Drives playback via Remotion's frame so the
 * animation is deterministic.
 */

import * as React from "react";
import { AbsoluteFill, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { Player } from "@lottiefiles/react-lottie-player";
import { useStyleTokens } from "../lib/tokens";
import { sceneOpacity } from "../lib/animations";

export interface LottiePlayProps {
  /** Path to .json under public/ — e.g. "lottie/loader.json" */
  lottie_path: string;
  /** Force aspect ratio container. Default: 50% width centered, square */
  size_px?: number;
  /** If true, use scene's full duration; if false, play once at native speed */
  loop_to_scene?: boolean;
  scene_duration_frames?: number;
}

export const LottiePlay: React.FC<LottiePlayProps> = ({
  lottie_path,
  size_px = 600,
  loop_to_scene = true,
  scene_duration_frames,
}) => {
  const t = useStyleTokens();
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const total = scene_duration_frames ?? durationInFrames;
  const op = sceneOpacity(frame, 0, total, 12, 18);
  const playerRef = React.useRef<any>(null);

  // The Lottie Player runs on its own internal time; for deterministic rendering
  // we drive seek manually via frame.
  React.useEffect(() => {
    if (playerRef.current) {
      const totalLottieFrames = playerRef.current.totalFrames || 60;
      const targetFrame = loop_to_scene
        ? (frame / total) * totalLottieFrames
        : Math.min(frame, totalLottieFrames);
      playerRef.current.setSeeker?.(targetFrame, false);
    }
  }, [frame, loop_to_scene, total]);

  return (
    <AbsoluteFill
      style={{
        backgroundColor: t.colors.bg,
        justifyContent: "center",
        alignItems: "center",
        opacity: op,
      }}
    >
      <div style={{ width: size_px, height: size_px }}>
        <Player
          ref={playerRef}
          src={staticFile(lottie_path)}
          autoplay={false}
          loop={false}
          keepLastFrame
          style={{ width: "100%", height: "100%" }}
        />
      </div>
    </AbsoluteFill>
  );
};

export const LottiePlaySchema = {
  lottie_path: { type: "string", required: true },
  size_px: { type: "number", required: false },
  loop_to_scene: { type: "boolean", required: false },
} as const;
